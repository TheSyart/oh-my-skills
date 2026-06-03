#!/usr/bin/env python3
"""Capture full video frames at selected timestamps with ffmpeg."""

from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)


def is_usable_ffmpeg(candidate: str | None) -> bool:
    if not candidate:
        return False
    path = Path(candidate).expanduser()
    if not path.is_file() or not os.access(path, os.X_OK):
        return False
    try:
        result = subprocess.run([str(path), "-version"], capture_output=True, text=True, timeout=15)
    except Exception:
        return False
    return result.returncode == 0


def resolve_ffmpeg(explicit_path: str | None = None) -> str | None:
    if explicit_path:
        return str(Path(explicit_path).expanduser()) if is_usable_ffmpeg(explicit_path) else None

    candidates = []
    if os.getenv("FFMPEG_BIN"):
        candidates.append(os.environ["FFMPEG_BIN"])
    if shutil.which("ffmpeg"):
        candidates.append(shutil.which("ffmpeg"))
    candidates.extend(
        [
            "/opt/homebrew/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            *glob.glob("/opt/homebrew/Cellar/ffmpeg/*/bin/ffmpeg"),
            *glob.glob("/usr/local/Cellar/ffmpeg/*/bin/ffmpeg"),
        ]
    )
    for candidate in candidates:
        if is_usable_ffmpeg(candidate):
            return str(Path(candidate).expanduser())
    return None


def parse_time(value: str) -> float:
    value = value.strip()
    if not value:
        raise ValueError("empty timestamp")
    if ":" not in value:
        seconds = float(value)
    else:
        total = 0.0
        for part in value.split(":"):
            total = total * 60 + float(part)
        seconds = total
    if seconds < 0:
        raise ValueError(f"timestamp must be non-negative: {value}")
    return seconds


def parse_times(raw: str) -> list[float]:
    times = [parse_time(item) for item in raw.split(",") if item.strip()]
    if not times:
        raise ValueError("no timestamps provided")
    return times


def frame_name(index: int, seconds: float) -> str:
    safe = f"{seconds:.3f}".replace(".", "_")
    return f"frame_{index:03d}_{safe}s.jpg"


def ffmpeg_input_args(video_url: str, seconds: float, user_agent: str, referer: str | None) -> list[str]:
    args = ["-ss", f"{seconds:.3f}"]
    if video_url.startswith(("http://", "https://")):
        if user_agent:
            args.extend(["-user_agent", user_agent])
        if referer:
            args.extend(["-headers", f"Referer: {referer}\r\n"])
    return args


def capture_frame(
    ffmpeg_bin: str,
    video_url: str,
    seconds: float,
    out_path: Path,
    user_agent: str,
    referer: str | None,
    timeout: int,
) -> None:
    cmd = (
        [ffmpeg_bin, "-hide_banner", "-loglevel", "error", "-nostdin"]
        + ffmpeg_input_args(video_url, seconds, user_agent, referer)
        + ["-i", video_url, "-frames:v", "1", "-q:v", "2", "-y", str(out_path)]
    )
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "ffmpeg failed").strip()
        raise RuntimeError(message)
    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RuntimeError("ffmpeg did not create a valid frame image")


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture full JPG frames from a video URL or local file.")
    parser.add_argument("--video-url", required=True, help="Direct video URL or local file")
    parser.add_argument("--times", required=True, help='Comma-separated seconds or HH:MM:SS values, e.g. "4.2,00:21,58.5"')
    parser.add_argument("--out-dir", required=True, help="Output directory for frames and manifest")
    parser.add_argument("--ffmpeg-bin", help="Explicit ffmpeg binary")
    parser.add_argument("--manifest-name", default="frames_manifest.json", help="Manifest file name")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT, help="HTTP user agent for ffmpeg")
    parser.add_argument("--referer", default=None, help="Optional HTTP Referer header")
    parser.add_argument("--timeout", type=int, default=60, help="Seconds per frame")
    args = parser.parse_args()

    ffmpeg_bin = resolve_ffmpeg(args.ffmpeg_bin)
    if not ffmpeg_bin:
        print(
            json.dumps(
                {
                    "error": "ffmpeg not found. Install ffmpeg, pass --ffmpeg-bin, or set FFMPEG_BIN before generating screenshot evidence."
                },
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 1

    try:
        times = parse_times(args.times)
    except Exception as exc:
        print(json.dumps({"error": f"invalid --times: {exc}"}, ensure_ascii=False), file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    frames: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for index, seconds in enumerate(times, start=1):
        out_path = out_dir / frame_name(index, seconds)
        try:
            capture_frame(ffmpeg_bin, args.video_url, seconds, out_path, args.user_agent, args.referer, args.timeout)
            frames.append({"time": seconds, "path": str(out_path), "file": out_path.name})
        except Exception as exc:
            errors.append({"time": seconds, "error": str(exc)})

    manifest = {
        "video_url": args.video_url,
        "out_dir": str(out_dir),
        "ffmpeg_bin": ffmpeg_bin,
        "frames": frames,
    }
    if errors:
        manifest["errors"] = errors

    manifest_path = out_dir / args.manifest_name
    manifest["manifest_path"] = str(manifest_path)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 1 if errors and not frames else 0


if __name__ == "__main__":
    raise SystemExit(main())
