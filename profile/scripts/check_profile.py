#!/usr/bin/env python3
# Mechanical check of a finished profile (English or Chinese template).
#
#   python3 check_profile.py work/jane-roe/PROFILE.md
#
# ERROR  : fix before sharing.   WARN : read it and decide.
# What it checks:
#   1. Sections 0 to 17 are present, in the order the template gives.
#   2. In sections 0 to 13, every bullet and table row carries a source tag like [S3], or says
#      unknown / 未知 / not checked / 未查.
#   3. Every tag used is defined in section 17 with a URL or DOI and a fetch date (YYYY-MM-DD).
#   4. Mentoring items in section 8 are labelled Signal / 信号; background items in section 9 are
#      labelled Self-stated / Reported by (自述 / 报道); reaction items in section 11 are labelled
#      Formal / Press / Community / Reaction (正式 / 报道 / 社区 / 反应).
#   5. No placeholders left (angle brackets, TODO).
#   6. Private-life wording (home address, family, health, religion, politics, pay), personal
#      e-mail domains, and phone numbers. These are not allowed in a profile of a researcher.
#   7. Loaded wording about records and conduct (WARN).
# It cannot tell whether a source really says what the line says. Read the sources.

import re
import sys

HEAD = re.compile(r"^##\s+(\d+)\.\s")
TAG = re.compile(r"\[S(\d+)\]")
SRC_ROW = re.compile(r"^\|\s*S(\d+)\s*\|(.*)$")
DATE = re.compile(r"\b(19|20)\d\d-\d\d-\d\d\b")
URLISH = re.compile(r"(https?://\S+|doi:\s*10\.\d{4,9}/\S+|10\.\d{4,9}/\S+)", re.I)
UNKNOWN = re.compile(r"unknown|not checked|not found on|未知|未查|未找到", re.I)
PLACEHOLDER = re.compile(r"<[^>\n]{2,60}>|TODO|TBD|待填")
PRIVATE = re.compile(
    r"home address|residential address|家庭住址|住址|家庭地址|spouse|\bwife\b|\bhusband\b|配偶|妻子|丈夫|"
    r"\bchildren\b|\bson\b|\bdaughter\b|子女|儿子|女儿|divorce|离婚|religio|宗教|political party|党派|"
    r"\bsalary\b|薪水|工资|diagnos|illness|疾病|病情", re.I)
PERSONAL_MAIL = re.compile(r"[\w.+-]+@(gmail|googlemail|outlook|hotmail|live|yahoo|qq|163|126|sina|icloud|protonmail|foxmail)\.", re.I)
PHONE = re.compile(r"(\+\d{1,3}[\s-]?\(?\d{1,4}\)?[\s-]?\d{3,4}[\s-]?\d{3,4})|(\(\d{3}\)\s?\d{3}-\d{4})|(\b\d{3}-\d{3}-\d{4}\b)")
LOADED = re.compile(r"\bfraud|\bfake\b|scandal|\bcheat|misconduct|\btoxic|abusive|\bbully|造假|欺诈|丑闻|恶劣|学术不端", re.I)


def main():
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit("usage: check_profile.py PROFILE.md\nChecks section order, source tags, dates and labels. Exit 1 on errors.")
    with open(sys.argv[1], encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    errors, warns = [], []
    section = None
    seen = []
    used = {}
    defined = {}
    table_head_pending = False
    for no, line in enumerate(lines, 1):
        m = HEAD.match(line)
        if m:
            section = int(m.group(1))
            seen.append(section)
            continue
        if PLACEHOLDER.search(line) and "```" not in line and not line.lstrip().startswith(">"):
            errors.append("%d: placeholder left in text: %s" % (no, PLACEHOLDER.search(line).group(0)))
        if PRIVATE.search(line):
            errors.append("%d: private-life wording, not allowed in a profile: %s" % (no, PRIVATE.search(line).group(0)))
        if PERSONAL_MAIL.search(line):
            errors.append("%d: personal e-mail address; use the institutional contact page" % no)
        if section is not None and section <= 13 and PHONE.search(line):
            warns.append("%d: looks like a phone number; keep only numbers the lab or institution publishes for enquiries" % no)
        if LOADED.search(line) and section in (8, 9, 10, 11, 13):
            warns.append("%d: loaded word near a record or conduct item; state the source text instead: %s" % (no, LOADED.search(line).group(0)))
        if section == 17:
            sm = SRC_ROW.match(line)
            if sm:
                n = int(sm.group(1))
                body = sm.group(2)
                defined[n] = no
                if not URLISH.search(body):
                    errors.append("%d: S%d has no URL or DOI" % (no, n))
                if not DATE.search(body):
                    errors.append("%d: S%d has no fetch date (YYYY-MM-DD)" % (no, n))
            continue
        if section is None or section > 13:
            continue
        for t in TAG.findall(line):
            used.setdefault(int(t), no)
        stripped = line.strip()
        if not stripped or stripped.startswith(">") or stripped.startswith("#"):
            continue
        if stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if all(re.match(r"^:?-{2,}:?$", c) for c in cells if c):
                continue
            nxt = lines[no] if no < len(lines) else ""
            if nxt.strip().startswith("|") and re.match(r"^\|\s*:?-{2,}", nxt.strip()):
                continue
        elif not stripped.startswith(("- ", "* ")) and not re.match(r"^\d+\.\s", stripped):
            continue
        if not TAG.search(line) and not UNKNOWN.search(line):
            errors.append("%d: claim without a source tag or an unknown mark: %s" % (no, stripped[:80]))
        if section == 8 and stripped.startswith(("- ", "* ")) and not re.search(r"signal|信号", stripped, re.I) and not UNKNOWN.search(stripped):
            errors.append("%d: mentoring item not labelled Signal / 信号: %s" % (no, stripped[:80]))
        if section == 9 and stripped.startswith(("- ", "* ")) and not re.search(r"self-stated|reported by|自述|报道", stripped, re.I) and not UNKNOWN.search(stripped):
            errors.append("%d: background item not labelled Self-stated / Reported by (自述 / 报道): %s" % (no, stripped[:80]))
        if section == 11 and stripped.startswith(("- ", "* ")) and not re.search(r"formal|press|community|reaction|正式|报道|社区|反应", stripped, re.I) and not UNKNOWN.search(stripped):
            errors.append("%d: reaction item not labelled Formal / Press / Community / Reaction (正式 / 报道 / 社区 / 反应): %s" % (no, stripped[:80]))
    expected = list(range(0, 18))
    if seen != expected:
        errors.append("sections found %s, expected 0 to 17 in order" % seen)
    for n, no in sorted(used.items()):
        if n not in defined:
            errors.append("%d: [S%d] is used but not defined in section 17" % (no, n))
    for n, no in sorted(defined.items()):
        if n not in used:
            warns.append("%d: S%d is defined but never cited" % (no, n))
    for e in errors:
        print("ERROR " + e)
    for w in warns:
        print("WARN  " + w)
    print("%d errors, %d warnings" % (len(errors), len(warns)))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
