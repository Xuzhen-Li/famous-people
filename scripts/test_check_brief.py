import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_brief  # noqa: E402
import background_data  # noqa: E402


class CheckBriefTest(unittest.TestCase):
    def test_private_terms_flagged(self):
        r = check_brief.check("- 他的妻子也是教授\n- lives at 12 Main St\n")
        self.assertEqual([x["level"] for x in r if x["level"] == "ERROR"], ["ERROR", "ERROR"])

    def test_scope_line_allowed(self):
        r = check_brief.check("范围：只含公开的职业信息。不含住址、家庭、私生活、健康。\n")
        self.assertEqual(r, [])

    def test_unsourced_fact_warns(self):
        r = check_brief.check("- 2012 年发表 Cas9 论文\n- 2012 年发表 Cas9 论文 https://doi.org/10.1126/science.1225829\n")
        self.assertEqual([x["line"] for x in r], [1])

    def test_example_brief_passes(self):
        here = os.path.dirname(os.path.abspath(__file__))
        p = os.path.join(here, "..", "examples", "doudna", "brief.md")
        with open(p, encoding="utf-8") as f:
            r = check_brief.check(f.read())
        self.assertFalse([x for x in r if x["level"] == "ERROR"], r)


class BackgroundDataTest(unittest.TestCase):
    def test_grouping_and_coauthors(self):
        rows = [
            {"core_project_num": "R01X", "project_title": "B", "fiscal_year": 2021, "award_amount": 10,
             "organization": {"org_name": "U"}, "activity_code": "R01"},
            {"core_project_num": "R01X", "project_title": "A", "fiscal_year": 2020, "award_amount": 5,
             "organization": {"org_name": "U"}, "activity_code": "R01"},
        ]
        g = background_data.group_grants(rows)
        self.assertEqual(g["R01X"]["total"], 15)
        self.assertEqual(g["R01X"]["years"], {2020, 2021})
        works = [{"authorships": [{"author": {"id": "me", "display_name": "Me"}},
                                  {"author": {"id": "x", "display_name": "X"}}]}] * 3
        self.assertEqual(background_data.summarize_coauthors(works, "me"), [("X", 3, "x")])


if __name__ == "__main__":
    unittest.main()
