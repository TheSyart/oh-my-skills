#!/usr/bin/env python3
"""Parse short-video share links through vendored extra-link parsers.

Output schema:
{
  "title": "...",
  "topic": "...",
  "videoId": "...",
  "url": "direct video URL",
  "rawUrl": "original URL or share text",
  "resource": "douyin|kuaishou|xhs|bilibili"
}
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


SCRIPT_DIR = Path(__file__).resolve().parent
VENDOR_DIR = SCRIPT_DIR / "vendor" / "extra_link"
sys.path.insert(0, str(VENDOR_DIR))


def extract_url(text: str) -> str:
    match = re.search(r"https?://[^\s]+", text)
    return match.group(0) if match else ""


def detect_platform(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "douyin.com" in host or "iesdouyin.com" in host:
        return "douyin"
    if "bilibili.com" in host or "b23.tv" in host:
        return "bilibili"
    if "kuaishou.com" in host or "v.kuaishou.com" in host or "chenzhongtech.com" in host:
        return "kuaishou"
    if "xiaohongshu.com" in host or "xhslink.com" in host:
        return "xhs"
    return ""


def normalize_result(result: Any, fallback_raw_url: str = "", fallback_resource: str = "") -> dict[str, Any]:
    if is_dataclass(result):
        data = asdict(result)
    elif isinstance(result, dict):
        data = dict(result)
    else:
        data = {
            key: getattr(result, key, "")
            for key in ("title", "topic", "videoId", "url", "rawUrl", "resource")
            if hasattr(result, key)
        }

    aliases = {
        "source": "resource",
        "platform": "resource",
        "video_id": "videoId",
        "video_url": "url",
        "directUrl": "url",
    }
    for old, new in aliases.items():
        if old in data and new not in data:
            data[new] = data[old]

    normalized = {
        "title": str(data.get("title") or ""),
        "topic": str(data.get("topic") or ""),
        "videoId": data.get("videoId") if data.get("videoId") is not None else "",
        "url": str(data.get("url") or ""),
        "rawUrl": str(data.get("rawUrl") or fallback_raw_url),
        "resource": str(data.get("resource") or fallback_resource),
    }
    if not normalized["url"]:
        raise ValueError("parser returned no direct video URL")
    if not normalized["resource"]:
        normalized["resource"] = detect_platform(normalized["rawUrl"])
    return normalized


def parse_input(input_text: str, p: int = 1) -> dict[str, Any]:
    url = extract_url(input_text)
    if not url:
        raise ValueError("未检测到链接")

    platform = detect_platform(url)
    if not platform:
        raise ValueError("不支持的链接来源，目前支持抖音、快手、小红书、B站")

    if platform == "douyin":
        from pharse.douyin import DouyinProcessor

        result = DouyinProcessor(api_key="").parse_share_url_result(input_text)
    elif platform == "kuaishou":
        from pharse.kuaishou import extract

        result = extract(url)
    elif platform == "xhs":
        from pharse.xhs import XHSExtractor

        result = XHSExtractor().extract(url)
    elif platform == "bilibili":
        from pharse.bilibili import extract

        result = asyncio.run(extract(url=url, p=p))
    else:
        raise ValueError(f"unsupported platform: {platform}")

    return normalize_result(result, fallback_raw_url=url, fallback_resource=platform)


def read_input(args: argparse.Namespace) -> str:
    if args.input_file:
        return Path(args.input_file).read_text(encoding="utf-8")
    if args.input:
        return args.input
    raise ValueError("must pass --input or --input-file")


def write_json(payload: dict[str, Any], out: str | None, pretty: bool) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2 if pretty else None)
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse a short-video share link.")
    parser.add_argument("--input", help="Share text or direct URL")
    parser.add_argument("--input-file", help="Path containing share text or URL")
    parser.add_argument("--from-json", help="Normalize an existing parser JSON result without network access")
    parser.add_argument("--out", help="Write JSON output to this file")
    parser.add_argument("--p", type=int, default=1, help="Bilibili page index")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    try:
        if args.from_json:
            raw = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
            result = normalize_result(raw)
        else:
            result = parse_input(read_input(args), p=args.p)
        write_json(result, args.out, args.pretty)
    except Exception as exc:
        error = {"error": str(exc)}
        print(json.dumps(error, ensure_ascii=False), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
