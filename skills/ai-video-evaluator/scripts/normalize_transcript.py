#!/usr/bin/env python3
"""Normalize ASR transcript text with a glossary and optional replacements."""

import argparse
import json
import re
import sys
from copy import deepcopy
from pathlib import Path


DEFAULT_GLOSSARY = Path(__file__).resolve().parents[1] / "assets" / "transcript_glossary.json"


def load_glossary(path: Path) -> dict:
    if not path.exists():
        return {"literal": [], "regex": []}
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("literal", [])
    data.setdefault("regex", [])
    return data


def parse_extra(values: list[str]) -> list[tuple[str, str]]:
    pairs = []
    for item in values:
        if "=" not in item:
            raise ValueError(f"extra replacement must be FROM=TO: {item}")
        left, right = item.split("=", 1)
        if not left:
            raise ValueError(f"empty FROM in replacement: {item}")
        pairs.append((left, right))
    return pairs


def apply_literal(text: str, pairs: list[tuple[str, str]], corrections: dict[str, dict]) -> str:
    for old, new in pairs:
        if old == new:
            continue
        count = text.count(old)
        if count:
            text = text.replace(old, new)
            key = f"literal:{old}->{new}"
            entry = corrections.setdefault(key, {"from": old, "to": new, "type": "literal", "count": 0})
            entry["count"] += count
    return text


def apply_regex(text: str, pairs: list[tuple[str, str]], corrections: dict[str, dict]) -> str:
    for pattern, repl in pairs:
        new_text, count = re.subn(pattern, repl, text, flags=re.IGNORECASE)
        if count and new_text != text:
            key = f"regex:{pattern}->{repl}"
            entry = corrections.setdefault(key, {"from": pattern, "to": repl, "type": "regex", "count": 0})
            entry["count"] += count
        text = new_text
    return text


def normalize_text(text: str, glossary: dict, extras: list[tuple[str, str]], corrections: dict[str, dict]) -> str:
    text = apply_literal(text, [(str(a), str(b)) for a, b in glossary.get("literal", [])], corrections)
    text = apply_literal(text, extras, corrections)
    text = apply_regex(text, [(str(a), str(b)) for a, b in glossary.get("regex", [])], corrections)
    return text


def normalize(data: dict, glossary: dict, extras: list[tuple[str, str]], keep_raw: bool) -> dict:
    result = deepcopy(data)
    corrections: dict[str, dict] = {}

    if keep_raw:
        result["raw_text"] = data.get("text", "")
        result["raw_sentences"] = deepcopy(data.get("sentences", []))

    result["text"] = normalize_text(str(result.get("text", "")), glossary, extras, corrections)
    for sentence in result.get("sentences", []):
        sentence["text"] = normalize_text(str(sentence.get("text", "")), glossary, extras, corrections)

    result["corrections"] = sorted(corrections.values(), key=lambda item: (-item["count"], item["from"]))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize a transcript JSON produced by transcribe.py.")
    parser.add_argument("--input", required=True, help="Input transcript JSON path")
    parser.add_argument("--out", default="-", help="Output transcript JSON path, or '-' for stdout")
    parser.add_argument("--glossary", default=str(DEFAULT_GLOSSARY), help="Glossary JSON path")
    parser.add_argument("--extra", action="append", default=[], help="Extra literal replacement: FROM=TO")
    parser.add_argument("--keep-raw", action="store_true", help="Keep raw_text and raw_sentences in output")
    args = parser.parse_args()

    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        glossary = load_glossary(Path(args.glossary))
        extras = parse_extra(args.extra)
        result = normalize(data, glossary, extras, args.keep_raw)
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1

    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out == "-":
        print(payload)
    else:
        Path(args.out).write_text(payload, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
