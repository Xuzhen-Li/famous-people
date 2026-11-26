#!/usr/bin/env python3
# Read the public part of an ORCID record: names, education, employment, funding, work count.
#
#   python3 orcid_record.py --orcid 0000-0000-0000-0000 --out work/jane-roe/orcid.md
#
# Only items the owner made public are returned by the public API. An empty record is common and
# says nothing about the person: mark every missing item as unknown and use another source.
# Never guess an ORCID: the checksum below only catches typing errors, not wrong people.

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import die, fetch_json, now_stamp, run, sha256_bytes, write_new

API = "https://pub.orcid.org/v3.0/"


def checksum_ok(orcid):
    # ISO 7064 mod 11-2, as used by ORCID.
    digits = orcid.replace("-", "")
    if not re.match(r"^\d{15}[\dX]$", digits):
        return False
    total = 0
    for ch in digits[:-1]:
        total = (total + int(ch)) * 2
    check = (12 - total % 11) % 11
    return digits[-1] == ("X" if check == 10 else str(check))


def year_of(d):
    if not d:
        return ""
    y = (d.get("year") or {}).get("value")
    return y or ""


def summaries(group_block):
    out = []
    for g in (group_block or {}).get("affiliation-group", []):
        for s in g.get("summaries", []):
            for v in s.values():
                out.append(v)
    return out


def main():
    ap = argparse.ArgumentParser(description="Public ORCID record reader")
    ap.add_argument("--orcid", required=True)
    ap.add_argument("--out", required=True, help="new Markdown file")
    args = ap.parse_args()
    oid = args.orcid.strip().replace("https://orcid.org/", "")
    if not checksum_ok(oid):
        die("not a valid ORCID checksum: " + oid)
    rec, raw, final = fetch_json(API + oid + "/record")
    person = rec.get("person") or {}
    name = person.get("name") or {}
    full = " ".join(x for x in [(name.get("given-names") or {}).get("value"),
                                (name.get("family-name") or {}).get("value")] if x)
    act = rec.get("activities-summary") or {}
    lines = ["# ORCID public record: %s (%s)" % (full or "name not public", oid), "",
             "- Source: " + final, "- Fetched: " + now_stamp(), "- sha256 of reply: " + sha256_bytes(raw),
             "- Last modified (ms since epoch, from the record history): %s" % (
                 ((rec.get("history") or {}).get("last-modified-date") or {}).get("value", "unknown")), ""]
    for label, key in (("Education", "educations"), ("Qualifications", "qualifications"),
                       ("Employment", "employments"), ("Invited positions", "invited-positions"),
                       ("Distinctions", "distinctions"), ("Memberships", "memberships")):
        items = summaries(act.get(key))
        lines.append("## %s (%d public items)" % (label, len(items)))
        for s in items:
            org = (s.get("organization") or {}).get("name", "unknown")
            lines.append("- %s | %s | %s to %s" % (s.get("role-title") or "role not stated", org,
                                                   year_of(s.get("start-date")) or "?",
                                                   year_of(s.get("end-date")) or "present or not stated"))
        if not items:
            lines.append("- none public: unknown")
        lines.append("")
    funds = (act.get("fundings") or {}).get("group", [])
    lines.append("## Funding (%d public groups)" % len(funds))
    for g in funds:
        for s in g.get("funding-summary", []):
            lines.append("- %s | %s | %s to %s" % ((s.get("title") or {}).get("title", {}).get("value", "untitled"),
                                                   (s.get("organization") or {}).get("name", "unknown"),
                                                   year_of(s.get("start-date")) or "?",
                                                   year_of(s.get("end-date")) or "?"))
    if not funds:
        lines.append("- none public: unknown")
    lines += ["", "## Works", "- Public work groups: %d" % len((act.get("works") or {}).get("group", [])), ""]
    write_new(args.out, "\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    run(main)
