#!/usr/bin/env python3
"""快手视频解析 - 输入分享链接，输出 {title, topic, videoId, url}"""

import re
import json
import sys
import argparse
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Referer": "https://v.kuaishou.com/",
}

INIT_STATE_REGEX = re.compile(r"window\.INIT_STATE\s*=\s*(\{.*?\})\s*<\/script>", re.DOTALL)


def resolve_url(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=20)
    return resp.url


def get_text(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def extract_hashtags(text: str) -> str:
    tags = re.findall(r"#\S+", text)
    return " ".join(tags)


def clean_title(text: str, tags: str) -> str:
    for t in tags.split():
        text = text.replace(t, "")
    return text.strip()


def extract_video_id(url: str) -> str:
    m = re.search(r"/fw/(?:photo|long-video)/([A-Za-z0-9]+)", url)
    return m.group(1) if m else ""


def extract(url: str) -> dict:
    # 1. 短链跳转
    real_url = resolve_url(url)
    if not real_url:
        raise ValueError("短链解析失败")
    real_url = real_url.replace("/fw/long-video/", "/fw/photo/")

    # 2. 抓取页面
    html = get_text(real_url)

    # 3. 解析 INIT_STATE
    m = INIT_STATE_REGEX.search(html)
    if not m:
        raise ValueError("未找到 INIT_STATE JSON 数据")
    init_state = json.loads(m.group(1))

    # 查找 photo 对象
    if "photo" in init_state and isinstance(init_state["photo"], dict):
        photo = init_state["photo"]
    else:
        photo = None
        for v in init_state.values():
            if isinstance(v, dict) and "photo" in v and isinstance(v["photo"], dict):
                photo = v["photo"]
                break
        if not photo:
            raise ValueError("INIT_STATE 中未找到 photo 信息")

    # 4. 提取信息
    caption = photo.get("caption") or ""
    topic = extract_hashtags(caption)
    title = clean_title(caption, topic)
    video_id = extract_video_id(real_url)

    video_url = ""
    for entry in photo.get("mainMvUrls") or []:
        if entry.get("url"):
            video_url = entry["url"]
            break
    if not video_url and photo.get("videoUrl"):
        video_url = photo["videoUrl"]
    if not video_url:
        raise ValueError("未找到视频直链")

    return {
        "title": title,
        "topic": topic,
        "videoId": video_id,
        "url": video_url,
        "platform": "kuaishou",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="快手分享链接")
    args = parser.parse_args()

    try:
        result = extract(args.url)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)
