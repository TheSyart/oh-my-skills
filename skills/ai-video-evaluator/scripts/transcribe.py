#!/usr/bin/env python3
"""视频语音转文本 - 输入视频URL，输出 {text, sentences}"""

import json
import sys
import time
import os
import argparse
import requests


def load_api_key() -> str:
    """从 .env 文件加载 API Key"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip().startswith("DASHSCOPE_API_KEY="):
                    return line.strip().split("=", 1)[1]
    key = os.getenv("DASHSCOPE_API_KEY", "")
    if key:
        return key
    raise ValueError("未配置 DASHSCOPE_API_KEY，请在 .env 文件中配置")


def submit_task(video_url: str, api_key: str) -> str:
    """提交转录任务，返回 task_id"""
    resp = requests.post(
        "https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
        },
        json={
            "model": "paraformer-v2",
            "input": {"file_urls": [video_url]},
            "parameters": {"language_hints": ["zh", "en"]},
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    task_id = data.get("output", {}).get("task_id")
    if not task_id:
        raise ValueError(f"未返回 task_id: {data}")
    return task_id


def poll_task(task_id: str, api_key: str, max_wait: int = 300) -> dict:
    """轮询任务状态，返回结果"""
    start = time.time()
    while time.time() - start < max_wait:
        resp = requests.get(
            f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )
        if not resp.ok:
            time.sleep(2)
            continue

        data = resp.json()
        status = data.get("output", {}).get("task_status")

        if status == "SUCCEEDED":
            return data["output"]
        if status == "FAILED":
            msg = data.get("output", {}).get("message", "转写失败")
            raise ValueError(f"转写失败: {msg}")

        time.sleep(2)

    raise TimeoutError("转录超时")


def get_result(result_url: str) -> dict:
    """从 transcription_url 获取转录结果"""
    resp = requests.get(result_url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    transcript = data.get("transcripts", [{}])[0]

    sentences = [
        {"text": s.get("text", ""), "begin_time": s.get("begin_time", 0), "end_time": s.get("end_time", 0)}
        for s in transcript.get("sentences", [])
    ]

    return {
        "text": transcript.get("text", ""),
        "sentences": sentences,
    }


def transcribe(video_url: str) -> dict:
    """完整转录流程"""
    api_key = load_api_key()
    print(f"提交转录任务...", file=sys.stderr)
    task_id = submit_task(video_url, api_key)
    print(f"任务ID: {task_id}，轮询中...", file=sys.stderr)
    output = poll_task(task_id, api_key)
    result_url = output["results"][0]["transcription_url"]
    return get_result(result_url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="视频直链URL")
    args = parser.parse_args()

    try:
        result = transcribe(args.url)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)
