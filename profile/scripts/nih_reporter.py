#!/usr/bin/env python3
# NIH RePORTER lookup of US federal (NIH) grants for a principal investigator.
#
#   python3 nih_reporter.py find --last Roe --first Jane          # list candidate PI profiles
#   python3 nih_reporter.py grants --profile-id 1234567 --out work/jane-roe/nih_grants.tsv
#
# Covers NIH only. Other funders (NSF, DOE, UKRI, ERC, NSFC and so on) need their own look-up;
# see SOURCES.md. A name search can match several people: use the profile id.
# Award amounts are per fiscal year and can include sub-projects or shared cores.
# Do not add them up and call the total the lab budget.

import argparse
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import die, fetch_json, now_stamp, run, write_new

API = "https://api.reporter.nih.gov/v2/projects/search"
FIELDS = ["ProjectNum", "ProjectTitle", "FiscalYear", "AwardAmount", "Organization",
          "PrincipalInvestigators", "ProjectStartDate", "ProjectEndDate", "ActivityCode"]


def post(criteria, offset=0, limit=500):
    body = json.dumps({"criteria": criteria, "include_fields": FIELDS, "offset": offset,
                       "limit": limit}).encode("utf-8")
    data, _, _ = fetch_json(API, data=body, headers={"Content-Type": "application/json"})
    return data


def core_number(num):
    # 5U54AI170792-05 -> U54AI170792 (drop the leading type digit and the year suffix)
    core = (num or "").split("-")[0]
    return core[1:] if core[:1].isdigit() else core


def cmd_find(args):
    data = post({"pi_names": [{"last_name": args.last, "first_name": args.first}]}, limit=500)
    seen = defaultdict(lambda: {"n": 0, "orgs": set()})
    for r in data.get("results", []):
        for pi in r.get("principal_investigators") or []:
            if (pi.get("last_name") or "").lower() == args.last.lower():
                k = (pi.get("profile_id"), pi.get("full_name"))
                seen[k]["n"] += 1
                seen[k]["orgs"].add((r.get("organization") or {}).get("org_name") or "")
    print("| profile id | name on awards | award records | organizations |")
    print("|---|---|---|---|")
    for (pid, nm), v in sorted(seen.items(), key=lambda kv: -kv[1]["n"]):
        v["orgs"].discard("")
        print("| %s | %s | %d | %s |" % (pid, nm, v["n"], "; ".join(sorted(v["orgs"]))))
    print("\nTotal records returned: %s. Checked %s." % (data["meta"].get("total"), now_stamp()))


def cmd_grants(args):
    rows, offset = [], 0
    while True:
        data = post({"pi_profile_ids": [int(args.profile_id)]}, offset=offset)
        res = data.get("results", [])
        rows += res
        offset += len(res)
        if not res or offset >= data["meta"].get("total", 0):
            break
    projects = defaultdict(lambda: {"years": set(), "title": "", "org": "", "n": 0, "amount": 0, "codes": set()})
    for r in rows:
        p = projects[core_number(r.get("project_num"))]
        p["years"].add(r.get("fiscal_year"))
        p["title"] = r.get("project_title") or p["title"]
        p["org"] = (r.get("organization") or {}).get("org_name") or p["org"]
        p["n"] += 1
        p["amount"] += r.get("award_amount") or 0
        p["codes"].add((r.get("activity_code") or ""))
    lines = ["core_project\tactivity_codes\tfirst_fy\tlast_fy\tfy_records\torganization(latest)\ttitle(latest)\tsum_of_award_amounts_usd"]
    for core, p in sorted(projects.items(), key=lambda kv: (min(y for y in kv[1]["years"] if y), kv[0])):
        yrs = sorted(y for y in p["years"] if y)
        lines.append("\t".join([core, "/".join(sorted(c for c in p["codes"] if c)), str(yrs[0]), str(yrs[-1]),
                                str(p["n"]), p["org"], (p["title"] or "").replace("\t", " "), str(p["amount"])]))
    write_new(args.out, "\n".join(lines) + "\n")
    print("profile %s: %d award records, %d core projects. Checked %s." % (
        args.profile_id, len(rows), len(projects), now_stamp()))
    print("The sum column adds fiscal-year records and can double count shared cores: read it as a rough size only.")
    print("TSV written to " + args.out)


def main():
    ap = argparse.ArgumentParser(description="NIH RePORTER helper")
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("find")
    f.add_argument("--last", required=True)
    f.add_argument("--first", required=True)
    g = sub.add_parser("grants")
    g.add_argument("--profile-id", required=True)
    g.add_argument("--out", required=True)
    args = ap.parse_args()
    {"find": cmd_find, "grants": cmd_grants}[args.cmd](args)


if __name__ == "__main__":
    run(main)
