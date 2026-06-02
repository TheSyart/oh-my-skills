#!/usr/bin/env python3
"""B站视频解析 - 输入分享链接或BV号，输出 {title, topic, videoId, url}"""

import re
import json
import sys
import argparse
import random
from urllib.parse import urlparse, urlunparse
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Accept": "application/json",
}

BILI_CDNS = [
    "upos-sz-mirrorcos.bilivideo.com",
    "upos-sz-mirrorali.bilivideo.com",
    "upos-sz-mirror08c.bilivideo.com",
]


def get_json(url: str, params: dict = None) -> dict:
    resp = requests.get(url, headers=HEADERS, params=params or {}, timeout=20)
    resp.raise_for_status()
    return resp.json()


def extract_bv(url: str) -> str:
    m = re.search(r'BV[0-9A-Za-z]+', url)
    if m:
        return m.group(0)
    # 短链跳转
    resp = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=20)
    real = str(resp.url)
    m2 = re.search(r'BV[0-9A-Za-z]+', real)
    if m2:
        return m2.group(0)
    raise ValueError("无法从链接提取BV号")


def change_cdn(url: str) -> str:
    parsed = urlparse(url)
    new_netloc = random.choice(BILI_CDNS)
    return urlunparse(parsed._replace(netloc=new_netloc))


def extract(url: str, p: int = 1) -> dict:
    # 1. 提取BV
    bv = extract_bv(url)

    # 2. 获取视频详情
    details = get_json("https://api.bilibili.com/x/web-interface/view", {"bvid": bv})
    if details.get("code") != 0 or "data" not in details:
        raise ValueError("获取视频详情失败")
    info = details["data"]
    title = info.get("title", "")
    topic = info.get("desc", "")

    # 3. 获取cid
    pagelist = get_json("https://api.bilibili.com/x/player/pagelist", {"bvid": bv})
    p_idx = max(0, min(p - 1, len(pagelist["data"]) - 1))
    cid = pagelist["data"][p_idx]["cid"]

    # 4. 获取直链
    playurl = get_json(
        "https://api.bilibili.com/x/player/playurl",
        {
            "bvid": bv,
            "cid": cid,
            "qn": 120,
            "otype": "json",
            "platform": "html5",
            "high_quality": 1,
            "fnval": 129,
            "fourk": 1,
        },
    )
    if playurl.get("code") != 0 or "data" not in playurl:
        raise ValueError("获取视频直链失败")
    video_url = playurl["data"]["durl"][0]["url"]
    video_url = change_cdn(video_url)

    return {
        "title": title,
        "topic": topic,
        "videoId": bv,
        "url": video_url,
        "platform": "bilibili",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="B站链接或BV号")
    parser.add_argument("--p", type=int, default=1, help="分P序号")
    args = parser.parse_args()

    try:
        result = extract(args.url, p=args.p)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)
