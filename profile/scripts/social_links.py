#!/usr/bin/env python3
# Find the public social-media and profile links that an official page gives, and read the public
# profile of an account that such a page links to. Public pages only. Standard library only.
#
#   python3 social_links.py page --url https://example.org/lab/ --out work/jane-roe/social_links.md
#   python3 social_links.py page --file work/jane-roe/lab.html --out work/jane-roe/social_links.md
#   python3 social_links.py mastodon --acct @name@instance.example --out work/jane-roe/mastodon.md
#   python3 social_links.py bluesky --handle name.bsky.social --out work/jane-roe/bluesky.md
#
# Rules built in:
#   - Only links that an official page (the lab page, the institution page) actually gives are
#     listed. A guessed account with the same name is never listed as the person.
#   - A URL is fetched only if robots.txt allows it. No login, no cookies, no private or locked
#     accounts, no pages behind a sign-in or a security check.
#   - The Mastodon and Bluesky lookups use the public profile endpoints only. They record the
#     bio, creation date, post count and date of the last post. They do not read the posts.
#   - X, Facebook, Instagram and LinkedIn need a sign-in to view: the script lists the link and
#     stops. Look by eye if you must, and write not checked when you could not.
#   - A link on an official page ties an account to the person or to the institution. Decide
#     which by reading the account. No link found is unknown, not proof that no account exists.

import argparse
import os
import re
import sys
import urllib.parse
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import die, fetch, fetch_json, now_stamp, run, sha256_bytes, write_new
from lab_page import robots_allows

PLATFORMS = [
    ("X", r"(^|\.)(x|twitter)\.com$"),
    ("Bluesky", r"(^|\.)bsky\.app$"),
    ("Mastodon or similar", r"(mastodon|genomic\.social|fosstodon|hachyderm|scholar\.social|sciences\.social|\.social$)"),
    ("LinkedIn", r"(^|\.)linkedin\.com$"),
    ("Facebook", r"(^|\.)facebook\.com$"),
    ("Instagram", r"(^|\.)instagram\.com$"),
    ("YouTube", r"(^|\.)(youtube\.com|youtu\.be)$"),
    ("GitHub", r"(^|\.)github\.com$"),
    ("Google Scholar", r"(^|\.)scholar\.google\."),
    ("ResearchGate", r"(^|\.)researchgate\.net$"),
    ("ORCID", r"(^|\.)orcid\.org$"),
    ("Weibo", r"(^|\.)weibo\.(com|cn)$"),
    ("Zhihu", r"(^|\.)zhihu\.com$"),
    ("WeChat", r"(^|\.)weixin\.qq\.com$"),
    ("Threads", r"(^|\.)threads\.net$"),
]
SIGN_IN_ONLY = {"X", "LinkedIn", "Facebook", "Instagram", "Threads"}
SHARE_PATH = re.compile(r"/(sharer|share|intent|dialog)\b", re.I)


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items = []
        self.cur = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            a = dict(attrs)
            if a.get("href"):
                self.cur = {"href": a["href"], "rel": a.get("rel") or "", "text": ""}

    def handle_data(self, data):
        if self.cur is not None:
            self.cur["text"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self.cur is not None:
            self.items.append(self.cur)
            self.cur = None


def platform_of(url):
    host = urllib.parse.urlsplit(url).netloc.lower()
    for name, pat in PLATFORMS:
        if re.search(pat, host):
            return name
    return None


def cmd_page(args):
    meta = []
    if args.url:
        if not robots_allows(args.url):
            die("robots.txt does not allow this page: " + args.url)
        raw, final = fetch(args.url, headers={"Accept": "text/html"})
        if re.search(rb"(captcha|turnstile|security check|please sign in|log in to continue)", raw[:20000], re.I):
            die("the page looks like a sign-in or security check: do not go around it")
        meta += ["- Source: " + final, "- Fetched: " + now_stamp(), "- sha256 of page: " + sha256_bytes(raw)]
        base = final
    else:
        with open(args.file, "rb") as fh:
            raw = fh.read()
        meta += ["- File: " + os.path.basename(args.file), "- sha256 of file: " + sha256_bytes(raw)]
        base = ""
    p = Links()
    p.feed(raw.decode("utf-8", errors="replace"))
    rows, seen = [], set()
    for it in p.items:
        url = urllib.parse.urljoin(base, it["href"].strip())
        name = platform_of(url)
        if not name or SHARE_PATH.search(url) or url in seen:
            continue
        seen.add(url)
        rel_me = "yes" if "me" in it["rel"].split() else "no"
        text = " ".join(it["text"].split())[:40] or "(no text)"
        rows.append((name, url, text, rel_me))
    out = ["# Social and profile links found on the page", "",
           "A link on an official page ties an account to the person or to the institution. Decide which by "
           "reading the account. Absence of a link is unknown, not proof that no account exists.", ""]
    if rows:
        out += ["| Platform | Address | Link text | rel=me |", "|---|---|---|---|"]
        for name, url, text, rel_me in rows:
            out.append("| %s | %s | %s | %s |" % (name, url, text.replace("|", "/"), rel_me))
        need = sorted({r[0] for r in rows if r[0] in SIGN_IN_ONLY})
        if need:
            out += ["", "Needs a sign-in to view, so not read by this script: " + ", ".join(need) + "."]
    else:
        out.append("No links to social or profile sites were found on this page: unknown.")
    out += [""] + meta
    text = "\n".join(out) + "\n"
    write_new(args.out, text)
    print(text)


def strip_html(s):
    return " ".join(re.sub(r"<[^>]+>", " ", s or "").replace("&amp;", "&").split())


def cmd_mastodon(args):
    m = re.match(r"^@?([\w.-]+)@([\w.-]+)$", args.acct.strip())
    if not m:
        die("use the form @name@instance.example")
    user, host = m.group(1), m.group(2)
    if not robots_allows("https://%s/api/v1/accounts/lookup" % host):
        die("robots.txt does not allow the lookup on " + host)
    data, raw, final = fetch_json("https://%s/api/v1/accounts/lookup" % host, params={"acct": user})
    fields = "; ".join("%s: %s" % (f.get("name"), strip_html(f.get("value"))) for f in data.get("fields", []))
    out = ["# Mastodon public profile: " + str(data.get("url")), "",
           "- Source: " + final,
           "- Fetched: " + now_stamp(),
           "- sha256 of reply: " + sha256_bytes(raw),
           "- Display name: " + str(data.get("display_name")),
           "- Bio: " + strip_html(data.get("note")),
           "- Linked fields: " + (fields or "none"),
           "- Account created: " + str(data.get("created_at")),
           "- Posts: %s; date of last post: %s" % (data.get("statuses_count"), data.get("last_status_at") or "no posts"),
           "- Automated account flag: " + str(data.get("bot")),
           "",
           "Not collected: followers, followed accounts and the posts themselves. Whether this account is the "
           "person must be shown by a link from an official page (rel=me or a plain link), not by the name.", ""]
    text = "\n".join(out)
    write_new(args.out, text)
    print(text)


def cmd_bluesky(args):
    handle = args.handle.strip().lstrip("@")
    data, raw, final = fetch_json("https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile", params={"actor": handle})
    out = ["# Bluesky public profile: https://bsky.app/profile/" + handle, "",
           "- Source: " + final,
           "- Fetched: " + now_stamp(),
           "- sha256 of reply: " + sha256_bytes(raw),
           "- Display name: " + str(data.get("displayName")),
           "- Bio: " + " ".join(str(data.get("description") or "").split()),
           "- Account created: " + str(data.get("createdAt") or data.get("indexedAt")),
           "- Posts: " + str(data.get("postsCount")),
           "",
           "Not collected: followers, followed accounts and the posts themselves. The account is the person only "
           "if an official page links to it.", ""]
    text = "\n".join(out)
    write_new(args.out, text)
    print(text)


def main():
    ap = argparse.ArgumentParser(description="Public social links and profiles")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("page")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--url")
    g.add_argument("--file")
    p.add_argument("--out", required=True)
    p.set_defaults(fn=cmd_page)
    m = sub.add_parser("mastodon")
    m.add_argument("--acct", required=True)
    m.add_argument("--out", required=True)
    m.set_defaults(fn=cmd_mastodon)
    b = sub.add_parser("bluesky")
    b.add_argument("--handle", required=True)
    b.add_argument("--out", required=True)
    b.set_defaults(fn=cmd_bluesky)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    run(main)
