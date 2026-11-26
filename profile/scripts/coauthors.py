#!/usr/bin/env python3
# Frequent co-authors and a small collaboration network from works.jsonl (see openalex_author.py).
#
#   python3 coauthors.py --dir work/jane-roe/openalex --out-dir work/jane-roe/network --top 25
#
# Writes coauthors.tsv (who, how many papers, first and last year, how often as first or last
# author) and edges.tsv plus network.dot (who among the top co-authors also publish together).
#
# Read the result as a list of leads, not as a verdict:
#   - Papers with more than --max-authors authors are left out of the counts. Large consortium
#     papers say little about a working relationship. The number left out is printed.
#   - The API cuts author lists longer than 100. Those papers are left out too.
#   - OpenAlex sometimes splits one person into two ids. Merge them by hand when you see the
#     same name twice, and say so in the profile.
#   - A frequent co-author is not necessarily a close collaborator, and a one-off co-author is not
#     necessarily a distant one.

import argparse
import itertools
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import die, run, short_id, write_new


def main():
    ap = argparse.ArgumentParser(description="Co-author counts and network")
    ap.add_argument("--dir", required=True, help="folder with author.json and works.jsonl")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--max-authors", type=int, default=25)
    ap.add_argument("--since", type=int, default=0, help="only papers from this year on")
    args = ap.parse_args()
    with open(os.path.join(args.dir, "author.json"), encoding="utf-8") as fh:
        me = short_id(json.load(fh)["id"])
    with open(os.path.join(args.dir, "works.jsonl"), encoding="utf-8") as fh:
        works = [json.loads(x) for x in fh if x.strip()]
    used = left_out = 0
    n = Counter()
    first = {}
    last = {}
    as_first = Counter()
    as_last = Counter()
    names = {}
    papers = []
    for w in works:
        if w["type"] in ("dataset", "erratum", "referee-report", "supplementary-materials", "conference-abstract"):
            continue
        if args.since and (w.get("year") or 0) < args.since:
            continue
        auth = w["authors"]
        if w["authors_truncated"] or len(auth) > args.max_authors:
            left_out += 1
            continue
        if not any(a["id"] == me for a in auth):
            continue
        used += 1
        ids = []
        mypos = [a["pos"] for a in auth if a["id"] == me][0]
        for a in auth:
            if a["id"] == me or not a["id"]:
                continue
            ids.append(a["id"])
            names[a["id"]] = a["name"]
            n[a["id"]] += 1
            y = w.get("year") or 0
            first[a["id"]] = min(first.get(a["id"], 9999), y)
            last[a["id"]] = max(last.get(a["id"], 0), y)
            if mypos == "last" and a["pos"] == "first":
                as_first[a["id"]] += 1
            if mypos == "first" and a["pos"] == "last":
                as_last[a["id"]] += 1
        papers.append(sorted(set(ids)))
    top = [i for i, _ in n.most_common(args.top)]
    lines = ["author_id\tname\tpapers_together\tfirst_year\tlast_year\tfirst_author_when_subject_is_last\tlast_author_when_subject_is_first"]
    for i in top:
        lines.append("\t".join([i, names[i], str(n[i]), str(first[i]), str(last[i]), str(as_first[i]), str(as_last[i])]))
    write_new(os.path.join(args.out_dir, "coauthors.tsv"), "\n".join(lines) + "\n")
    edges = Counter()
    topset = set(top)
    for p in papers:
        for a, b in itertools.combinations([x for x in p if x in topset], 2):
            edges[tuple(sorted((a, b)))] += 1
    elines = ["a\tb\tpapers_with_subject"]
    for (a, b), c in edges.most_common():
        elines.append("%s\t%s\t%d" % (names[a], names[b], c))
    write_new(os.path.join(args.out_dir, "edges.tsv"), "\n".join(elines) + "\n")
    dot = ["graph coauthors {", "  layout=neato; overlap=false; node [shape=ellipse, fontsize=10];",
           "  subject [label=\"subject\", shape=rect];"]
    for i in top:
        dot.append("  \"%s\" [label=\"%s\"];" % (i, names[i].replace("\"", "")))
        dot.append("  subject -- \"%s\" [penwidth=%.1f];" % (i, 0.5 + n[i] / 10.0))
    for (a, b), c in edges.items():
        dot.append("  \"%s\" -- \"%s\" [style=dashed];" % (a, b))
    dot.append("}")
    write_new(os.path.join(args.out_dir, "network.dot"), "\n".join(dot) + "\n")
    print("papers used: %d; left out for author count or cut list: %d; distinct co-authors: %d" % (used, left_out, len(n)))
    print("TSV and DOT written to " + args.out_dir)


if __name__ == "__main__":
    run(main)
