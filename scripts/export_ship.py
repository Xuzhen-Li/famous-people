#!/usr/bin/env python3
"""Export a work artifact to a ship (reader-clean) file — mechanical pass only.

Does the SAFE, repeatable stripping:
  - remove YAML frontmatter
  - drop internal QC provenance tables (from a `## 数字与…出处` / `## 数字与出处`
    / `## 出处与…` heading to the next same-level `## ` heading or EOF)

It does NOT rewrite prose. After running, fix remaining prose leaks by hand and
gate with publish_lint.py (PUBLISH_CLEAN). Two-step by design: machines strip
structure, humans rewrite meaning.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

FRONTMATTER = re.compile(r"\A\ufeff?---\s*\n.*?\n---\s*\n", re.S)
# internal provenance / QC tables that must not ship
DROP_SECTION_HEADINGS = re.compile(
    r"^##\s*(数字与.*出处|数字与出处|出处与.*|数字与图注.*)\s*$", re.M
)


def strip_frontmatter(t: str) -> str:
    return FRONTMATTER.sub("", t, count=1)


def drop_internal_sections(t: str) -> tuple[str, list[str]]:
    lines = t.splitlines(keepends=True)
    out: list[str] = []
    dropped: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if DROP_SECTION_HEADINGS.match(line.strip("\n")):
            dropped.append(line.strip())
            i += 1
            while i < len(lines) and not re.match(r"^##\s", lines[i]):
                i += 1
            continue
        out.append(line)
        i += 1
    return "".join(out), dropped


def main() -> int:
    ap = argparse.ArgumentParser(description="Export work artifact -> ship file (mechanical)")
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", dest="dst", required=True)
    args = ap.parse_args()
    src = Path(args.src)
    if not src.exists():
        print(f"输入不存在: {src}", file=sys.stderr)
        return 2
    text = src.read_text(encoding="utf-8")
    text = strip_frontmatter(text)
    text, dropped = drop_internal_sections(text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    dst = Path(args.dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    print(f"wrote {dst}")
    print(f"dropped frontmatter + {len(dropped)} internal section(s): {dropped}")
    print("下一步：手工改写残留散文脚手架，再跑 publish_lint.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
