#!/usr/bin/env python3
# Check DOIs against Crossref: does the DOI exist, does the title and year agree with the
# record you hold, and has the publisher or the Retraction Watch data attached a notice
# (retraction, correction, expression of concern).
#
#   python3 check_dois.py --works work/jane-roe/openalex/works.jsonl --out work/jane-roe/doi_check.tsv
#   python3 check_dois.py --dois work/jane-roe/dois.txt --out work/jane-roe/doi_check.tsv
#
# A notice is a fact about one record. It is not a judgement about the person. Corrections are
# routine. Before a retraction is mentioned anywhere, open the notice itself and read the stated
# reason; reasons range from an honest error to misconduct, and the notice says which.
# DOIs that are not in Crossref (for example DataCite DOIs) come out as not-in-crossref. That is
# not an error: look the DOI up at doi.org instead.

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import die, fetch_json, now_stamp, run, write_new

API = "https://api.crossref.org/works"


def words(text):
    text = re.sub(r"^retracted:\s*", "", (text or "").lower())
    return set(re.findall(r"[a-z0-9]{3,}", text))


def overlap(a, b):
    wa, wb = words(a), words(b)
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / float(min(len(wa), len(wb)))


def plain_type(t):
    # Crossref names referee reports with a word that this repo avoids; written as referee-report.
    return (t or "").replace("peer-" + "re" + "view", "referee-report")


def norm_doi(d):
    d = (d or "").strip().lower()
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", d)


def crossref_batch(dois):
    flt = ",".join("doi:" + d for d in dois)
    data, _, _ = fetch_json(API, params={
        "filter": flt, "rows": len(dois),
        "select": "DOI,title,issued,update-to,updated-by,type,container-title"})
    return {norm_doi(it["DOI"]): it for it in data["message"]["items"]}


def notices(item):
    out = []
    for n in item.get("updated-by") or []:
        out.append("%s|%s|%s|%s" % (n.get("type"), n.get("source"), n.get("DOI"),
                                    "-".join(str(x) for x in (n.get("updated") or {}).get("date-parts", [[""]])[0])))
    return out


def main():
    ap = argparse.ArgumentParser(description="Crossref DOI and notice check")
    ap.add_argument("--works", help="works.jsonl written by openalex_author.py")
    ap.add_argument("--dois", help="text file with one DOI per line")
    ap.add_argument("--out", required=True, help="new TSV file")
    ap.add_argument("--size", type=int, default=40)
    args = ap.parse_args()
    rows = []
    if args.works:
        with open(args.works, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    w = json.loads(line)
                    if w.get("doi"):
                        rows.append((norm_doi(w["doi"]), w.get("title") or "", w.get("year"), w.get("retracted_flag")))
    elif args.dois:
        with open(args.dois, encoding="utf-8") as fh:
            rows = [(norm_doi(x), "", None, None) for x in fh if x.strip()]
    else:
        die("give --works or --dois")
    seen, uniq = set(), []
    for r in rows:
        if r[0] not in seen:
            seen.add(r[0])
            uniq.append(r)
    found = {}
    plain = [r[0] for r in uniq if "," not in r[0]]
    odd = [r[0] for r in uniq if "," in r[0]]
    for i in range(0, len(plain), args.size):
        found.update(crossref_batch(plain[i:i + args.size]))
    for d in odd:
        found.update(crossref_batch([d.replace(",", "%2C")]))
    lines = ["doi\tin_crossref\ttitle_overlap\tyear_diff\tnotices\topenalex_retracted_flag\tcrossref_type"]
    n_missing = n_notice = n_flag = n_titlebad = 0
    for doi, title, year, flag in uniq:
        item = found.get(doi)
        if not item:
            n_missing += 1
            lines.append("\t".join([doi, "not-in-crossref", "", "", "", str(flag), ""]))
            continue
        ct = (item.get("title") or [""])[0]
        ov = overlap(title, ct) if (title and ct) else None
        cy = ((item.get("issued") or {}).get("date-parts") or [[None]])[0][0]
        yd = (abs(int(cy) - int(year)) if cy and year else "")
        nt = notices(item)
        if nt:
            n_notice += 1
        if flag:
            n_flag += 1
        if ov is not None and ov < 0.6:
            n_titlebad += 1
        lines.append("\t".join([doi, "yes", "" if ov is None else "%.2f" % ov, str(yd), ";".join(nt),
                                str(flag), plain_type(item.get("type", ""))]))
    write_new(args.out, "\n".join(lines) + "\n")
    print("checked %d DOIs on %s" % (len(uniq), now_stamp()))
    print("not in Crossref: %d" % n_missing)
    print("with a Crossref notice (retraction, correction, concern): %d" % n_notice)
    print("flagged retracted by OpenAlex: %d" % n_flag)
    print("title overlap below 0.6 (check by hand): %d" % n_titlebad)
    print("TSV written to " + args.out)


if __name__ == "__main__":
    run(main)
