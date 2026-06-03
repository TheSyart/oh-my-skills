#!/usr/bin/env python3
"""
快手视频解析器

功能：
- 解析短链 v.kuaishou.com 并获取真实地址
- 兼容 chenzhongtech fw/photo 页面解析（统一 long-video -> photo）
- 抓取页面并解析 window.INIT_STATE JSON
- 提取标题与话题标签（以空格分隔），生成视频直链
- 输出统一数据模型（title、topic、videoId、url）
"""
import argparse
import json
import re
from typing import Dict, Any, Optional
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models import VideoResult
import request as req

# 请求头（模拟 iOS Safari）
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.0 Mobile/15E148 Safari/604.1"
    ),
    "Referer": "https://v.kuaishou.com/",
}

# 匹配 window.INIT_STATE 的脚本块
INIT_STATE_REGEX = re.compile(r"window\.INIT_STATE\s*=\s*(\{.*?\})\s*</script>", re.DOTALL)


def extract_hashtags(text: str) -> str:
    """
    从标题中提取以 # 开头的标签，组装为以空格分隔的字符串
    """
    if not text:
        return ""
    tags = re.findall(r"#\S+", text)
    return " ".join(tags)


def clean_title(text: str, tags: str) -> str:
    """
    将标题中的话题标签移除，并清理首尾空格
    """
    if not text:
        return ""
    if tags:
        for t in tags.split():
            text = text.replace(t, "")
    return text.strip()


def extract_video_id_from_url(url: str) -> str:
    """
    从快手真实地址中提取视频ID（fw/photo/<id> 或 fw/long-video/<id>）
    """
    m = re.search(r"/fw/(?:photo|long-video)/([A-Za-z0-9]+)", url)
    return m.group(1) if m else ""


def pick_first_main_mv_url(photo: Dict[str, Any]) -> Optional[str]:
    """
    选择 mainMvUrls 列表中第一个包含 url 的条目
    """
    mv_urls = photo.get("mainMvUrls") or []
    for entry in mv_urls:
        url = entry.get("url")
        if url:
            return url
    # 兼容字段 videoUrl
    if photo.get("videoUrl"):
        return photo["videoUrl"]
    return None


def parse_init_state(html: str) -> Dict[str, Any]:
    """
    解析页面中的 window.INIT_STATE JSON
    """
    m = INIT_STATE_REGEX.search(html)
    if not m:
        raise ValueError("未找到 INIT_STATE JSON 数据")
    block = m.group(1)
    return json.loads(block)


def locate_photo(init_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    在 INIT_STATE 中定位 photo 对象
    """
    # 可能存在顶层包含 photo 的结构
    if "photo" in init_state and isinstance(init_state["photo"], dict):
        return init_state["photo"]
    # 遍历 values 查找包含 photo 的条目
    for v in init_state.values():
        if isinstance(v, dict) and "photo" in v and isinstance(v["photo"], dict):
            return v["photo"]
    raise ValueError("INIT_STATE 中未找到 photo 信息")


def extract(url: str) -> VideoResult:
    """
    主解析流程：
    - 解析短链跳转
    - 统一将 long-video 替换成 photo
    - 抓取页面并解析 INIT_STATE
    - 提取标题、话题、videoId、视频直链
    """
    real_url = req.resolve_url(url, headers=HEADERS)
    if not real_url:
        raise ValueError("短链解析失败")
    real_url = real_url.replace("/fw/long-video/", "/fw/photo/")

    html = req.get_text(real_url, headers=HEADERS)
    init_state = parse_init_state(html)
    photo = locate_photo(init_state)

    caption = photo.get("caption") or ""
    topic = extract_hashtags(caption)
    title = clean_title(caption, topic)
    video_id = extract_video_id_from_url(real_url)

    video_url = pick_first_main_mv_url(photo)
    if not video_url:
        raise ValueError("未找到视频直链")

    return VideoResult(
        title=title,
        topic=topic,
        videoId=video_id,
        url=video_url,
        rawUrl=url,
        resource="kuaishou"
    )

def main() -> None:
    """
    命令行入口：
    - 输入：--url <快手短链或页面地址>
    - 输出：统一 JSON（title、topic、videoId、url）
    """
    parser = argparse.ArgumentParser(description="Kuaishou video link extractor")
    parser.add_argument("--url", required=True, help="Kuaishou short link or page url")
    args = parser.parse_args()

    try:
        result = extract(args.url)
        print(json.dumps({"title": result.title, "topic": result.topic, "videoId": result.videoId, "url": result.url}, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
