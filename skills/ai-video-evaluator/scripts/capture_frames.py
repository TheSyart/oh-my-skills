#!/usr/bin/env python3
"""Capture video frames at selected timestamps with ffmpeg.

Input:
  --video-url "<video direct URL or local path>"
  --times "12.3,45.0,78.5"
  --out-dir "<report asset directory>"

Output:
  JSON manifest printed to stdout and written to frames_manifest.json.
"""

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)


def resolve_ffmpeg(explicit_path: str | None) -> str | None:
    """Find ffmpeg even when the shell profile PATH was not loaded."""
    candidates = []
    if explicit_path:
        candidates.append(explicit_path)

    env_path = os.getenv("FFMPEG_BIN")
    if env_path:
        candidates.append(env_path)

    path_bin = shutil.which("ffmpeg")
    if path_bin:
        candidates.append(path_bin)

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
            return candidate
    return None


def is_usable_ffmpeg(candidate: str | None) -> bool:
    if not candidate or not os.path.isfile(candidate) or not os.access(candidate, os.X_OK):
        return False
    try:
        result = subprocess.run(
            [candidate, "-version"],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except Exception:
        return False
    return result.returncode == 0


def parse_time(value: str) -> float:
    """Parse seconds or HH:MM:SS.mmm into seconds."""
    value = value.strip()
    if not value:
        raise ValueError("empty timestamp")

    if ":" not in value:
        seconds = float(value)
    else:
        parts = value.split(":")
        if len(parts) > 3:
            raise ValueError(f"invalid timestamp: {value}")
        total = 0.0
        for part in parts:
            total = total * 60 + float(part)
        seconds = total

    if seconds < 0:
        raise ValueError(f"timestamp must be >= 0: {value}")
    return seconds


def parse_times(raw: str) -> list[float]:
    times = [parse_time(item) for item in raw.split(",") if item.strip()]
    if not times:
        raise ValueError("no valid timestamps provided")
    return times


def frame_name(index: int, seconds: float) -> str:
    safe_seconds = f"{seconds:.3f}".replace(".", "_")
    return f"frame_{index:03d}_{safe_seconds}s.jpg"


def ffmpeg_base_args(ffmpeg_bin: str) -> list[str]:
    return [ffmpeg_bin, "-hide_banner", "-loglevel", "error", "-nostdin"]


def ffmpeg_input_args(video_url: str, seconds: float, user_agent: str, referer: str | None) -> list[str]:
    args = ["-ss", f"{seconds:.3f}"]
    if video_url.startswith(("http://", "https://")):
        if user_agent:
            args.extend(["-user_agent", user_agent])
        if referer:
            args.extend(["-headers", f"Referer: {referer}\r\n"])
    return args


def capture_frame(
    video_url: str,
    seconds: float,
    out_path: Path,
    ffmpeg_bin: str,
    user_agent: str,
    referer: str | None,
    timeout: int,
) -> None:
    cmd = (
        ffmpeg_base_args(ffmpeg_bin)
        + ffmpeg_input_args(video_url, seconds, user_agent, referer)
        + [
            "-i",
            video_url,
            "-frames:v",
            "1",
            "-q:v",
            "2",
            "-y",
            str(out_path),
        ]
    )
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "ffmpeg failed").strip()
        raise RuntimeError(message)
    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RuntimeError("ffmpeg did not create a valid frame image")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture JPG frames from a video URL/path at comma-separated timestamps."
    )
    parser.add_argument("--video-url", required=True, help="Video direct URL or local file path")
    parser.add_argument("--times", required=True, help='Comma-separated seconds, e.g. "12.3,45,78.5"')
    parser.add_argument("--out-dir", required=True, help="Directory for frame JPGs and manifest")
    parser.add_argument("--ffmpeg-bin", default=None, help="Optional path to ffmpeg binary")
    parser.add_argument("--manifest-name", default="frames_manifest.json", help="Manifest filename")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT, help="HTTP user agent for ffmpeg")
    parser.add_argument("--referer", default=None, help="Optional HTTP Referer header")
    parser.add_argument("--timeout", type=int, default=60, help="Seconds to wait per frame")
    args = parser.parse_args()

    ffmpeg_bin = resolve_ffmpeg(args.ffmpeg_bin)
    if ffmpeg_bin is None:
        print(
            json.dumps(
                {
                    "error": "ffmpeg not found. Install ffmpeg, pass --ffmpeg-bin, or set FFMPEG_BIN before generating screenshot-based reports."
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

    frames = []
    errors = []
    for index, seconds in enumerate(times, start=1):
        out_path = out_dir / frame_name(index, seconds)
        try:
            capture_frame(
                args.video_url,
                seconds,
                out_path,
                ffmpeg_bin,
                args.user_agent,
                args.referer,
                args.timeout,
            )
            frames.append({"time": seconds, "path": str(out_path)})
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
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
