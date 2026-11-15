#!/usr/bin/env python3
"""Check a background brief (mode 2) for private-information terms and unsourced facts.

  python3 scripts/check_brief.py work/<slug>/brief.md [--json]

ERROR: a private-information term (address, family, health...) appears outside the scope line.
WARN: a table row or bullet with a year or a number but no link or [n] reference.
Exit 1 if any ERROR.
"""
import argparse
import json
import re
import sys

PRIVATE = [
    # zh
    "住址", "家庭住址", "住在", "电话号码", "手机号", "私人邮箱", "车牌", "配偶", "妻子", "丈夫",
    "老公", "老婆", "儿子", "女儿", "子女", "孩子", "父母", "离婚", "婚姻", "恋情", "病史", "生病",
    "癌症", "抑郁", "怀孕", "宗教信仰", "政治倾向", "性取向",
    # en
    "home address", "lives at", "phone number", "spouse", "husband", "wife", "son ", "daughter",
    "children", "divorce", "marriage", "pregnan", "diagnosed", "medical history", "illness",
    "religion", "sexual orientation",
]
SCOPE_HINT = ("范围", "Scope", "不查", "不含", "excluded", "Exclude")
SOURCE = re.compile(r"https?://|\[\d+\]|doi\.org|DOI|见来源|出处")
FACTLIKE = re.compile(r"(19|20)\d\d|\d{2,}")


def check(text):
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        if not any(h in line for h in SCOPE_HINT):
            for w in PRIVATE:
                if w.lower() in low:
                    out.append({"line": i, "level": "ERROR", "msg": f"private-information term: {w.strip()}"})
                    break
        s = line.strip()
        is_item = s.startswith("- ") or (s.startswith("|") and not set(s) <= set("|- "))
        if is_item and FACTLIKE.search(s) and not SOURCE.search(s):
            if s.startswith("| 年份") or s.startswith("| Year") or "YYYY" in s:
                continue
            out.append({"line": i, "level": "WARN", "msg": "fact-like line without a source"})
    return out


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("path")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    with open(a.path, encoding="utf-8") as f:
        res = check(f.read())
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        for r in res:
            print(f"{a.path}:{r['line']}: {r['level']}: {r['msg']}")
        print(f"{sum(r['level']=='ERROR' for r in res)} ERROR, {sum(r['level']=='WARN' for r in res)} WARN")
    return 1 if any(r["level"] == "ERROR" for r in res) else 0


if __name__ == "__main__":
    sys.exit(main())
