#!/usr/bin/env python3
"""
小红书视频解析器

功能：
- 解析短链并获取最终页面地址
- 抓取页面并解析 window.__INITIAL_STATE__ JSON
- 提取标题与话题（移除 [话题]# 标记）
- 从 stream 中选择首个可用 masterUrl 作为视频直链
- 输出统一数据模型（title、topic、videoId、url）
"""
from __future__ import annotations

import argparse
import json
import re
from typing import Optional, Dict, Any
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models import VideoResult

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.0 Mobile/15E148 Safari/604.1"
    )
}


class XHSExtractResult:
    title: str
    topic: str
    videoId: Any
    url: str


class XHSExtractor:
    """
    小红书视频直链解析核心类
    """

    INITIAL_STATE_REGEX = re.compile(
        r"window\.__INITIAL_STATE__\s*=\s*(\{.*?\})\s*;?\s*<\/script>",
        re.DOTALL,
    )
    NOTE_ID_REGEX = re.compile(r"/(?:explore|discovery/item)/([^?]+)")

    def extract_note_id(self, url: str) -> str:
        """
        从 explore 或 discovery/item 页面链接提取笔记 ID
        """
        match = self.NOTE_ID_REGEX.search(url)
        if not match:
            raise ValueError(f"无法从链接提取作品ID: {url}")
        return match.group(1)

    def resolve_final_url(self, url: str) -> str:
        """
        解析短链并返回最终可访问链接
        """
        import request as req
        return req.resolve_url(url, headers=HEADERS)

    def fetch_html(self, url: str) -> str:
        """
        获取页面 HTML 文本（模拟移动端 UA）
        """
        import request as req
        return req.get_text(url, headers=HEADERS)

    def parse_initial_state(self, html: str) -> Dict[str, Any]:
        """
        从 HTML 中提取并解析 window.__INITIAL_STATE__ 的 JSON
        兼容 JS 对象中的 undefined，转换为合法 JSON 后再解析
        """
        m = self.INITIAL_STATE_REGEX.search(html)
        if not m:
            raise ValueError("未找到 __INITIAL_STATE__ JSON 数据")
        block = m.group(1)

        # 1. JS -> JSON 兼容处理
        fixed = re.sub(r'\bundefined\b', 'null', block)


        try:
             # 2. 转 dict
            data = json.loads(fixed)

            # 3. 处理嵌套 JSON 字符串
            launch_cfg = data["noteData"]["data"]["noteData"]
            return launch_cfg
        except json.JSONDecodeError as exc:
            raise ValueError(f"__INITIAL_STATE__ JSON 解析失败: {exc}") from exc

    def extract_note_object(self, initial_state: Dict[str, Any], note_id: str) -> Dict[str, Any]:
        return initial_state

    def extract(self, url: str) -> XHSExtractResult:
        """
        执行完整解析流程并返回统一数据模型
        """
        final_url = url if self.NOTE_ID_REGEX.search(url) else self.resolve_final_url(url)
        html = self.fetch_html(final_url)
        initial_state = self.parse_initial_state(html)
        note_obj = self.extract_note_object(initial_state, "")
        title = (note_obj.get("title") or "").strip()
        topic = (note_obj.get("desc") or "").replace("[话题]#", "").strip()
        try:
            media_obj = note_obj["video"]["media"]
            video_id_value = media_obj.get("videoId")
            if video_id_value is None:
                video_id_value = media_obj.get("video", {}).get("videoId")
            if video_id_value is None:
                raise KeyError("videoId")
        except KeyError as exc:
            raise KeyError("未找到 video.media.videoId 或 video.media.video.videoId") from exc
        try:
            stream_obj = media_obj["stream"]
        except KeyError as exc:
            raise KeyError("未找到 video.media.stream") from exc

        # 遍历 stream 字典，找到首个有效的 masterUrl
        final_url_val = ""
        for key in stream_obj:
            stream_list = stream_obj[key]
            if not stream_list:
                continue
            for item in stream_list:
                if item.get("masterUrl"):
                    final_url_val = item["masterUrl"]
                    break
            if final_url_val:
                break

        if not final_url_val:
             raise ValueError("未在 stream 中找到有效的 masterUrl")

        return VideoResult(
            title=title,
            topic=topic,
            videoId=video_id_value,
            url=final_url_val,
            rawUrl=url,
            resource="xhs"
        )

def main() -> None:
    """
    命令行接口：
    - 输入：--url 小红书笔记页面链接或短链
    - 输出：包含 title、topic、videoId、url 的 JSON
    """
    parser = argparse.ArgumentParser(description="小红书视频直链解析器")
    parser.add_argument("--url", required=True, help="小红书笔记页面链接或短链")
    args = parser.parse_args()

    extractor = XHSExtractor()
    try:
        result = extractor.extract(args.url)
        print(
            json.dumps(
                {
                    "title": result.title,
                    "topic": result.topic,
                    "videoId": result.videoId,
                    "url": result.url,
                },
                ensure_ascii=False,
            )
        )
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
