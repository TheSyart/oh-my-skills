# Transcript Correction

Correct subtitles before scoring. Wrong subtitles can create false concept errors, wrong evidence quotes, and unfair scores.

## Procedure

1. Build a proper-name list from title, topic, screenshots, context, and domain knowledge.
2. Run `scripts/normalize_transcript.py` with the default glossary.
3. Add per-video `--extra "wrong=correct"` replacements for obvious ASR errors.
4. Use only the corrected transcript in report quotes, claim tables, evidence cards, and summaries.
5. Keep uncertain terms unchanged or mark them as `疑似 X`; never invent certainty.

## Common AI Terms

- OpenAI, ChatGPT, Codex, Claude Code, Anthropic, Cursor, Gemini, Midjourney, Stable Diffusion.
- SDK, API, model context protocol, tool use, tool result, CLAUDE.md.

## Report Use

Mention corrections only when they materially affect judgment. Do not dump raw ASR text into the report.
