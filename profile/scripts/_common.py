#!/usr/bin/env python3
# Shared helpers for the profile scripts. Standard library only.
# Every script here reads public sources only, never logs in, and never overwrites a file.

import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

BASE_UA = "famous-bio-profile/1.0 (public-source research script)"


def user_agent():
    # Set CONTACT_EMAIL in your own shell so site operators can reach you. Never commit it.
    mail = os.environ.get("CONTACT_EMAIL", "").strip()
    return BASE_UA + (" mailto:" + mail if mail else "")


def today():
    # Local date of the machine that runs the script, as YYYY-MM-DD.
    return datetime.now().astimezone().date().isoformat()


def now_stamp():
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def fetch(url, params=None, data=None, headers=None, retries=3, pause=0.25, timeout=45):
    # Returns (bytes, final_url). Retries on 429 and 5xx with a growing wait.
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    hdr = {"User-Agent": user_agent()}
    if headers:
        hdr.update(headers)
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=hdr)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read()
                time.sleep(pause)
                return body, resp.geturl()
        except urllib.error.HTTPError as err:
            last = err
            if err.code in (429, 500, 502, 503, 504) and attempt + 1 < retries:
                time.sleep(2 * (attempt + 1))
                continue
            raise
        except urllib.error.URLError as err:
            last = err
            if attempt + 1 < retries:
                time.sleep(2 * (attempt + 1))
                continue
            raise
    raise last


def fetch_json(url, params=None, data=None, headers=None, **kw):
    hdr = {"Accept": "application/json"}
    if headers:
        hdr.update(headers)
    body, final = fetch(url, params=params, data=data, headers=hdr, **kw)
    return json.loads(body.decode("utf-8")), body, final


def write_new(path, text):
    # Refuses to overwrite. Creates parent folders.
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    with open(path, "x", encoding="utf-8") as fh:
        fh.write(text)


def run(main):
    # Wraps a script entry point so a failed web call prints a short message, not a traceback.
    try:
        main()
    except urllib.error.HTTPError as err:
        body = ""
        try:
            body = err.read()[:200].decode("utf-8", "replace")
        except Exception:
            pass
        die("web request failed: HTTP %s for %s %s" % (err.code, err.url, body))
    except urllib.error.URLError as err:
        die("web request failed: %s" % err.reason)
    except FileExistsError as err:
        die("will not overwrite an existing file: %s" % err.filename)


def die(msg):
    sys.stderr.write("error: " + msg + "\n")
    sys.exit(2)


def openalex_params(extra=None):
    p = dict(extra or {})
    mail = os.environ.get("CONTACT_EMAIL", "").strip()
    if mail:
        p["mailto"] = mail
    key = os.environ.get("OPENALEX_API_KEY", "").strip()
    if key:
        p["api_key"] = key
    return p


def short_id(value):
    # https://openalex.org/A123 -> A123
    return value.rstrip("/").split("/")[-1] if value else value
