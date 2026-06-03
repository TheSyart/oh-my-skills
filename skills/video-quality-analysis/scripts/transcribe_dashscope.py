#!/usr/bin/env python3
"""Transcribe a video URL with DashScope Paraformer and sentence timestamps."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import requests


SKILL_DIR = Path(__file__).resolve().parents[1]


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def load_api_key(explicit_env: str = "DASHSCOPE_API_KEY") -> str:
    load_dotenv(Path.cwd() / ".env")
    load_dotenv(SKILL_DIR / ".env")
    key = os.getenv(explicit_env, "")
    if not key:
        raise ValueError(f"{explicit_env} is not set; configure it before transcription")
    return key


def submit_task(video_url: str, api_key: str, model: str) -> str:
    response = requests.post(
        "https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
        },
        json={
            "model": model,
            "input": {"file_urls": [video_url]},
            "parameters": {"language_hints": ["zh", "en"]},
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    task_id = data.get("output", {}).get("task_id")
    if not task_id:
        raise RuntimeError(f"DashScope did not return task_id: {data}")
    return task_id


def poll_task(task_id: str, api_key: str, interval: float, max_wait: int) -> dict[str, Any]:
    start = time.time()
    while time.time() - start <= max_wait:
        response = requests.get(
            f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        output = data.get("output", {})
        status = output.get("task_status")
        if status == "SUCCEEDED":
            return output
        if status == "FAILED":
            raise RuntimeError(output.get("message") or "DashScope transcription failed")
        time.sleep(interval)
    raise TimeoutError(f"DashScope transcription timed out after {max_wait}s")


def fetch_transcription(result_url: str) -> dict[str, Any]:
    response = requests.get(result_url, timeout=30)
    response.raise_for_status()
    data = response.json()
    transcript = (data.get("transcripts") or [{}])[0]
    sentences = []
    for sentence in transcript.get("sentences", []) or []:
        sentences.append(
            {
                "text": str(sentence.get("text") or ""),
                "begin_time": int(sentence.get("begin_time") or 0),
                "end_time": int(sentence.get("end_time") or 0),
            }
        )
    return {"text": str(transcript.get("text") or ""), "sentences": sentences}


def transcribe(video_url: str, model: str, interval: float, max_wait: int, env_name: str) -> dict[str, Any]:
    api_key = load_api_key(env_name)
    task_id = submit_task(video_url, api_key, model)
    output = poll_task(task_id, api_key, interval, max_wait)
    results = output.get("results") or []
    if not results or not results[0].get("transcription_url"):
        raise RuntimeError(f"DashScope task succeeded but returned no transcription URL: {output}")
    payload = fetch_transcription(results[0]["transcription_url"])
    payload["task_id"] = task_id
    payload["model"] = model
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Transcribe a video URL through DashScope Paraformer.")
    parser.add_argument("--url", required=True, help="Direct video URL")
    parser.add_argument("--out", help="Write transcript JSON to this file")
    parser.add_argument("--model", default="paraformer-v2", help="DashScope ASR model")
    parser.add_argument("--poll-interval", type=float, default=2.0, help="Polling interval in seconds")
    parser.add_argument("--max-wait", type=int, default=300, help="Maximum wait in seconds")
    parser.add_argument("--env-name", default="DASHSCOPE_API_KEY", help="API key environment variable name")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    try:
        payload = transcribe(args.url, args.model, args.poll_interval, args.max_wait, args.env_name)
        text = json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None)
        if args.out:
            Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.out).write_text(text + "\n", encoding="utf-8")
        else:
            print(text)
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
