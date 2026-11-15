#!/usr/bin/env python3
"""Pull public, professional data on one researcher into a markdown appendix.

Sources (public APIs, no key needed):
  OpenAlex   https://api.openalex.org   works, citations, coauthors, venues, institutions
  NIH RePORTER https://api.reporter.nih.gov  NIH grants where the person is a PI (US only)

Usage:
  python3 scripts/background_data.py --orcid 0000-0001-9161-999X \
      --nih "Doudna,Jennifer" --out work/doudna/data.md
  python3 scripts/background_data.py --openalex A5067184382 --out work/x/data.md

It writes only professional output data. It never looks up addresses, family or health.
The output file must not exist yet.
"""
import argparse
import collections
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request

UA = {"User-Agent": "famous-people-background/1.0 (mailto:example@example.org)"}


def get_json(url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = dict(UA)
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if body else "GET")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def openalex_author(openalex_id=None, orcid=None):
    if orcid:
        return get_json(f"https://api.openalex.org/authors/orcid:{orcid}")
    return get_json(f"https://api.openalex.org/authors/{openalex_id}")


def openalex_works(author_id, sort, n):
    q = urllib.parse.urlencode({"filter": f"author.id:{author_id}", "sort": sort,
                                "per-page": n,
                                "select": "id,doi,title,publication_year,cited_by_count,primary_location,authorships,type"})
    return get_json(f"https://api.openalex.org/works?{q}")["results"]


def nih_grants(last, first):
    body = {"criteria": {"pi_names": [{"last_name": last, "first_name": first}]},
            "include_fields": ["CoreProjectNum", "ProjectTitle", "FiscalYear", "AwardAmount",
                               "Organization", "ActivityCode"],
            "limit": 500, "sort_field": "fiscal_year", "sort_order": "desc"}
    return get_json("https://api.reporter.nih.gov/v2/projects/search", body)["results"]


def summarize_coauthors(works, self_id, top=15):
    c = collections.Counter()
    names = {}
    for w in works:
        for a in w.get("authorships") or []:
            aid = (a.get("author") or {}).get("id")
            if aid and aid != self_id:
                c[aid] += 1
                names[aid] = a["author"].get("display_name")
    return [(names[k], v, k) for k, v in c.most_common(top)]


def summarize_venues(works, top=10):
    c = collections.Counter()
    for w in works:
        src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name")
        if src:
            c[src] += 1
    return c.most_common(top)


def group_grants(rows):
    g = collections.OrderedDict()
    for r in rows:
        k = r.get("core_project_num")
        e = g.setdefault(k, {"title": r.get("project_title"), "years": set(), "total": 0,
                              "org": (r.get("organization") or {}).get("org_name"),
                              "activity": r.get("activity_code")})
        e["years"].add(r.get("fiscal_year"))
        e["total"] += r.get("award_amount") or 0
    return g


def render(author, top_cited, recent, coauthors, venues, grants, today):
    L = []
    L.append(f"# Data appendix: {author['display_name']}")
    L.append("")
    L.append(f"Retrieved {today} from OpenAlex ({author['id']}) and NIH RePORTER. "
             "Counts come from those two databases; other databases give different numbers.")
    L.append("")
    s = author.get("summary_stats") or {}
    L.append("## Output")
    L.append("")
    L.append(f"- Works in OpenAlex: {author.get('works_count')}")
    L.append(f"- Citations in OpenAlex: {author.get('cited_by_count')}")
    L.append(f"- h-index (OpenAlex): {s.get('h_index')}")
    if author.get("orcid"):
        L.append(f"- ORCID: {author['orcid']}")
    insts = [i.get("display_name") for i in author.get("last_known_institutions") or []]
    if insts:
        L.append(f"- Last known institutions (OpenAlex): {'; '.join(insts)}")
    L.append("")
    L.append("A yearly citation count of 0 in early years can be missing data rather than zero citations; check before using it.")
    L.append("")
    L.append("| Year | Works | Citations received |")
    L.append("| --- | --- | --- |")
    for y in sorted(author.get("counts_by_year") or [], key=lambda r: -r["year"]):
        L.append(f"| {y['year']} | {y['works_count']} | {y['cited_by_count']} |")
    L.append("")
    for title, ws in (("Most cited works", top_cited), ("Most recent works", recent)):
        L.append(f"## {title}")
        L.append("")
        L.append("| Year | Title | Venue | Cited by | DOI |")
        L.append("| --- | --- | --- | --- | --- |")
        for w in ws:
            src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
            t = (w.get("title") or "").replace("|", "/")
            L.append(f"| {w.get('publication_year')} | {t} | {src} | {w.get('cited_by_count')} | {w.get('doi') or ''} |")
        L.append("")
    L.append("## Frequent coauthors (in the works sampled above)")
    L.append("")
    for name, n, aid in coauthors:
        L.append(f"- {name}: {n} ({aid})")
    L.append("")
    L.append("## Frequent venues (same sample)")
    L.append("")
    for v, n in venues:
        L.append(f"- {v}: {n}")
    L.append("")
    if grants is not None:
        L.append("## NIH grants as PI (NIH RePORTER)")
        L.append("")
        L.append("Rows are grouped by core project number. The title is the latest row's title, so for "
                 "multi-project awards (P01, U19, U54) it can be a sub-project or core where this person "
                 "is the listed PI. Totals add the rows returned and are not the full award.")
        L.append("")
        L.append("| Core project | Activity | Fiscal years | Total awarded (USD, summed rows) | Organization | Title |")
        L.append("| --- | --- | --- | --- | --- | --- |")
        for k, e in grants.items():
            ys = sorted(y for y in e["years"] if y)
            span = f"{ys[0]}-{ys[-1]}" if ys else ""
            L.append(f"| {k} | {e['activity']} | {span} | {e['total']:,} | {e['org']} | {(e['title'] or '').replace('|', '/')} |")
        L.append("")
    return "\n".join(L) + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--orcid")
    g.add_argument("--openalex", help="OpenAlex author id, e.g. A5067184382")
    p.add_argument("--nih", help="'Last,First' to search NIH RePORTER as PI")
    p.add_argument("--sample", type=int, default=200, help="recent works used for coauthor/venue counts")
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    if os.path.exists(a.out):
        p.error(f"{a.out} exists; not overwriting")
    author = openalex_author(a.openalex, a.orcid)
    aid = author["id"].rsplit("/", 1)[-1]
    top = openalex_works(aid, "cited_by_count:desc", 10)
    recent = openalex_works(aid, "publication_date:desc", 10)
    sample = openalex_works(aid, "publication_date:desc", min(a.sample, 200))
    grants = None
    if a.nih:
        last, first = [x.strip() for x in a.nih.split(",", 1)]
        grants = group_grants(nih_grants(last, first))
    today = dt.date.today().isoformat()
    text = render(author, top, recent, summarize_coauthors(sample, author["id"]),
                  summarize_venues(sample), grants, today)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "x", encoding="utf-8") as f:
        f.write(text)
    print(a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
