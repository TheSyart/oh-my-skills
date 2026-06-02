#!/usr/bin/env python3
"""统一入口：自动检测平台并解析视频链接"""

import json
import sys
import re
import subprocess
import argparse
from urllib.parse import urlparse


def detect_platform(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "douyin.com" in host or "iesdouyin.com" in host:
        return "douyin"
    if "bilibili.com" in host or "b23.tv" in host:
        return "bilibili"
    if "kuaishou.com" in host or "chenzhongtech.com" in host:
        return "kuaishou"
    if "xiaohongshu.com" in host or "xhslink.com" in host:
        return "xhs"
    return ""


def extract_url(text: str) -> str:
    m = re.search(r"https?://[^\s]+", text)
    return m.group(0) if m else ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="视频分享链接")
    parser.add_argument("--script-dir", default=None, help="脚本目录路径")
    args = parser.parse_args()

    # 提取URL
    url = extract_url(args.url)
    if not url:
        print(json.dumps({"error": "未找到有效的URL"}, ensure_ascii=False))
        sys.exit(1)

    # 检测平台
    platform = detect_platform(url)
    if not platform:
        print(json.dumps({"error": "不支持的平台，目前支持抖音、快手、小红书、B站"}, ensure_ascii=False))
        sys.exit(1)

    # 确定脚本目录
    if args.script_dir:
        script_dir = args.script_dir
    else:
        script_dir = __file__.rsplit("/", 1)[0]

    script_path = f"{script_dir}/{platform}.py"

    # 执行对应脚本
    result = subprocess.run(
        [sys.executable, script_path, "--url", url],
        capture_output=True,
        text=True,
    )

    print(result.stdout.strip() if result.returncode == 0 else result.stderr.strip())
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
