#!/usr/bin/env python3
"""Reader-clean lint for public biography exports.

Complements qc_gate.py:
  - qc_gate.py checks evidence and structure in the work draft.
  - publish_lint.py checks that the public export contains no draft metadata,
    internal IDs, stage markers, unresolved notes, broken images, or
    authoring/package commentary.

Exit 0 = PUBLISH_CLEAN, 1 = LEAK (fix before shipping), 2 = file missing.
This does not judge factual correctness.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RULES: list[tuple[str, str, str]] = [
    ("内部 ID 外泄", r"BG-\d{3}|【BG-\d{3}】", "error"),
    (
        "内部阶段标记外泄",
        r"pipeline_run|run_id|MECH_(?:PASS|FAIL)|PUBLISH_CLEAN|"
        r"\bS[0-8](?:\.\d+)?\b|qc_gate|verify_dois|export_ship|publish_lint",
        "error",
    ),
    (
        "草稿专用标题外泄",
        r"^##\s*(?:数字与.*出处|出处与.*|数字与图注.*)\s*$",
        "error",
    ),
    ("未决标记外泄", r"\[待确认|\[待核|\[推测\]|待确认/二手", "error"),
    ("图片占位符外泄", r"<!--\s*FIGURE(?::|\s|-->)", "error"),
    (
        "作者或打包过程外泄",
        r"本示例|本包|再分发依据|不附带位图|生成说明|"
        r"编辑说明|读者稿|机械门禁|人工事实抽检",
        "error",
    ),
    ("自指元叙事偏多（建议降密度）", r"本篇|本文认为", "warn"),
]

FRONTMATTER = re.compile(r"\A\ufeff?---\s*\n")
CN = re.compile(r"[\u4e00-\u9fff]")
FIG_MD = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def cn_len(t: str) -> int:
    return len(CN.findall(t))


def check_images(text: str, base: Path) -> list[str]:
    """Check public image destinations and local file existence."""
    errors = []
    for rel in FIG_MD.findall(text):
        if rel.startswith(("http://", "https://", "data:")):
            continue
        if rel.startswith(("/", "~")):
            errors.append(f"不可移植的图片路径: {rel}")
            continue
        if re.search(r"BG-\d{3}", rel):
            errors.append(f"图片路径含内部 ID: {rel}")
        p = (base / rel).resolve()
        if not p.exists():
            errors.append(f"死链图片: {rel}")
    return errors


def scan(text: str, base: Path | None = None) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if FRONTMATTER.match(text):
        errors.append("YAML frontmatter 未剥离：公开文件不应带草稿元数据")
    if base is not None:
        errors.extend(check_images(text, base))
    for label, pat, severity in RULES:
        rx = re.compile(pat, re.M)
        hits = rx.findall(text)
        if not hits:
            continue
        sample = [h if isinstance(h, str) else h[0] for h in hits][:6]
        n = len(hits)
        if severity == "error":
            errors.append(f"{label}: {n} 处（如 {sample}）")
        else:
            if label.startswith("自指") and n < 6:
                continue
            warnings.append(f"{label}: {n} 处（如 {sample}）")
    return errors, warnings


def main() -> int:
    ap = argparse.ArgumentParser(description="Reader-clean publish lint")
    ap.add_argument("--file", required=True)
    ap.add_argument("--json-out", default="")
    args = ap.parse_args()
    path = Path(args.file)
    if not path.exists():
        print(f"文件不存在: {path}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8")
    errors, warnings = scan(text, base=path.parent)
    clean = len(errors) == 0
    verdict = "PUBLISH_CLEAN" if clean else "LEAK"
    print("=" * 52)
    print(f"PUBLISH LINT | {verdict} | {path.name}")
    print(f"cn≈{cn_len(text)}")
    print("=" * 52)
    for e in errors:
        print(f"ERROR  {e}")
    for w in warnings:
        print(f"WARN   {w}")
    print("-" * 52)
    print("可直接投放" if clean else "存在内部残留 — 修掉 ERROR 再投放")
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps({"file": str(path), "verdict": verdict,
                        "errors": errors, "warnings": warnings,
                        "cn_chars": cn_len(text)}, ensure_ascii=False, indent=2),
            encoding="utf-8")
    return 0 if clean else 1


if __name__ == "__main__":
    sys.exit(main())
