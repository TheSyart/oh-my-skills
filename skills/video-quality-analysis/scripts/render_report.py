#!/usr/bin/env python3
"""Render report_data.json into the reusable HTML evidence report template."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = SKILL_DIR / "assets" / "report-template" / "report_template.html"
PLATFORM_LOGOS = {
    "douyin": ("抖音", SKILL_DIR / "assets" / "platform-logos" / "logo-douyin.png"),
    "kuaishou": ("快手", SKILL_DIR / "assets" / "platform-logos" / "logo-kuaishou.png"),
    "xhs": ("小红书", SKILL_DIR / "assets" / "platform-logos" / "logo-xiaohongshu.png"),
    "xiaohongshu": ("小红书", SKILL_DIR / "assets" / "platform-logos" / "logo-xiaohongshu.png"),
    "bilibili": ("B站", SKILL_DIR / "assets" / "platform-logos" / "logo-bilibili.png"),
}
SCORE_NAMES = ["知识价值", "概念准确", "证据质量", "信息密度", "焦虑操控", "可操作性"]
CLAIM_STATUS_CLASS = {"正确": "ok", "可疑": "warn", "错误": "bad", "无法核验": "mid", "不适用": "mid"}


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def slug_platform(raw: str) -> str:
    value = (raw or "").strip().lower()
    if value in {"xiaohongshu", "小红书"}:
        return "xhs"
    if value in {"抖音", "douyin"}:
        return "douyin"
    if value in {"快手", "kuaishou"}:
        return "kuaishou"
    if value in {"b站", "哔哩哔哩", "bilibili"}:
        return "bilibili"
    return value


def score_class(score: float) -> str:
    if score < 2.5:
        return "score-low"
    if score < 3.5:
        return "score-mid"
    return "score-high"


def score_percent(score: float) -> int:
    return max(0, min(100, round(score / 5 * 100)))


def verdict_class(label: str, score: float) -> str:
    text = label or ""
    if "不推荐" in text or score <= 13:
        return "verdict-bad"
    if "谨慎" in text or score <= 22:
        return "verdict-caution"
    return "verdict-good"


def score_items(data: dict[str, Any]) -> list[dict[str, Any]]:
    raw = data.get("scores") or []
    if isinstance(raw, dict):
        items = [{"name": key, **(value if isinstance(value, dict) else {"score": value})} for key, value in raw.items()]
    else:
        items = list(raw)
    by_name = {str(item.get("name")): item for item in items if isinstance(item, dict)}
    ordered = []
    for name in SCORE_NAMES:
        item = by_name.get(name, {})
        ordered.append({"name": name, "score": float(item.get("score") or 0), "reason": item.get("reason") or "未填写评分依据。"})
    return ordered


def render_score_cards(data: dict[str, Any]) -> str:
    cards = []
    for item in score_items(data):
        score = float(item["score"])
        cards.append(
            f'''<article class="score-card {score_class(score)}">
  <div class="score-head"><span>{esc(item["name"])}</span><strong>{esc(f"{score:g}")}/5</strong></div>
  <div class="bar" aria-hidden="true"><span style="width:{score_percent(score)}%"></span></div>
  <p>{esc(item["reason"])}</p>
</article>'''
        )
    return "\n".join(cards)


def list_items(items: list[dict[str, Any]]) -> str:
    if not items:
        return '<li><strong>未填写</strong><span>需要补充对应时间点和证据。</span></li>'
    parts = []
    for item in items:
        time = esc(item.get("time", ""))
        text = esc(item.get("text", ""))
        reason = esc(item.get("reason", ""))
        parts.append(f"<li><strong>{time}</strong><span>{text}</span><em>{reason}</em></li>")
    return "\n".join(parts)


def render_corrections(data: dict[str, Any]) -> str:
    corrections = data.get("corrections") or []
    if not corrections:
        return '<p class="empty-note">本次未记录专名纠错；仍需人工确认关键术语没有误识别。</p>'
    rows = []
    for item in corrections:
        rows.append(
            f'''<tr>
  <td>{esc(item.get("from"))}</td>
  <td>{esc(item.get("to"))}</td>
  <td>{esc(item.get("count", ""))}</td>
  <td>{esc(item.get("reason") or item.get("type") or "")}</td>
</tr>'''
        )
    return f'''<table class="compact-table">
  <thead><tr><th>原字幕</th><th>纠正后</th><th>次数</th><th>说明</th></tr></thead>
  <tbody>{"".join(rows)}</tbody>
</table>'''


def render_claim_rows(data: dict[str, Any]) -> str:
    claims = data.get("claims") or []
    if not claims:
        claims = [{"claim": "不适用", "status": "不适用", "reason": "视频不是知识教学或没有可抽取的明确断言。", "time": ""}]
    rows = []
    for item in claims:
        status = str(item.get("status") or "无法核验")
        tag_class = CLAIM_STATUS_CLASS.get(status, "mid")
        rows.append(
            f'''<tr>
  <td>{esc(item.get("claim"))}</td>
  <td><span class="tag {tag_class}">{esc(status)}</span></td>
  <td>{esc(item.get("reason"))}</td>
  <td>{esc(item.get("time"))}</td>
</tr>'''
        )
    return "\n".join(rows)


def placeholder_svg(label: str) -> str:
    label = esc(label or "No frame")
    svg = (
        f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1280 720'>"
        f"<rect width='1280' height='720' fill='%23161717'/>"
        f"<text x='640' y='360' text-anchor='middle' fill='%23f0e2c8' "
        f"font-size='54' font-family='Arial'>{label}</text></svg>"
    )
    return "data:image/svg+xml;utf8," + quote(svg, safe="/:=;'#% ")


def render_evidence_cards(data: dict[str, Any]) -> str:
    evidence = data.get("evidence") or []
    if not evidence:
        evidence = [{"time": "", "image": "", "subtitle": "未填写证据", "reason": "需要选择 3-6 个时间点。", "type": "待补充"}]
    cards = []
    for index, item in enumerate(evidence, start=1):
        src = str(item.get("image") or "").strip() or placeholder_svg(item.get("time") or f"Evidence {index}")
        cards.append(
            f'''<article class="evidence-card">
  <div class="frame-wrap"><img src="{esc(src)}" alt="Evidence frame at {esc(item.get("time"))}"></div>
  <div class="evidence-body">
    <div class="evidence-top"><span class="timecode">{esc(item.get("time"))}</span><span class="evidence-type">{esc(item.get("type") or "证据")}</span></div>
    <blockquote>{esc(item.get("subtitle"))}</blockquote>
    <p>{esc(item.get("reason"))}</p>
  </div>
</article>'''
        )
    return "\n".join(cards)


def render_overall(data: dict[str, Any]) -> str:
    overall = data.get("overall") or ""
    if isinstance(overall, list):
        return "\n".join(f"<p>{esc(item)}</p>" for item in overall)
    return f"<p>{esc(overall)}</p>" if overall else "<p>未填写总体判断。</p>"


def render_transcript(data: dict[str, Any]) -> str:
    transcript = data.get("transcript") or {}
    if isinstance(transcript, str):
        return esc(transcript)
    items = transcript.get("items") or []
    if not items and transcript.get("text"):
        return esc(transcript.get("text"))
    lines = []
    for item in items:
        lines.append(f'<span class="timeline-time">{esc(item.get("time"))}</span> {esc(item.get("text"))}')
    return "\n".join(lines) if lines else "未填写字幕摘要。"


def count_transcript(data: dict[str, Any]) -> int:
    transcript = data.get("transcript") or {}
    if isinstance(transcript, dict):
        return len(transcript.get("items") or [])
    return 1 if transcript else 0


def copy_platform_logo(platform: str, out_path: Path) -> tuple[str, str]:
    slug = slug_platform(platform)
    label, source = PLATFORM_LOGOS.get(slug, ("未知平台", None))
    if not source or not source.exists():
        return label, ""
    assets_dir = out_path.parent / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    target = assets_dir / source.name
    shutil.copy2(source, target)
    return label, f"assets/{target.name}"


def render(data: dict[str, Any], template_path: Path, out_path: Path) -> str:
    metadata = data.get("metadata") or {}
    verdict = data.get("verdict") or {}
    score = float(verdict.get("score") or sum(float(item["score"]) for item in score_items(data)))
    label = str(verdict.get("label") or ("推荐" if score >= 23 else "谨慎" if score >= 14 else "不推荐"))
    platform_label, platform_logo = copy_platform_logo(str(metadata.get("platform") or metadata.get("resource") or ""), out_path)
    anxiety = data.get("anxiety") or {}
    low_value = data.get("low_value") or data.get("lowValue") or {}
    transcript = data.get("transcript") or {}

    replacements = {
        "PAGE_TITLE": f"{metadata.get('title') or 'AI 视频质量评估报告'} - Video Quality Analysis",
        "REPORT_CLASS": verdict_class(label, score),
        "HERO_TITLE": metadata.get("title") or "AI 视频质量评估报告",
        "HERO_SUBTITLE": verdict.get("subtitle") or "基于字幕、截图与断言证据的内容质量评估。",
        "VERDICT_LABEL": label,
        "TOTAL_SCORE": f"{score:g}",
        "VERDICT_REASON": verdict.get("reason") or "未填写结论理由。",
        "VIDEO_TITLE": metadata.get("title") or "",
        "PLATFORM_LOGO_SRC": platform_logo,
        "PLATFORM_LABEL": platform_label,
        "VIDEO_ID": metadata.get("videoId") or metadata.get("video_id") or "",
        "TOPIC": metadata.get("topic") or "",
        "EVALUATED_AT": metadata.get("evaluated_at") or metadata.get("evaluatedAt") or "",
        "DURATION": metadata.get("duration") or "",
        "SCORE_CARDS_HTML": render_score_cards(data),
        "CORRECTIONS_HTML": render_corrections(data),
        "ANXIETY_LEVEL": anxiety.get("level") or "未填写",
        "ANXIETY_SUMMARY": anxiety.get("summary") or "未填写焦虑营销判断。",
        "ANXIETY_EVIDENCE_HTML": list_items(anxiety.get("evidence") or []),
        "LOW_VALUE_LEVEL": low_value.get("level") or "未填写",
        "LOW_VALUE_SUMMARY": low_value.get("summary") or "未填写低价值内容判断。",
        "LOW_VALUE_EVIDENCE_HTML": list_items(low_value.get("evidence") or []),
        "CLAIM_ROWS_HTML": render_claim_rows(data),
        "EVIDENCE_CARDS_HTML": render_evidence_cards(data),
        "OVERALL_ASSESSMENT_HTML": render_overall(data),
        "TRANSCRIPT_NOTE": transcript.get("note") if isinstance(transcript, dict) else "纠正后的关键字幕摘要。",
        "TRANSCRIPT_COUNT": count_transcript(data),
        "TRANSCRIPT_TEXT": render_transcript(data),
    }

    html_text = template_path.read_text(encoding="utf-8")
    for key, value in replacements.items():
        html_text = html_text.replace("{{" + key + "}}", str(value))
    leftovers = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", html_text)))
    if leftovers:
        raise RuntimeError(f"unreplaced template placeholders: {', '.join(leftovers)}")
    return html_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Video Quality Analysis HTML report.")
    parser.add_argument("--input", required=True, help="report_data.json path")
    parser.add_argument("--out", required=True, help="Output report.html path")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE), help="HTML template path")
    args = parser.parse_args()

    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        out_path = Path(args.out).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        html_text = render(data, Path(args.template), out_path)
        out_path.write_text(html_text, encoding="utf-8")
        print(json.dumps({"report": str(out_path)}, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
