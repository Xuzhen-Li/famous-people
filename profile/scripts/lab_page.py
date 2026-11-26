#!/usr/bin/env python3
# Turn a public lab "people" page into counts you can cite: current members by role, alumni by
# listed next position, time in lab, and join announcements by year.
#
#   python3 lab_page.py --url https://example.org/people/ --save-html work/jane-roe/lab_people.html --out work/jane-roe/lab_people.md
#   python3 lab_page.py --file work/jane-roe/lab_people.html --out work/jane-roe/lab_people.md
#
# Rules built in:
#   - A URL is fetched only if robots.txt allows it, once, with an honest user agent.
#   - No login, no cookies, no pages behind a sign-in or a security check.
#   - Names of trainees are left out of the output unless you add --names. The subject of a
#     profile is the researcher, not the students. Counts are enough to answer the questions.
#   - Everything is a count of what the page lists. A page can be out of date, and a missing
#     alumnus is not evidence of anything.

import argparse
import os
import re
import sys
import urllib.parse
import urllib.robotparser
from collections import Counter, OrderedDict
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import die, fetch, now_stamp, run, sha256_bytes, user_agent, write_new

VOID = {"br", "img", "input", "meta", "link", "hr", "source", "area", "base", "col", "embed", "wbr"}
ROW_CLASS = re.compile(r"(^|[_-])(tr|row)$")
CELL_CLASS = re.compile(r"(^|[_-])(td|cell)$")
HEAD_ROW_CLASS = re.compile(r"(^|[_-])th$")
NAME_CLASS = re.compile(r"(^|[_-])(person|member|people|team|staff|profile|student|postdoc)[_-]*name$|^name$")
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
DATE_LINE = re.compile(r"^(%s) \d{1,2}, (\d{4})$" % MONTHS)
FACULTY = re.compile(r"\b(professor|lecturer|faculty|group leader|principal investigator|assistant prof|associate prof)\b", re.I)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.skip = 0
        self.heading = None
        self.in_head = False
        self.sections = OrderedDict()
        self.cards = OrderedDict()
        self.card = None
        self.row = None
        self.cell = None
        self.lines = []
        self.buf = ""

    def flush(self):
        t = " ".join(self.buf.split())
        if t:
            self.lines.append(t)
        self.buf = ""

    def role(self, tag, attrs):
        cls = (dict(attrs).get("class") or "").split()
        if tag == "tr" or any(ROW_CLASS.search(c) for c in cls):
            return "row"
        if any(HEAD_ROW_CLASS.search(c) for c in cls):
            return "cell" if self.row is not None else "row"
        if tag in ("td", "th") or any(CELL_CLASS.search(c) for c in cls):
            return "cell"
        if any(NAME_CLASS.search(c) for c in cls):
            return "card"
        return None

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag in VOID:
            if tag == "br":
                self.buf += " "
            return
        r = self.role(tag, attrs)
        self.stack.append((tag, r))
        if tag in ("h1", "h2", "h3", "h4"):
            self.flush()
            self.in_head = True
            self.heading_buf = ""
        if tag in ("p", "div", "li", "tr", "section", "h1", "h2", "h3", "h4"):
            self.flush()
        if r == "card":
            self.card = ""
        if r == "row":
            self.row = []
        if r == "cell" and self.row is not None:
            self.cell = ""

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1
        if tag in VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                role = self.stack[i][1]
                del self.stack[i:]
                break
        else:
            return
        if tag in ("h1", "h2", "h3", "h4"):
            self.in_head = False
            self.heading = " ".join(self.heading_buf.split())
            self.flush()
            self.lines.append("## " + self.heading)
            self.buf = ""
        if role == "card" and self.card is not None:
            nm = " ".join(self.card.split())
            lst = self.cards.setdefault(self.heading or "(no heading)", [])
            if nm and nm not in lst:
                lst.append(nm)
            self.card = None
        if role == "cell" and self.cell is not None and self.row is not None:
            self.row.append(" ".join(self.cell.split()))
            self.cell = None
        if role == "row" and self.row is not None:
            if any(self.row):
                self.sections.setdefault(self.heading or "(no heading)", []).append(self.row)
            self.row = None

    def handle_data(self, data):
        if self.skip:
            return
        if self.in_head:
            self.heading_buf += data
        if self.cell is not None:
            self.cell += data
        if self.card is not None:
            self.card += data
        self.buf += data


def parse(html):
    p = Page()
    p.feed(html)
    p.flush()
    return p


def tenure(rows):
    spans = []
    for r in rows:
        for c in r:
            m = re.match(r"^\s*(\d{4})\s*[-\u2013]\s*(\d{4})\s*$", c)
            if m and int(m.group(2)) >= int(m.group(1)):
                spans.append(int(m.group(2)) - int(m.group(1)))
                break
    return sorted(spans)


def render(p, names, counts_only=False):
    out = ["# Lab page counts", "", "Counts of what the page lists on the day it was read. A missing person or "
           "a blank cell is unknown, not a finding.", ""]
    for head, rows in p.sections.items():
        body = [r for r in rows]
        header = None
        if body and all(re.match(r"^(name|time in lab|position|location|years?|role|current)", c, re.I) or not c for c in body[0]):
            header = body[0]
            body = body[1:]
        out.append("## %s: %d listed" % (head, len(body)))
        if header:
            out.append("- Columns: " + " | ".join(header))
        spans = tenure(body)
        if spans:
            out.append("- Listed time in lab: %d entries with a year range; median %d years, range %d to %d years"
                       % (len(spans), spans[len(spans) // 2], spans[0], spans[-1]))
        if header and any(re.search(r"position|location|current", c, re.I) for c in header):
            idx = [i for i, c in enumerate(header) if re.search(r"position|location|current", c, re.I)][0]
            positions = [r[idx] if idx < len(r) else "" for r in body]
            blank = sum(1 for x in positions if not x.strip())
            fac = sum(1 for x in positions if FACULTY.search(x))
            out.append("- Next position listed: %d of %d; blank: %d" % (len(body) - blank, len(body), blank))
            out.append("- Of those listed, wording that names a faculty or group-leader post: %d (read the strings; the match is a keyword guess)" % fac)
            if not names and not counts_only:
                out.append("- Listed positions (names left out):")
                for x in sorted(set(x for x in positions if x.strip())):
                    out.append("  - " + x)
        if names:
            for r in body:
                out.append("  - " + " | ".join(r))
        out.append("")
    for head, nms in p.cards.items():
        out.append("## %s: %d person cards listed" % (head, len(nms)))
        if names:
            for n in nms:
                out.append("  - " + n)
        out.append("")
    joins = Counter()
    i = 0
    while i < len(p.lines) - 1:
        m = DATE_LINE.match(p.lines[i])
        if m and re.search(r"\bjoined|welcome", p.lines[i + 1], re.I):
            txt = p.lines[i + 1].lower()
            role = ("postdoc" if "postdoc" in txt else "graduate student" if "graduate student" in txt
                    else "staff" if "staff" in txt else "other")
            joins[(m.group(2), role)] += 1
        i += 1
    if joins:
        out += ["## Join announcements on the news list (announcements, not people: one can name several)", "",
                "| Year | Role | Announcements |", "|---|---|---|"]
        for (y, role), n in sorted(joins.items()):
            out.append("| %s | %s | %d |" % (y, role, n))
        out.append("")
    return "\n".join(out)


def robots_allows(url):
    parts = urllib.parse.urlsplit(url)
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url("%s://%s/robots.txt" % (parts.scheme, parts.netloc))
    try:
        rp.read()
    except Exception:
        return True
    return rp.can_fetch(user_agent(), url)


def main():
    ap = argparse.ArgumentParser(description="Public lab page counts")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--url")
    g.add_argument("--file")
    ap.add_argument("--save-html", help="new file for the raw HTML when --url is used")
    ap.add_argument("--out", required=True)
    ap.add_argument("--names", action="store_true", help="include names (default: left out)")
    ap.add_argument("--counts-only", action="store_true", help="also leave out the list of listed positions")
    args = ap.parse_args()
    meta = []
    if args.url:
        if not robots_allows(args.url):
            die("robots.txt does not allow this page: " + args.url)
        raw, final = fetch(args.url, headers={"Accept": "text/html"})
        if re.search(rb"(captcha|turnstile|security check|please sign in|log in to continue)", raw[:20000], re.I):
            die("the page looks like a sign-in or security check: do not go around it; use another source")
        meta += ["- Source: " + final, "- Fetched: " + now_stamp(), "- sha256 of page: " + sha256_bytes(raw)]
        if args.save_html:
            with open(args.save_html, "xb") as fh:
                fh.write(raw)
        html = raw.decode("utf-8", errors="replace")
    else:
        with open(args.file, "rb") as fh:
            raw = fh.read()
        meta += ["- File: " + args.file, "- sha256 of file: " + sha256_bytes(raw)]
        html = raw.decode("utf-8", errors="replace")
    text = render(parse(html), args.names, args.counts_only) + "\n" + "\n".join(meta) + "\n"
    write_new(args.out, text)
    print(text)


if __name__ == "__main__":
    run(main)
