#!/usr/bin/env python3
# Offline tests for the profile helpers. No network. Run: python3 -B profile/scripts/test_profile_scripts.py
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import check_dois  # noqa: E402
import lab_page  # noqa: E402
import openalex_author  # noqa: E402
import orcid_record  # noqa: E402
import social_links  # noqa: E402
from _common import short_id, write_new  # noqa: E402


class SmallHelpers(unittest.TestCase):
    def test_orcid_checksum(self):
        self.assertTrue(orcid_record.checksum_ok("0000-0002-1825-0097"))
        self.assertTrue(orcid_record.checksum_ok("0000-0001-9161-999X"))
        self.assertFalse(orcid_record.checksum_ok("0000-0002-1825-0098"))
        self.assertFalse(orcid_record.checksum_ok("not-an-orcid"))

    def test_h_index(self):
        self.assertEqual(openalex_author.h_index([10, 8, 5, 4, 3]), 4)
        self.assertEqual(openalex_author.h_index([]), 0)
        self.assertEqual(openalex_author.h_index([0, 0]), 0)

    def test_short_id(self):
        self.assertEqual(short_id("https://openalex.org/A123"), "A123")

    def test_title_overlap(self):
        self.assertEqual(check_dois.overlap("RNA structure of a ribozyme", "RNA structure of a ribozyme"), 1.0)
        self.assertEqual(check_dois.overlap("", "anything here"), 0.0)
        self.assertLess(check_dois.overlap("Crystal structure of a ribozyme", "Fruit fly wing size"), 0.3)

    def test_doi_normal_form(self):
        self.assertEqual(check_dois.norm_doi("https://doi.org/10.1000/ABC"), "10.1000/abc")

    def test_type_wording(self):
        self.assertEqual(openalex_author.type_label(None), "unknown")
        self.assertEqual(openalex_author.type_label("article"), "article")
        self.assertEqual(check_dois.plain_type(""), "")

    def test_write_new_refuses_to_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "sub", "a.txt")
            write_new(p, "one")
            with self.assertRaises(FileExistsError):
                write_new(p, "two")
            with open(p, encoding="utf-8") as fh:
                self.assertEqual(fh.read(), "one")


TABLE_PAGE = """<html><body><h2>Former Students</h2><table>
<tr><th>Name</th><th>Time In Lab</th><th>Position</th></tr>
<tr><td>Student One</td><td>2010-2014</td><td>Assistant Professor, Some University</td></tr>
<tr><td>Student Two</td><td>2012-2018</td><td></td></tr>
</table></body></html>"""


class LabPage(unittest.TestCase):
    def test_tenure(self):
        self.assertEqual(lab_page.tenure([["A", "2010-2014", "x"], ["B", "2012\u20132018", ""], ["C", "n/a", ""]]), [4, 6])

    def test_names_left_out_by_default(self):
        text = lab_page.render(lab_page.parse(TABLE_PAGE), names=False)
        self.assertNotIn("Student One", text)
        self.assertNotIn("Student Two", text)
        self.assertIn("2 listed", text)

    def test_names_shown_only_on_request(self):
        text = lab_page.render(lab_page.parse(TABLE_PAGE), names=True)
        self.assertIn("Student One", text)


class SocialLinks(unittest.TestCase):
    def test_platform_of(self):
        self.assertEqual(social_links.platform_of("https://x.com/someone"), "X")
        self.assertEqual(social_links.platform_of("https://scholar.google.com/citations?user=abc"), "Google Scholar")
        self.assertIsNone(social_links.platform_of("https://example.org/about"))

    def test_link_parser_reads_rel_me(self):
        p = social_links.Links()
        p.feed("<a rel=\"me\" href=\"https://mastodon.example/@a\">Mastodon</a>")
        self.assertEqual(len(p.items), 1)
        self.assertEqual(p.items[0]["rel"], "me")

    def test_page_command_lists_links_from_a_file_and_skips_share_buttons(self):
        html = ("<a href=\"https://x.com/lab\">X</a>"
                "<a href=\"https://www.facebook.com/sharer/sharer.php?u=1\">share</a>"
                "<a href=\"/people\">People</a>")
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "page.html")
            out = os.path.join(d, "links.md")
            with open(src, "w", encoding="utf-8") as fh:
                fh.write(html)
            r = subprocess.run([sys.executable, "-B", os.path.join(HERE, "social_links.py"), "page",
                                "--file", src, "--out", out], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(out, encoding="utf-8") as fh:
                text = fh.read()
            self.assertIn("https://x.com/lab", text)
            self.assertNotIn("sharer", text)
            self.assertIn("sign-in", text)


def run_check(path):
    return subprocess.run([sys.executable, "-B", os.path.join(HERE, "check_profile.py"), path],
                          capture_output=True, text=True)


class ProfileCheck(unittest.TestCase):
    def test_templates_are_refused_until_filled(self):
        for name in ("profile.en.md", "profile.zh.md"):
            r = run_check(os.path.join(ROOT, "profile", "templates", name))
            self.assertNotEqual(r.returncode, 0, name)

    def test_examples_pass(self):
        for name in ("PROFILE.en.md", "PROFILE.zh.md"):
            r = run_check(os.path.join(ROOT, "examples", "doudna", name))
            self.assertEqual(r.returncode, 0, name + "\n" + r.stdout + r.stderr)

    def _bad(self, body):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "P.md")
            write_new(p, body)
            return run_check(p)

    def test_missing_source_tag_is_caught(self):
        r = self._bad("# Profile: Test\n\n## 0. Summary\n\n- A claim with no source tag.\n")
        self.assertNotEqual(r.returncode, 0)

    def test_unlabelled_background_and_reaction_items_are_caught(self):
        head = "".join("## %d. Section\n\n" % n for n in range(0, 9))
        body = head + "## 9. Background\n\n- She likes hiking [S1].\n\n## 10. Social\n\n- Nothing [S1].\n\n" \
               "## 11. Reactions\n\n- Someone said something [S1].\n\n"
        body += "".join("## %d. Section\n\n" % n for n in range(12, 17))
        body += "## 17. Sources\n\n| Tag | Address | Read | Date |\n|---|---|---|---|\n| S1 | https://example.org | x | 2026-01-01 |\n"
        r = self._bad(body)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not labelled Self-stated", r.stdout)
        self.assertIn("not labelled Formal", r.stdout)

    def test_family_wording_is_caught(self):
        r = self._bad("# Profile: Test\n\n## 0. Summary\n\n- Her husband is a doctor [S1].\n")
        self.assertIn("private-life wording", r.stdout)


if __name__ == "__main__":
    unittest.main()
