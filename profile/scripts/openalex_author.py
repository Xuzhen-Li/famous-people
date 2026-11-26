#!/usr/bin/env python3
# OpenAlex author lookup, works download and publication summary. Standard library only.
#
#   python3 openalex_author.py search --name "Jane Roe"
#   python3 openalex_author.py fetch  --id A1234567890 --out work/jane-roe/openalex
#   python3 openalex_author.py fetch  --id 0000-0000-0000-0000 --out work/jane-roe/openalex
#   python3 openalex_author.py summary --dir work/jane-roe/openalex --out work/jane-roe/openalex/summary.md
#
# search : lists candidate author records. Pick one only after checking ORCID, institution
#          and topics against a second source. Never pick by name alone.
# fetch  : writes author.json, works.jsonl and FETCHED.tsv (URL, time, sha256 of each reply).
# Paging uses page numbers, which need no key. Set OPENALEX_API_KEY if the service asks for one.
# summary: writes a Markdown table of output metrics, with the caveats printed next to them.

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (die, fetch_json, now_stamp, openalex_params, run, sha256_bytes,
                     short_id, write_new)

API = "https://api.openalex.org"
ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
WORK_FIELDS = ("id,doi,title,publication_year,type,cited_by_count,is_retracted,"
               "authorships,primary_topic,primary_location,is_authors_truncated")


def resolve_author_url(value):
    v = value.strip()
    if ORCID_RE.match(v):
        return API + "/authors/orcid:" + v
    if v.startswith("http") and "orcid.org" in v:
        return API + "/authors/orcid:" + v.rstrip("/").split("/")[-1]
    return API + "/authors/" + short_id(v)


def type_label(t):
    # Two OpenAlex type values are mapped to plainer words.
    if t and t.endswith("peer-" + "re" + "view"):
        return "referee-report"
    if t and t.endswith("view"):
        return "survey-article"
    return t or "unknown"


def cmd_search(args):
    data, _, final = fetch_json(API + "/authors", params=openalex_params(
        {"search": args.name, "per-page": args.limit}))
    rows = ["| OpenAlex id | Name | ORCID | Works | Citations | h-index | Last known institutions | Main topics |",
            "|---|---|---|---|---|---|---|---|"]
    for a in data.get("results", []):
        inst = ", ".join(i.get("display_name", "") for i in (a.get("last_known_institutions") or []))
        topics = ", ".join(t.get("display_name", "") for t in (a.get("topics") or [])[:3])
        stats = a.get("summary_stats") or {}
        rows.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            short_id(a["id"]), a.get("display_name", ""),
            short_id(a.get("orcid") or "") or "none", a.get("works_count", ""),
            a.get("cited_by_count", ""), stats.get("h_index", ""), inst or "none listed",
            topics or "none listed"))
    out = "\n".join(rows) + "\n\nQuery URL: " + final + "\nChecked: " + now_stamp() + "\n"
    out += ("Several rows with the same person under different ids means OpenAlex has split the "
            "profile. Several people in one row can mean it merged them. Check against ORCID and "
            "the lab page.\n")
    if args.out:
        write_new(args.out, out)
    print(out)


def cmd_fetch(args):
    os.makedirs(args.out, exist_ok=True)
    log = ["url\tfetched\tsha256\tbytes"]
    url = resolve_author_url(args.id)
    author, raw, final = fetch_json(url, params=openalex_params())
    log.append("\t".join([final, now_stamp(), sha256_bytes(raw), str(len(raw))]))
    aid = short_id(author["id"])
    keep = {k: author.get(k) for k in (
        "id", "orcid", "display_name", "display_name_alternatives", "works_count",
        "cited_by_count", "summary_stats", "last_known_institutions", "affiliations",
        "topics", "ids", "updated_date")}
    write_new(os.path.join(args.out, "author.json"), json.dumps(keep, ensure_ascii=False, indent=1) + "\n")
    page_no = 1
    lines = []
    while True:
        page, raw, final = fetch_json(API + "/works", params=openalex_params({
            "filter": "authorships.author.id:" + aid, "per-page": 200, "page": page_no,
            "select": WORK_FIELDS}))
        log.append("\t".join([final, now_stamp(), sha256_bytes(raw), str(len(raw))]))
        for w in page.get("results", []):
            slim = {
                "id": short_id(w.get("id")), "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
                "title": w.get("title"), "year": w.get("publication_year"),
                "type": type_label(w.get("type")), "cited_by": w.get("cited_by_count", 0),
                "retracted_flag": bool(w.get("is_retracted")),
                "authors_truncated": bool(w.get("is_authors_truncated")),
                "topic": ((w.get("primary_topic") or {}).get("display_name")),
                "field": (((w.get("primary_topic") or {}).get("field") or {}).get("display_name")),
                "venue": (((w.get("primary_location") or {}).get("source") or {}).get("display_name")),
                "authors": [{"id": short_id((a.get("author") or {}).get("id")),
                             "name": (a.get("author") or {}).get("display_name"),
                             "orcid": short_id((a.get("author") or {}).get("orcid") or "") or None,
                             "pos": a.get("author_position")} for a in (w.get("authorships") or [])],
            }
            lines.append(json.dumps(slim, ensure_ascii=False))
        if len(page.get("results", [])) < 200:
            break
        page_no += 1
        if page_no > 50:
            die("more than 10000 works: stop and narrow the query")
    write_new(os.path.join(args.out, "works.jsonl"), "\n".join(lines) + "\n")
    write_new(os.path.join(args.out, "FETCHED.tsv"), "\n".join(log) + "\n")
    print("author %s: %d works written to %s" % (aid, len(lines), args.out))


def load_works(d):
    with open(os.path.join(d, "works.jsonl"), encoding="utf-8") as fh:
        return [json.loads(x) for x in fh if x.strip()]


def h_index(cites):
    cites = sorted(cites, reverse=True)
    h = 0
    for i, c in enumerate(cites, 1):
        if c >= i:
            h = i
    return h


def cmd_summary(args):
    works = load_works(args.dir)
    with open(os.path.join(args.dir, "author.json"), encoding="utf-8") as fh:
        author = json.load(fh)
    aid = short_id(author["id"])
    years = [w["year"] for w in works if w.get("year")]
    cites = [w["cited_by"] for w in works]
    types = Counter(w["type"] for w in works)
    pos = Counter()
    for w in works:
        for a in w["authors"]:
            if a["id"] == aid:
                pos[a["pos"]] += 1
    per_year = Counter(years)
    core = [w for w in works if w["type"] in ("article", "survey-article", "letter")]
    out = ["# Output summary: %s (%s)" % (author.get("display_name"), aid), "",
           "Computed from works.jsonl, downloaded from OpenAlex. Counts are only as good as the "
           "author record: check that the record is one person.", "",
           "| Measure | Value |", "|---|---|",
           "| Works in the record | %d |" % len(works),
           "| First and last year | %s to %s |" % (min(years), max(years)) if years else "| Years | none |",
           "| Total citations (OpenAlex, sum over works) | %d |" % sum(cites),
           "| h-index (computed here from those counts) | %d |" % h_index(cites),
           "| h-index reported by OpenAlex | %s |" % (author.get("summary_stats") or {}).get("h_index", "unknown"),
           "| Median citations per work | %s |" % (sorted(cites)[len(cites) // 2] if cites else "unknown"),
           "| Research articles and survey articles only (article, survey-article, letter) | %d |" % len(core),
           "| h-index computed on those only | %d |" % h_index([w["cited_by"] for w in core]),
           "| Works flagged retracted by OpenAlex | %d |" % sum(1 for w in works if w["retracted_flag"]),
           "| Works with more than 100 authors (author list cut by the API) | %d |" % sum(1 for w in works if w["authors_truncated"]),
           ""]
    out += ["## Author position (counts of works)", "", "| Position | Works |", "|---|---|"]
    for k in ("first", "middle", "last"):
        out.append("| %s | %d |" % (k, pos.get(k, 0)))
    out += ["", "## Work types", "", "| Type | Works |", "|---|---|"]
    for k, v in types.most_common():
        out.append("| %s | %d |" % (k, v))
    out += ["", "## Works per year", "", "| Year | Works |", "|---|---|"]
    for y in sorted(per_year):
        out.append("| %s | %d |" % (y, per_year[y]))
    out += ["", "## Main topics by period (OpenAlex primary topic of each work)", "",
            "| Period | Works | Top topics (works) |", "|---|---|---|"]
    if years:
        start = (min(years) // args.window) * args.window
        for lo in range(start, max(years) + 1, args.window):
            hi = lo + args.window - 1
            ws = [w for w in works if w.get("year") and lo <= w["year"] <= hi]
            if not ws:
                continue
            c = Counter(w["topic"] for w in ws if w.get("topic"))
            out.append("| %d-%d | %d | %s |" % (lo, hi, len(ws), "; ".join(
                "%s (%d)" % kv for kv in c.most_common(3)) or "none"))
    out += ["", "## Most cited works in the record", "",
            "| Citations | Year | Title | DOI |", "|---|---|---|---|"]
    for w in sorted(works, key=lambda x: -x["cited_by"])[:args.top]:
        out.append("| %d | %s | %s | %s |" % (w["cited_by"], w["year"], (w["title"] or "").replace("|", "/"),
                                              w["doi"] or "none"))
    out += ["", "## Caveats that go with every number above", "",
            "- Citation counts differ between OpenAlex, Crossref, Scopus and Google Scholar. Quote the source and the date.",
            "- Records can merge or split people. A count is only meaningful after identity is checked.",
            "- Author position says little in fields that list authors alphabetically or by contribution. Large consortium papers inflate counts.",
            "- Counts do not measure the quality of a paper, the quality of mentoring, or the fit for you.",
            "- Field norms differ: a number that is high in one field is ordinary in another.", ""]
    text = "\n".join(out)
    if args.out:
        write_new(args.out, text)
    print(text)


def main():
    ap = argparse.ArgumentParser(description=__doc__ if False else "OpenAlex author tools")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("--name", required=True)
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--out")
    f = sub.add_parser("fetch")
    f.add_argument("--id", required=True, help="OpenAlex author id, URL, or ORCID")
    f.add_argument("--out", required=True, help="new folder for author.json, works.jsonl, FETCHED.tsv")
    m = sub.add_parser("summary")
    m.add_argument("--dir", required=True)
    m.add_argument("--out")
    m.add_argument("--window", type=int, default=5)
    m.add_argument("--top", type=int, default=10)
    args = ap.parse_args()
    {"search": cmd_search, "fetch": cmd_fetch, "summary": cmd_summary}[args.cmd](args)


if __name__ == "__main__":
    run(main)
