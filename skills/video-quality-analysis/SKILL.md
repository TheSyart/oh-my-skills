---
name: video-quality-analysis
description: Evaluate AI short videos from Douyin, Kuaishou, Xiaohongshu, or Bilibili links. Use when users need to parse a shared video link, transcribe it with timestamps, correct AI tool names in subtitles, capture evidence frames, identify AI anxiety marketing or empty low-quality content, review claims, score six quality dimensions, and generate an evidence-backed HTML report.
---

# Video Quality Analysis

Use this skill to turn a short-video share link into an evidence-backed quality report. The goal is to help ordinary viewers decide whether an AI-related video is worth watching, whether it sells AI anxiety, and whether its claims are supported by transcript and screenshot evidence.

This is a fresh implementation. Do not use or reference any other local video-evaluator skill.

## Workflow

1. Parse the share link.
   ```bash
   SKILL_DIR="$HOME/.codex/skills/video-quality-analysis"
   python3 "$SKILL_DIR/scripts/parse_link.py" --input "<share text or URL>" --out "<workdir>/metadata.json"
   ```

2. Transcribe the parsed direct video URL with DashScope.
   ```bash
   python3 "$SKILL_DIR/scripts/transcribe_dashscope.py" \
     --url "<metadata.url>" \
     --out "<workdir>/transcript.raw.json"
   ```

3. Correct the transcript before scoring.
   ```bash
   python3 "$SKILL_DIR/scripts/normalize_transcript.py" \
     --input "<workdir>/transcript.raw.json" \
     --out "<workdir>/transcript.normalized.json"
   ```
   Add per-video corrections when needed:
   ```bash
   python3 "$SKILL_DIR/scripts/normalize_transcript.py" \
     --input "<workdir>/transcript.raw.json" \
     --out "<workdir>/transcript.normalized.json" \
     --extra "open air=OpenAI" \
     --extra "cloud code=Claude Code"
   ```

4. Select 3-6 evidence timepoints from the corrected transcript. Prefer the opening promise, strongest fear hook, key claim, proof gap, and final conversion action. Capture frames:
   ```bash
   python3 "$SKILL_DIR/scripts/capture_frames.py" \
     --video-url "<metadata.url>" \
     --times "4.2,21.0,58.5" \
     --out-dir "<report_dir>/assets"
   ```

5. Score and write report data using the references in this skill. Render HTML:
   ```bash
   python3 "$SKILL_DIR/scripts/render_report.py" \
     --input "<workdir>/report_data.json" \
     --out "<report_dir>/report.html"
   ```

## Evidence Rules

Always ground the judgment in the corrected subtitle and screenshot evidence. Do not judge from title style or visual tone alone.

Read these references as needed:

- `references/scoring-rubric.md`: six 0-5 scoring dimensions and recommendation thresholds.
- `references/evidence-selection.md`: how to choose 3-6 timepoints and what each point should prove.
- `references/transcript-correction.md`: proper-name correction workflow and uncertainty rules.
- `references/report-writing.md`: direct but evidence-anchored report voice.

## Requirements

- Python 3.9+.
- `requests` for parsing/transcription HTTP calls.
- `aiohttp` if parsing Bilibili through the vendored parser.
- `ffmpeg` is required for complete HTML reports. If frame capture fails because ffmpeg is missing, stop and ask the user to install ffmpeg instead of producing a complete report without screenshot evidence.
- `DASHSCOPE_API_KEY` must be set in the environment or in a `.env` file in the current working directory or skill directory for transcription.

## Assets

- `assets/report-template/report_template.html`: reusable single-page HTML template.
- `assets/platform-logos/`: local platform logo PNGs copied from the user's desktop.
- `assets/test-fixtures/report_data.json`: fixture for rendering and visual QA.

## Parser Attribution

The link parser code in `scripts/vendor/extra_link/` is vendored from `TheSyart/extra-link` at commit `154fade02fd325b247d1f3c074d6a3af9267775e` under the MIT License. Preserve `scripts/vendor/extra_link/LICENSE` and `scripts/vendor/extra_link/VENDORED_EXTRA_LINK.md` when modifying or distributing this skill.
