#!/usr/bin/env python3
"""Mechanical check for a 生物学名人系列 article. Stdlib only."""

import argparse
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

HANZI = re.compile(r"[\u4e00-\u9fff]")
SENTENCE_SPLIT = re.compile(r"[。！？]")
HEADING = re.compile(r"^#{1,6}\s+(.*)$")
REF_HEADING = re.compile(r"^(参考文献|references)\s*$", re.I)
IMAGE_LINE = re.compile(r"^!\[[^\]]*\]\([^)]*\)\s*$")
IMAGE_FIND = re.compile(r"!\[([^\]]*)\]\(([^)]*)\)")
ITALIC_LINE = re.compile(r"^(\*[^*\n]+\*|_([^_\n]+)_)[。！？]?$")
CITE = re.compile(r"\[(\d+(?:\s*[,，、\-–]\s*\d+)*)\]")
FRONTMATTER = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.S)

SOURCE_WALK = r"档案|新闻稿|颁奖词|授奖辞|讲稿里|讲演里|论文里|短文里|短讯里|通讯里|文章里|传记里|传记写|简历里"
DISCLAIM = r"不是一回事|还不是|这是后来|是后来的|不能倒回|不要混|不要合成|读者只需|读者可以只|并不是后来"

ANALOGY = [
    re.compile(r"像[^。！？\n]{0,80}一样"),
    re.compile(r"好比"),
    re.compile(r"犹如"),
    re.compile(r"仿佛"),
    re.compile(r"如同"),
    re.compile(r"就像"),
]
HYPE = (
    "伟大",
    "震撼",
    "颠覆",
    "改写了",
    "史诗",
    "传奇",
    "巨匠",
    "神秘面纱",
    "原来如此",
    "让我们",
    "不禁",
    "无疑",
)
LEAKS = (
    ("[待确认]", r"\[待确认\]"),
    ("[推测]", r"\[推测\]"),
    ("TODO", r"\bTODO\b"),
    ("facts.md", r"facts\.md"),
    ("Walk", r"\bWalk\b"),
    ("Selected", r"\bSelected\b"),
    ("S1", r"\bS1\b"),
    ("S2", r"\bS2\b"),
    ("brief", r"\bbrief\b"),
)


def hanzi_count(text):
    return len(HANZI.findall(text))


def median(values):
    if not values:
        return 0
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def percentile_90(values):
    if not values:
        return 0
    ordered = sorted(values)
    index = max(0, math.ceil(0.9 * len(ordered)) - 1)
    return ordered[index]


def split_frontmatter(text):
    match = FRONTMATTER.match(text)
    if not match:
        return text
    return text[match.end() :]


def split_body_and_refs(text):
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        heading = HEADING.match(line.strip())
        if heading and REF_HEADING.match(heading.group(1).strip()):
            body = "".join(lines[:i])
            refs = "".join(lines[i + 1 :])
            return body, refs, True
    return text, "", False


def prose_lines(body):
    paragraphs = []
    current = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            if current:
                paragraphs.append("".join(current))
                current = []
            continue
        if HEADING.match(line) or IMAGE_LINE.match(line) or ITALIC_LINE.match(line):
            continue
        if line.startswith(">"):
            line = line.lstrip(">").strip()
            if not line:
                continue
        current.append(line)
    if current:
        paragraphs.append("".join(current))
    return paragraphs


def citation_numbers(text):
    found = []
    for match in CITE.finditer(text):
        parts = re.split(r"\s*[,，、\-–]\s*", match.group(1))
        for part in parts:
            if part.isdigit():
                found.append(int(part))
    return found


def reference_numbers(refs):
    numbers = set(citation_numbers(refs))
    for line in refs.splitlines():
        stripped = line.strip()
        numbered = re.match(r"^(\d+)\s*[\.、\)]\s+\S", stripped)
        if numbered:
            numbers.add(int(numbered.group(1)))
    return numbers


def sentence_lengths(paragraphs):
    lengths = []
    for paragraph in paragraphs:
        for piece in SENTENCE_SPLIT.split(paragraph):
            count = hanzi_count(piece)
            if count:
                lengths.append(count)
    return lengths


def image_refs(body):
    lines = body.splitlines()
    found = []
    for index, raw in enumerate(lines):
        for match in IMAGE_FIND.finditer(raw):
            found.append((index, match.group(2).strip()))
    return lines, found


def next_nonempty_line(lines, index):
    for later in lines[index + 1 :]:
        stripped = later.strip()
        if stripped:
            return stripped
    return ""


def prev_nonempty_line(lines, index):
    for earlier in reversed(lines[:index]):
        stripped = earlier.strip()
        if stripped:
            return stripped
    return ""


def svg_parse_error(file_path, path):
    try:
        text = file_path.read_bytes().decode("utf-8")
        ET.fromstring(text)
    except (UnicodeDecodeError, ET.ParseError):
        return f"SVG 无法解析（多半是中文乱码）：{path}"
    if "\ufffd" in text:
        return f"SVG 无法解析（多半是中文乱码）：{path}"
    return None


def title_tail(text):
    for line in text.splitlines():
        if not line.startswith("# "):
            continue
        title = line[2:].strip()
        if "：" in title:
            return title.rsplit("：", 1)[1].strip()
        if "｜" in title:
            return title.rsplit("｜", 1)[1].strip()
        return ""
    return ""


def analyze(text, base_dir=None):
    raw = split_frontmatter(text)
    body, refs, has_refs = split_body_and_refs(raw)
    paragraphs = prose_lines(body)
    para_counts = [hanzi_count(p) for p in paragraphs]
    sentences = sentence_lengths(paragraphs)
    prose = "\n".join(paragraphs)
    short_n = sum(1 for n in sentences if n < 12)
    sentence_n = len(sentences)
    analogy_n = sum(len(pattern.findall(prose)) for pattern in ANALOGY)
    errors = []
    warnings = []

    for label, pattern in LEAKS:
        if re.search(pattern, body):
            errors.append(f"正文出现过程标记：{label}")
    if not has_refs:
        errors.append("没有「参考文献」一节")
    else:
        known = reference_numbers(refs)
        missing = sorted({n for n in citation_numbers(body) if n not in known})
        for number in missing:
            errors.append(f"正文的 [{number}] 在参考文献里没有对应条目")
    for count in para_counts:
        if count > 600:
            errors.append(f"有段落超过 600 字（{count}）")
            break
    med = median(sentences)
    if med < 15:
        errors.append(f"句子中位长度 {med:g} 字，低于 15 字")
    if 15 <= med < 22:
        warnings.append(
            f"句子中位 {med:g} 字，一句一断偏碎：把同一件事的起因和结果用「因为/于是/所以/可是」接成一句；不要只把句号改成逗号"
        )
    if med > 45:
        warnings.append(f"句子中位 {med:g} 字，可能一逗到底，拆开一些长句")
    long_n = sum(1 for n in sentences if n > 80)
    if long_n > 5:
        warnings.append(f"超过 80 字的长句 {long_n} 句")

    if sentence_n and short_n / sentence_n > 0.35:
        warnings.append(
            f"短于 12 字的句子占 {short_n / sentence_n:.0%}（{short_n}/{sentence_n}）"
        )
    n = hanzi_count(prose)
    if n < 4000:
        warnings.append(f"正文汉字 {n}，少于 4000，可能讲得太浅；回 facts.md 看有没有没讲开的事")
    if analogy_n > 3:
        warnings.append(f"比方标记 {analogy_n} 处，多于 3 处")
    paraphrase_n = len(re.findall(r"[他她]写", prose))
    if paraphrase_n > 6:
        warnings.append(f"「他写/她写」{paraphrase_n} 处，像在转述论文")
    source_n = len(re.findall(SOURCE_WALK, prose))
    if source_n > 6:
        warnings.append(f"按资料转述的说法（档案/新闻稿/授奖辞/论文里……）{source_n} 处")
    disclaim_n = len(re.findall(DISCLAIM, prose))
    if disclaim_n > 2:
        warnings.append(f"撇清或提醒读者的句式（不是一回事/还不是/这是后来……）{disclaim_n} 处")
    stand_in_n = len(re.findall(r"账|图纸", prose))
    if stand_in_n:
        warnings.append(f"「账 / 图纸」这类借来的说法 {stand_in_n} 处，换成实验、推算、表、结论")
    symbols = set(re.findall(r"(?<![A-Za-z0-9])[A-Za-z]{1,3}(?:-[a-z]?\d+|\d+)?(?![A-Za-z0-9])", prose))
    symbols -= {"DNA", "RNA", "X", "Y"}
    if len(symbols) > 6:
        warnings.append(f"正文里有 {len(symbols)} 种字母符号（{'、'.join(sorted(symbols))}），只留主线必需的一两个")
    textbook = re.findall(
        r"叫(?:作|做)?(?:减数分裂|有丝分裂|等位|配子|二倍体|受精)"
        r"|(?:DNA|染色体|染色质|基因|有丝分裂|减数分裂)(?:就)?是(?:构成|组成)[^，。]{0,10}物质",
        prose,
    )
    if textbook:
        warnings.append(f"给课本里的词下了定义 {len(textbook)} 处（{'、'.join(textbook)}），读者学过，直接用")
    jargon_n = len(re.findall(r"\bkb\b|编号", prose))
    if jargon_n:
        warnings.append(f"「kb / 编号」这类笔记细节 {jargon_n} 处，留在 facts.md")
    years = [int(y) for y in re.findall(r"(?<!\d)(1[6-9]\d\d|20\d\d)(?=\s*年)", prose)]
    recent_floor = date.today().year - 10
    if years and max(years) < recent_floor:
        warnings.append(f"正文最晚只写到 {max(years)} 年，后续没讲到最近十年（{recent_floor} 年以后）的研究进展")
    date_n = max((len(re.findall(r"[0-9一二]{1}[0-9〇一二三四五六七八九]{3}\s*年", p)) for p in paragraphs), default=0)
    if date_n > 6:
        warnings.append(f"有一段出现 {date_n} 个年份，像年表")
    for word in HYPE:
        hits = prose.count(word)
        for _ in range(hits):
            warnings.append(f"套话：{word}")

    image_lines, found = image_refs(body)
    for index, path in found:
        if path.startswith("http://") or path.startswith("https://"):
            warnings.append(f"图片是外链，没有下载到本地：{path}")
        elif base_dir is not None and not (Path(base_dir) / path).is_file():
            errors.append(f"图片文件不存在：{path}")
        elif base_dir is not None and path.endswith(".svg"):
            message = svg_parse_error(Path(base_dir) / path, path)
            if message:
                errors.append(message)
        if not ITALIC_LINE.match(next_nonempty_line(image_lines, index)):
            warnings.append(f"图片缺图注：{path}")
        before = prev_nonempty_line(image_lines, index)
        if before and not before.startswith(("#", "!", "*", ">")) and hanzi_count(before) < 50:
            warnings.append(f"图片前面是一段很短的话，像是为放图补写的：{before}")
    if len(found) < 6:
        warnings.append(f"配图 {len(found)} 张，少于 6 张")
    k = sum(1 for _, path in found if path.endswith(".svg"))
    if k:
        warnings.append(f"用了自绘 SVG 图 {k} 张，改找网上现成的图")

    tail = title_tail(raw)
    tail_n = hanzi_count(tail)
    if tail_n > 18:
        warnings.append(f"题目后半句 {tail_n} 字，太长（真人题目多在 4–18 字）：{tail}")
    h1 = ""
    for line in raw.splitlines():
        if line.startswith("# "):
            h1 = line[2:].strip()
            break
    if re.search(r"怎样|为什么|如何|竟然|竟", h1):
        warnings.append(f"题目在设悬念：{h1}")

    for raw in body.splitlines():
        stripped = raw.strip()
        if not stripped.startswith("## "):
            continue
        heading = HEADING.match(stripped)
        if not heading:
            continue
        title = heading.group(1).strip()
        if hanzi_count(title) > 12:
            warnings.append(f"小标题太长：{title}")

    return {
        "hanzi": n,
        "sentences": {
            "n": sentence_n,
            "median": med,
            "p90": percentile_90(sentences),
            "short_n": short_n,
            "short_share": (short_n / sentence_n) if sentence_n else 0,
        },
        "paragraphs": {
            "n": len(para_counts),
            "median": median(para_counts),
            "max": max(para_counts) if para_counts else 0,
        },
        "analogy_markers": analogy_n,
        "images": len(found),
        "errors": errors,
        "warnings": warnings,
    }


def format_report(report):
    s = report["sentences"]
    p = report["paragraphs"]
    lines = [
        f"正文汉字：{report['hanzi']}",
        (
            f"句子：{s['n']} 句，中位 {s['median']:g} 字，"
            f"p90 {s['p90']:g} 字，短于 12 字 {s['short_share']:.0%}"
            f"（{s['short_n']}/{s['n']}）"
        ),
        f"段落：{p['n']} 段，中位 {p['median']:g} 字，最长 {p['max']} 字",
        f"配图：{report['images']} 张",
        f"比方标记：{report['analogy_markers']}",
    ]
    if report["warnings"]:
        lines.append("WARN：")
        lines.extend(f"  - {item}" for item in report["warnings"])
    else:
        lines.append("WARN：无")
    if report["errors"]:
        lines.append("ERROR：")
        lines.extend(f"  - {item}" for item in report["errors"])
    else:
        lines.append("ERROR：无")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="检查一篇生物学名人系列文章")
    parser.add_argument("file", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = analyze(args.file.read_text(encoding="utf-8"), base_dir=args.file.parent)
    if args.json:
        json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(format_report(report))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
