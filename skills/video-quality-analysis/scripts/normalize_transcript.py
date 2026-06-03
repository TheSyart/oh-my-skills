#!/usr/bin/env python3
"""Normalize ASR transcript text with a glossary and per-video replacements."""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_GLOSSARY = SKILL_DIR / "assets" / "transcript_glossary.json"


def load_glossary(path: Path) -> dict[str, list[list[str]]]:
    if not path.exists():
        return {"literal": [], "regex": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("literal", [])
    data.setdefault("regex", [])
    return data


def parse_extra(values: list[str]) -> list[tuple[str, str]]:
    pairs = []
    for value in values:
        if "=" not in value:
            raise ValueError(f"--extra must be FROM=TO: {value}")
        left, right = value.split("=", 1)
        if not left:
            raise ValueError(f"--extra has empty FROM: {value}")
        pairs.append((left, right))
    return pairs


def record(corrections: dict[str, dict[str, Any]], old: str, new: str, kind: str, count: int) -> None:
    key = f"{kind}:{old}->{new}"
    item = corrections.setdefault(key, {"from": old, "to": new, "type": kind, "count": 0})
    item["count"] += count


def apply_literal(text: str, pairs: list[tuple[str, str]], corrections: dict[str, dict[str, Any]]) -> str:
    for old, new in pairs:
        if old == new:
            continue
        count = text.count(old)
        if count:
            text = text.replace(old, new)
            record(corrections, old, new, "literal", count)
    return text


def apply_regex(text: str, pairs: list[tuple[str, str]], corrections: dict[str, dict[str, Any]]) -> str:
    for pattern, repl in pairs:
        new_text, count = re.subn(pattern, repl, text, flags=re.IGNORECASE)
        if count and new_text != text:
            text = new_text
            record(corrections, pattern, repl, "regex", count)
    return text


def normalize_text(
    text: str,
    glossary: dict[str, list[list[str]]],
    extras: list[tuple[str, str]],
    corrections: dict[str, dict[str, Any]],
) -> str:
    literal_pairs = [(str(a), str(b)) for a, b in glossary.get("literal", [])]
    regex_pairs = [(str(a), str(b)) for a, b in glossary.get("regex", [])]
    text = apply_literal(text, literal_pairs, corrections)
    text = apply_literal(text, extras, corrections)
    text = apply_regex(text, regex_pairs, corrections)
    return text


def normalize(data: dict[str, Any], glossary: dict[str, list[list[str]]], extras: list[tuple[str, str]], keep_raw: bool) -> dict[str, Any]:
    result = deepcopy(data)
    corrections: dict[str, dict[str, Any]] = {}

    if keep_raw:
        result["raw_text"] = data.get("text", "")
        result["raw_sentences"] = deepcopy(data.get("sentences", []))

    result["text"] = normalize_text(str(result.get("text", "")), glossary, extras, corrections)
    result_sentences = result.setdefault("sentences", [])
    for sentence in result_sentences:
        sentence["text"] = normalize_text(str(sentence.get("text", "")), glossary, extras, corrections)
        sentence["begin_time"] = int(sentence.get("begin_time") or 0)
        sentence["end_time"] = int(sentence.get("end_time") or 0)

    result["corrections"] = sorted(corrections.values(), key=lambda item: (-item["count"], item["from"]))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize a timestamped transcript JSON.")
    parser.add_argument("--input", required=True, help="Input transcript JSON")
    parser.add_argument("--out", default="-", help="Output path, or '-' for stdout")
    parser.add_argument("--glossary", default=str(DEFAULT_GLOSSARY), help="Glossary JSON path")
    parser.add_argument("--extra", action="append", default=[], help="Additional replacement FROM=TO")
    parser.add_argument("--keep-raw", action="store_true", help="Keep raw_text and raw_sentences")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = normalize(data, load_glossary(Path(args.glossary)), parse_extra(args.extra), args.keep_raw)
        text = json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None)
        if args.out == "-":
            print(text)
        else:
            Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.out).write_text(text + "\n", encoding="utf-8")
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
