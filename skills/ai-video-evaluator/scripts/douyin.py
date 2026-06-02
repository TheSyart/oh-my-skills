#!/usr/bin/env python3
"""抖音视频解析 - 输入分享链接，输出 {title, topic, videoId, url}"""

import re
import json
import sys
import argparse
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
}


def resolve_url(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=20)
    return resp.url


def get_text(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def extract(text: str) -> dict:
    # 1. 提取URL
    urls = re.findall(r"https?://[^\s]+", text)
    if not urls:
        raise ValueError("未找到有效的分享链接")

    share_url = urls[0]
    final_url = resolve_url(share_url)
    video_id = final_url.split("?")[0].strip("/").split("/")[-1]
    share_url = f"https://www.iesdouyin.com/share/video/{video_id}"

    # 2. 获取页面
    page_html = get_text(share_url)

    # 3. 解析 _ROUTER_DATA
    pattern = re.compile(r"window\._ROUTER_DATA\s*=\s*(.*?)</script>", re.DOTALL)
    find_res = pattern.search(page_html)
    if not find_res:
        raise ValueError("从HTML中解析视频信息失败")

    json_data = json.loads(find_res.group(1).strip())
    VIDEO_KEY = "video_(id)/page"
    NOTE_KEY = "note_(id)/page"

    if VIDEO_KEY in json_data["loaderData"]:
        info = json_data["loaderData"][VIDEO_KEY]["videoInfoRes"]
    elif NOTE_KEY in json_data["loaderData"]:
        info = json_data["loaderData"][NOTE_KEY]["videoInfoRes"]
    else:
        raise ValueError("无法解析视频或图集信息")

    data = info["item_list"][0]

    # 4. 提取信息
    video_url = data["video"]["play_addr"]["url_list"][0].replace("playwm", "play")
    desc = data.get("desc", "").strip() or f"douyin_{video_id}"
    desc = re.sub(r'[\\/:*?"<>|]', "_", desc)

    topics = []
    for extra in data.get("text_extra", []):
        if extra.get("type") == 1:
            name = extra.get("hashtag_name")
            if name:
                topics.append(name)
    topic_str = "#" + " #".join(topics)

    title = desc.replace(topic_str, "").strip()

    # 5. 增强URL（跟随跳转获取最终直链）
    try:
        final_video_url = resolve_url(video_url)
    except Exception:
        final_video_url = video_url

    return {
        "title": title,
        "topic": topic_str,
        "videoId": video_id,
        "url": final_video_url,
        "platform": "douyin"
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="抖音分享链接")
    args = parser.parse_args()

    try:
        result = extract(args.url)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)
