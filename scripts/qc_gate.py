#!/usr/bin/env python3
"""Mechanical QC gate for evidence-grounded biography articles.

Exit 0 = MECH_PASS, 1 = MECH_FAIL.
This checks structural and evidence hygiene, not factual correctness.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

AI_PATTERNS = [
    r"想象一下",
    r"让我们[一]?起",
    r"值得一提的是",
    r"不容忽视的是",
    r"值得注意的是",
    r"无疑[,，]",
    r"不可否认",
    r"综上所述",
    r"本节核心论点",
    r"\*\*本文认为\*\*",
]

# Editorial instructions that should not appear in reader prose.
ASIDE_PATTERNS = [
    r"要另(?:行)?核(?:对|验)",
    r"这一条(?:可以|需要)保留",
    r"正文以.{0,20}为准",
    r"结论(?:只)?停在",
    r"本文只(?:讨论|处理|停在)",
    r"不在本文(?:讨论|展开|处理)",
    r"(?:应该|需要)写在正文里",
    r"(?:此处|这里)(?:补|加|删除|保留)(?:一段|一句|说明)",
]

# Compressed editorial or methods-summary phrasing that usually leaks notes.
ABSTRACT_NOTE_PATTERNS = [
    r"故合并统计",
    r"未观察到.{0,16}差异，故",
    r"并不改变这一(?:比例|结果|结论)",
    r"上述结果(?:与|同).{0,20}一致，故",
]

PLACEHOLDER_DOI = re.compile(
    r"10\.\d{4,}/[^\s\]\)]*(?:xxxxx|XXXXX|doi\.org/XXXX)", re.I
)
FIG_MD = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
CITE = re.compile(r"\[(\d+)\]")
REF_LINE = re.compile(r"^\[(\d+)\]\s")


def load(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def cn_len(t: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", t))


def parse_bib_ids(t: str) -> set[int]:
    ids = set()
    for line in t.splitlines():
        m = REF_LINE.match(line.strip())
        if m:
            ids.add(int(m.group(1)))
    return ids


def cited_ids(t: str) -> set[int]:
    # ignore bib section lines themselves for "body cites"
    body = t
    for marker in ("## 参考文献", "## References", "# 参考文献"):
        if marker in t:
            body = t.split(marker)[0]
            break
    return {int(x) for x in CITE.findall(body)}


def check_images(t: str, base: Path) -> list[str]:
    errs = []
    for rel in FIG_MD.findall(t):
        if rel.startswith(("http://", "https://", "data:")):
            continue
        p = (base / rel).resolve()
        if not p.exists():
            errs.append(f"死链图片: {rel}")
    return errs


def audit(path: Path, profile: str) -> dict:
    t = load(path)
    base = path.parent
    errors: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []

    n_cn = cn_len(t)
    notes.append(f"汉字约 {n_cn}")

    # placeholders
    if PLACEHOLDER_DOI.search(t) or "arXiv:2504.xxxxx" in t or "xxxxx" in t.lower():
        errors.append("存在占位 DOI / xxxxx")

    # images
    errors.extend(check_images(t, base))

    # FIGURE comments without files are OK; broken md images are not
    fig_comments = len(re.findall(r"<!--\s*FIGURE:", t))
    if fig_comments:
        notes.append(f"未解析 FIGURE 占位块: {fig_comments}（需 S5 落盘后替换）")

    # citations
    bib = parse_bib_ids(t)
    cited = cited_ids(t)
    if cited and not bib:
        warnings.append("正文有 [n] 引用但未检测到参考文献列表")
    dangling = sorted(cited - bib)
    unused = sorted(bib - cited)
    if dangling:
        errors.append(f"悬空引用（文中有、文献表无）: {dangling[:20]}")
    if unused and profile == "wechat":
        warnings.append(f"未引用文献条目: {unused[:15]}（建议删或改用）")
    # AI flavor density
    ai_hits = []
    for pat in AI_PATTERNS:
        ai_hits.extend(re.findall(pat, t))
    if len(ai_hits) >= 8:
        warnings.append(f"AI 套话偏多: {len(ai_hits)} 处（如 {ai_hits[:5]}）")
    elif ai_hits:
        notes.append(f"AI 套话: {len(ai_hits)} 处")

    if profile == "wechat":
        aside_hits = []
        for pat in ASIDE_PATTERNS:
            aside_hits.extend(re.findall(pat, t))
        if aside_hits:
            errors.append(
                f"作者旁白 {len(aside_hits)} 处（如 {aside_hits[:6]}）。"
                "请把编辑说明移出读者稿。"
            )
        note_hits = []
        for pat in ABSTRACT_NOTE_PATTERNS:
            note_hits.extend(re.findall(pat, t))
        if note_hits:
            errors.append(
                f"压缩式编辑/方法说明 {len(note_hits)} 处（如 {note_hits[:6]}）。"
                "请改成有明确行动者、观察或判断的读者句。"
            )

    # profile length bands (warning only — not vanity pass)
    if profile == "wechat":
        if n_cn < 2000:
            warnings.append(f"偏短: {n_cn}（传记长文通常至少 2000 汉字）")
        if n_cn > 5000:
            warnings.append(f"偏长: {n_cn}（检查是否需要删减或拆分）")
        thesis = t.count("本文认为")
        if thesis > 4:
            warnings.append(f"「本文认为」过多: {thesis}（建议 ≤3）")

    mech_pass = len(errors) == 0
    return {
        "file": str(path),
        "profile": profile,
        "cn_chars": n_cn,
        "mech_pass": mech_pass,
        "errors": errors,
        "warnings": warnings,
        "notes": notes,
        "cited": len(cited),
        "bib": len(bib),
        "verdict": "MECH_PASS" if mech_pass else "MECH_FAIL",
        "human_required": True,
        "message": (
            "机械门禁通过 — 仍须人工事实抽检"
            if mech_pass
            else "机械门禁失败 — 修复 errors 后再跑"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Biography/article mechanical QC gate")
    ap.add_argument("--file", required=True)
    ap.add_argument("--profile", choices=["wechat", "article"], default="wechat")
    ap.add_argument("--json-out", default="")
    args = ap.parse_args()
    path = Path(args.file)
    if not path.exists():
        print(f"文件不存在: {path}", file=sys.stderr)
        return 2
    r = audit(path, args.profile)
    print("=" * 50)
    print(f"QC GATE | {r['verdict']} | {path.name}")
    print(f"profile={r['profile']} cn≈{r['cn_chars']} cites={r['cited']} bib={r['bib']}")
    print("=" * 50)
    for e in r["errors"]:
        print(f"ERROR  {e}")
    for w in r["warnings"]:
        print(f"WARN   {w}")
    for n in r["notes"]:
        print(f"NOTE   {n}")
    print("-" * 50)
    print(r["message"])
    print("HUMAN_REQUIRED: yes")
    out = Path(args.json_out) if args.json_out else path.with_suffix(".qc.json")
    out.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out}")
    return 0 if r["mech_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
