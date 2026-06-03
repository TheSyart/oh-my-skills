#!/usr/bin/env python3
"""
抖音视频解析器与工具集

功能：
- 解析抖音分享链接，获取无水印视频直链
- 组装统一数据模型（title、topic、videoId、url）
- 保留下载、音频提取与文本识别工具函数（按需使用）
"""

import os
import re
import json
import requests
import tempfile
import asyncio
from pathlib import Path
from typing import Optional, Tuple
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models import VideoResult
import request as req
try:
    import ffmpeg
except Exception:
    ffmpeg = None
try:
    from tqdm.asyncio import tqdm
except Exception:
    tqdm = None
from urllib import request
from http import HTTPStatus
try:
    import dashscope
except Exception:
    dashscope = None
try:
    from mcp.server.fastmcp import FastMCP
    from mcp.server.fastmcp import Context
    mcp = FastMCP("Douyin MCP Server", dependencies=["requests", "ffmpeg-python", "tqdm", "dashscope"])
    def _tool(): return mcp.tool()
    def _resource(x): return mcp.resource(x)
    def _prompt(): return mcp.prompt()
except Exception:
    mcp = None
    class Context: pass
    def _tool():
        def decorator(fn): return fn
        return decorator
    def _resource(x):
        def decorator(fn): return fn
        return decorator
    def _prompt():
        def decorator(fn): return fn
        return decorator

# 请求头，模拟移动端访问
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/121.0.2277.107 Version/17.0 Mobile/15E148 Safari/604.1'
}

# 默认 API 配置
DEFAULT_MODEL = "paraformer-v2"


class DouyinProcessor:
    """抖音视频处理器"""

    def __init__(self, api_key: str, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model or DEFAULT_MODEL
        self.temp_dir = Path(tempfile.mkdtemp())
        if dashscope and api_key:
            dashscope.api_key = api_key

    def __del__(self):
        """清理临时目录"""
        import shutil
        if hasattr(self, 'temp_dir') and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def parse_share_url(self, share_text: str) -> dict:
        """从分享文本中提取无水印视频链接"""
        # 提取分享链接
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', share_text)
        if not urls:
            raise ValueError("未找到有效的分享链接")

        share_url = urls[0]
        final_url = req.resolve_url(share_url, headers=HEADERS)
        video_id = final_url.split("?")[0].strip("/").split("/")[-1]
        share_url = f'https://www.iesdouyin.com/share/video/{video_id}'

        # 获取视频页面内容
        page_html = req.get_text(share_url, headers=HEADERS)

        pattern = re.compile(
            pattern=r"window\._ROUTER_DATA\s*=\s*(.*?)</script>",
            flags=re.DOTALL,
        )
        find_res = pattern.search(page_html)

        if not find_res or not find_res.group(1):
            raise ValueError("从HTML中解析视频信息失败")

        # 解析JSON数据
        json_data = json.loads(find_res.group(1).strip())
        VIDEO_ID_PAGE_KEY = "video_(id)/page"
        NOTE_ID_PAGE_KEY = "note_(id)/page"

        if VIDEO_ID_PAGE_KEY in json_data["loaderData"]:
            original_video_info = json_data["loaderData"][VIDEO_ID_PAGE_KEY]["videoInfoRes"]
        elif NOTE_ID_PAGE_KEY in json_data["loaderData"]:
            original_video_info = json_data["loaderData"][NOTE_ID_PAGE_KEY]["videoInfoRes"]
        else:
            raise Exception("无法从JSON中解析视频或图集信息")

        data = original_video_info["item_list"][0]

        # 获取视频信息
        video_url = data["video"]["play_addr"]["url_list"][0].replace("playwm", "play")
        desc = data.get("desc", "").strip() or f"douyin_{video_id}"

        # 替换文件名中的非法字符
        desc = re.sub(r'[\\/:*?"<>|]', '_', desc)

        # 提取话题
        topics = []
        if "text_extra" in data:
            for extra in data["text_extra"]:
                if extra.get("type") == 1:  # 1 usually represents hashtag/topic
                    hashtag_name = extra.get("hashtag_name")
                    if hashtag_name:
                        topics.append(hashtag_name)

        topic_str = "#" + " #".join(topics)

        return {
            "url": video_url,
            "title": desc.replace(topic_str, "").strip(),
            "topic": topic_str,
            "videoId": video_id
        }

    def parse_share_url_result(self, share_text: str) -> VideoResult:
        """返回统一数据模型 VideoResult"""
        data = self.parse_share_url(share_text)
        return VideoResult(title=data["title"], topic=data["topic"], videoId=data["videoId"], url=data["url"], rawUrl=share_text, resource="douyin")

    async def download_video(self, video_info: dict, ctx: Context) -> Path:
        """异步下载视频到临时目录"""
        filename = f"{video_info['video_id']}.mp4"
        filepath = self.temp_dir / filename

        ctx.info(f"正在下载视频: {video_info['title']}")

        response = requests.get(video_info['url'], headers=HEADERS, stream=True)
        response.raise_for_status()

        # 获取文件大小
        total_size = int(response.headers.get('content-length', 0))

        # 异步下载文件，显示进度
        with open(filepath, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = downloaded / total_size
                        await ctx.report_progress(downloaded, total_size)

        ctx.info(f"视频下载完成: {filepath}")
        return filepath

    def extract_audio(self, video_path: Path) -> Path:
        """从视频文件中提取音频"""
        audio_path = video_path.with_suffix('.mp3')

        try:
            (
                ffmpeg
                .input(str(video_path))
                .output(str(audio_path), acodec='libmp3lame', q=0)
                .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
            )
            return audio_path
        except Exception as e:
            raise Exception(f"提取音频时出错: {str(e)}")

    def extract_text_from_video_url(self, video_url: str) -> str:
        """从视频URL中提取文字（使用阿里云百炼API）"""
        try:
            # 发起异步转录任务
            task_response = dashscope.audio.asr.Transcription.async_call(
                model=self.model,
                file_urls=[video_url],
                language_hints=['zh', 'en']
            )

            # 等待转录完成
            transcription_response = dashscope.audio.asr.Transcription.wait(
                task=task_response.output.task_id
            )

            if transcription_response.status_code == HTTPStatus.OK:
                # 获取转录结果
                for transcription in transcription_response.output['results']:
                    url = transcription['transcription_url']
                    result = json.loads(request.urlopen(url).read().decode('utf8'))

                    # 保存结果到临时文件
                    temp_json_path = self.temp_dir / 'transcription.json'
                    with open(temp_json_path, 'w') as f:
                        json.dump(result, f, indent=4, ensure_ascii=False)

                    # 提取文本内容
                    if 'transcripts' in result and len(result['transcripts']) > 0:
                        return result['transcripts'][0]['text']
                    else:
                        return "未识别到文本内容"

            else:
                raise Exception(f"转录失败: {transcription_response.output.message}")

        except Exception as e:
            raise Exception(f"提取文字时出错: {str(e)}")

    def cleanup_files(self, *file_paths: Path):
        """清理指定的文件"""
        for file_path in file_paths:
            if file_path.exists():
                file_path.unlink()


@_tool()
def get_douyin_download_link(share_link: str) -> str:
    """
    获取抖音视频的无水印下载链接

    参数:
    - share_link: 抖音分享链接或包含链接的文本

    返回:
    - 包含下载链接和视频信息的JSON字符串
    """
    try:
        processor = DouyinProcessor("")  # 获取下载链接不需要API密钥
        video_info = processor.parse_share_url(share_link)

        return json.dumps({
            "status": "success",
            "video_id": video_info["video_id"],
            "title": video_info["title"],
            "download_url": video_info["url"],
            "description": f"视频标题: {video_info['title']}",
            "usage_tip": "可以直接使用此链接下载无水印视频"
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"获取下载链接失败: {str(e)}"
        }, ensure_ascii=False, indent=2)


def _unused():
    return None


@_tool()
def parse_douyin_video_info(share_link: str) -> str:
    """
    解析抖音分享链接，获取视频基本信息

    参数:
    - share_link: 抖音分享链接或包含链接的文本

    返回:
    - 视频信息（JSON格式字符串）
    """
    try:
        processor = DouyinProcessor("")  # 不需要API密钥来解析链接
        video_info = processor.parse_share_url(share_link)

        return json.dumps({
            "video_id": video_info["video_id"],
            "title": video_info["title"],
            "download_url": video_info["url"],
            "status": "success"
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        }, ensure_ascii=False, indent=2)


@_resource("douyin://video/{video_id}")
def get_video_info(video_id: str) -> str:
    """
    获取指定视频ID的详细信息

    参数:
    - video_id: 抖音视频ID

    返回:
    - 视频详细信息
    """
    share_url = f"https://www.iesdouyin.com/share/video/{video_id}"
    try:
        processor = DouyinProcessor("")
        video_info = processor.parse_share_url(share_url)
        return json.dumps(video_info, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取视频信息失败: {str(e)}"


def guide_unused() -> str:
    return ""


def _cli_main():
    import argparse
    parser = argparse.ArgumentParser(description="Douyin video link extractor")
    parser.add_argument("--url", required=True, help="Douyin share URL")
    args = parser.parse_args()

    try:
        processor = DouyinProcessor("")
        info = processor.parse_share_url_result(args.url)
        print(json.dumps(
            {
                "title": info.title,
                "topic": info.topic,
                "videoId": info.videoId,
                "url": info.url
            },
            ensure_ascii=False
        ))
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))

if __name__ == "__main__":
    _cli_main()
