#!/usr/bin/env python3
"""Ping Crossref for DOIs in a work draft; append local figure checks.

Writes a line-oriented log. Does not prove experimental facts.
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DOI_RE = re.compile(
    r"(?:doi\.org/|DOI:\s*|doi:\s*)(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)",
    re.I,
)
FIG_MD = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
USER_AGENT = "famous-biologist-biography-skill/1.0"


def extract_dois(text: str) -> list[str]:
    seen: list[str] = []
    for raw in DOI_RE.findall(text):
        doi = raw.rstrip(".,;")
        while doi.endswith(")") and doi.count("(") < doi.count(")"):
            doi = doi[:-1]
        if doi not in seen:
            seen.append(doi)
    return seen


def crossref(doi: str, timeout: float) -> str:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            item = json.load(resp)["message"]
        year = (item.get("published") or {}).get("date-parts", [[None]])[0][0]
        title = (item.get("title") or [""])[0]
        title = re.sub(r"\s+", " ", title).strip()
        return f"PASS | {doi} | {year} | {title}"
    except urllib.error.HTTPError as exc:
        return f"FAIL | {doi} | HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001 — log any network/parse failure
        return f"FAIL | {doi} | {exc}"


def figure_lines(text: str, draft: Path) -> list[str]:
    lines = []
    for rel in FIG_MD.findall(text):
        if rel.startswith(("http://", "https://", "data:")):
            lines.append(f"REMOTE | SKIP | {rel}")
            continue
        path = (draft.parent / rel).resolve()
        flag = "PASS" if path.is_file() else "FAIL"
        bg = " | contains-BG" if re.search(r"BG-\d{3}", rel) else ""
        lines.append(f"LOCAL | {flag} | {rel}{bg}")
    return lines


def verification_passes(rows: list[str]) -> bool:
    """Return false for either DOI failures or missing local figures."""
    return not any(
        row.startswith("FAIL |") or row.startswith("LOCAL | FAIL |")
        for row in rows
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Crossref DOI + local figure log")
    ap.add_argument("--file", required=True, help="work draft markdown")
    ap.add_argument("--out", required=True, help="S7-verify-log.txt")
    ap.add_argument("--timeout", type=float, default=20.0)
    args = ap.parse_args()
    draft = Path(args.file)
    if not draft.exists():
        print(f"missing: {draft}", file=__import__("sys").stderr)
        return 2
    text = draft.read_text(encoding="utf-8")
    rows = [crossref(d, args.timeout) for d in extract_dois(text)]
    if not rows:
        rows.append("DOI | NONE | no DOI patterns in file")
    rows.extend(figure_lines(text, draft))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    for row in rows:
        print(row)
    return 0 if verification_passes(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
