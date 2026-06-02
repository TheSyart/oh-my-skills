#!/usr/bin/env python3
"""小红书视频解析 - 输入分享链接，输出 {title, topic, videoId, url}"""

import re
import json
import sys
import argparse
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
}

INITIAL_STATE_REGEX = re.compile(r"window\.__INITIAL_STATE__\s*=\s*(\{.*?\})\s*;?\s*<\/script>", re.DOTALL)
NOTE_ID_REGEX = re.compile(r"/explore/([^?]+)")


def resolve_url(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=20)
    return resp.url


def get_text(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def extract(url: str) -> dict:
    # 1. 处理短链或提取noteId
    if NOTE_ID_REGEX.search(url):
        final_url = url
    else:
        final_url = resolve_url(url)

    # 2. 抓取页面
    html = get_text(final_url)

    # 3. 解析 INITIAL_STATE
    m = INITIAL_STATE_REGEX.search(html)
    if not m:
        raise ValueError("未找到 __INITIAL_STATE__ JSON 数据")
    block = m.group(1)
    fixed = re.sub(r'\bundefined\b', 'null', block)
    data = json.loads(fixed)
    note_obj = data["noteData"]["data"]["noteData"]

    # 4. 提取信息
    title = (note_obj.get("title") or "").strip()
    topic = (note_obj.get("desc") or "").replace("[话题]#", "").strip()

    video_id = note_obj["video"]["media"]["videoId"]
    stream_obj = note_obj["video"]["media"]["stream"]

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

    return {
        "title": title,
        "topic": topic,
        "videoId": video_id,
        "url": final_url_val,
        "platform": "xhs",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="小红书分享链接")
    args = parser.parse_args()

    try:
        result = extract(args.url)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)
