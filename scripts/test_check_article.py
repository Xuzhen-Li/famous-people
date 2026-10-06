#!/usr/bin/env python3
"""Tests for check_article.py. Each ERROR and the count logic."""

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from check_article import analyze, format_report, hanzi_count, main, median, percentile_90

LONG = "摩尔根在培养瓶里看见一只白眼雄蝇"  # 16 hanzi


def article(body, refs="[1] Morgan. Science, 1910. https://doi.org/10.1126/science.32.812.120"):
    return f"{body}\n\n## 参考文献\n\n{refs}\n"


def ok_body(extra=""):
    sentences = "。".join([LONG] * 4) + "。"
    return f"{sentences}这一结果写在当年的短文里[1]。\n\n{extra}"


def with_images(n):
    parts = [f"![图](https://example.com/{i}.png)\n\n*图{i}。*" for i in range(n)]
    parts.append("果" * 30 + "。")
    return article("\n\n".join(parts))


class CountTests(unittest.TestCase):
    def test_hanzi_median_p90_and_filters(self):
        text = """---
title: 试
---

# 小标题不计入

一九一零年五月，摩尔根在培养瓶里发现了一只白眼雄果蝇，于是把它配给红眼雌果蝇。后代全部是红眼，红色相对于白色是显性。

![图](fly.png)

*这是整行图注，不计入。*

> 培养瓶就放在哥伦比亚大学的实验台上，旁边还有红眼雌蝇。

## 参考文献

[1] Morgan. Science, 1910. https://doi.org/10.1126/science.32.812.120
"""
        report = analyze(text)
        s1 = hanzi_count("一九一零年五月，摩尔根在培养瓶里发现了一只白眼雄果蝇，于是把它配给红眼雌果蝇")
        s2 = hanzi_count("后代全部是红眼，红色相对于白色是显性")
        s3 = hanzi_count("培养瓶就放在哥伦比亚大学的实验台上，旁边还有红眼雌蝇")
        lengths = [s1, s2, s3]
        self.assertEqual(report["sentences"]["n"], 3)
        self.assertEqual(report["sentences"]["median"], median(lengths))
        self.assertEqual(report["sentences"]["p90"], percentile_90(lengths))
        self.assertEqual(report["hanzi"], sum(lengths))
        self.assertEqual(report["paragraphs"]["n"], 2)
        self.assertEqual(report["paragraphs"]["max"], s1 + s2)
        self.assertEqual(report["errors"], [])

    def test_analogy_and_hype_counts(self):
        prose = (
            "这个比例好比一把尺子，读起来并不费劲。"
            "结果犹如账本上的一栏，数字跟在动词后面。"
            "过程仿佛流水那样往前走，并不停在口号上。"
            "做法如同对照实验里的那一组，材料是果蝇。"
            "读者就像观众坐在台下，听完一次杂交。"
        )
        text = article(ok_body(prose + "这真是伟大的一步，也是伟大的发现。"))
        report = analyze(text)
        self.assertEqual(report["analogy_markers"], 5)
        self.assertEqual(sum(1 for w in report["warnings"] if w == "套话：伟大"), 2)
        self.assertTrue(any("比方标记" in w for w in report["warnings"]))
        self.assertEqual(report["errors"], [])


class ErrorTests(unittest.TestCase):
    def test_each_leak_marker(self):
        samples = {
            "[待确认]": "这一年的数字仍是[待确认]。",
            "[推测]": "后来的读者有[推测]。",
            "TODO": "这里 TODO 还要补。",
            "facts.md": "细节见 facts.md。",
            "Walk": "这一段叫 Walk。",
            "Selected": "条目是 Selected。",
            "S1": "先写 S1。",
            "S2": "再写 S2。",
            "brief": "不要交 brief。",
        }
        for label, sentence in samples.items():
            report = analyze(article(ok_body(sentence)))
            self.assertTrue(
                any(label in err for err in report["errors"]),
                msg=report["errors"],
            )

    def test_paraphrase_warning(self):
        few = analyze(article("他写下这一行字，又把瓶子放回架子上。" * 6, refs="1. x"))
        many = analyze(article("他写下这一行字，又把瓶子放回架子上。" * 7, refs="1. x"))
        self.assertFalse(any("他写" in w for w in few["warnings"]))
        self.assertTrue(any("7 处" in w for w in many["warnings"]))

    def test_source_walk_disclaim_and_timeline(self):
        walk = "论文里说他数了很多只果蝇，结果并不整齐。" * 7
        disclaim = "这和后来的理论不是一回事，他当时还不是这样想的。这是后来的说法。"
        timeline = "他一八六六年生，一八八六年毕业，一八九〇年博士，一八九一年教书，一九〇四年到纽约，一九〇九年养蝇，一九一〇年发表。"
        report = analyze(article(walk + "\n\n" + disclaim + "\n\n" + timeline, refs="1. x"))
        joined = " ".join(report["warnings"])
        self.assertIn("按资料转述", joined)
        self.assertIn("撇清", joined)
        self.assertIn("年表", joined)
        clean = analyze(article("他数了很多只果蝇，结果并不整齐，白眼只在雄蝇身上。" * 7, refs="1. x"))
        clean_joined = " ".join(clean["warnings"])
        for label in ("按资料转述", "撇清", "年表"):
            self.assertNotIn(label, clean_joined)

    def test_long_sentences_and_stand_in_words(self):
        long_sentence = "他" + "把白眼雄蝇和红眼雌蝇放进同一个瓶子里" * 5 + "。"
        report = analyze(article(long_sentence * 6 + "这笔账和那张图纸对上了。", refs="1. x"))
        joined = " ".join(report["warnings"])
        self.assertIn("一逗到底", joined)
        self.assertIn("80 字的长句 6 句", joined)
        self.assertIn("账 / 图纸", joined)

    def test_missing_references_section(self):
        report = analyze(ok_body())
        self.assertIn("没有「参考文献」一节", report["errors"])

    def test_citation_without_entry(self):
        report = analyze(article("他投给了杂志[2]。" + "。".join([LONG] * 4) + "。", refs="[1] Only one."))
        self.assertTrue(any("[2]" in err for err in report["errors"]))

    def test_numbered_reference_matches(self):
        body = "。".join([LONG] * 4) + "。见当年原文[1]。"
        report = analyze(article(body, refs="1. Morgan. Science, 1910. https://example.org"))
        self.assertEqual(report["errors"], [])

    def test_paragraph_over_600(self):
        report = analyze(article("测" * 601 + "。"))
        self.assertTrue(any("600" in err for err in report["errors"]))

    def test_choppy_median(self):
        report = analyze(article("他说完了。她记下了。天数对上。瓶子空了。"))
        self.assertTrue(any("中位" in err for err in report["errors"]))


def prose_hanzi(n, piece=40):
    chunks = []
    left = n
    while left:
        take = piece if left >= piece else left
        chunks.append("果" * take)
        left -= take
    paragraphs = []
    for i in range(0, len(chunks), 4):
        paragraphs.append("。".join(chunks[i : i + 4]) + "。")
    return "\n\n".join(paragraphs)


class WarnTests(unittest.TestCase):
    def test_short_share_and_short_body_are_warnings_only(self):
        short = "他说完了。"  # 4
        long = LONG + "。"
        text = article((short * 4) + (long * 6))
        report = analyze(text)
        self.assertGreaterEqual(report["sentences"]["median"], 15)
        self.assertGreater(report["sentences"]["short_share"], 0.35)
        self.assertLess(report["hanzi"], 4000)
        self.assertEqual(report["errors"], [])
        self.assertTrue(any("短于 12" in w for w in report["warnings"]))
        self.assertTrue(any("少于 4000，可能讲得太浅" in w for w in report["warnings"]))

    def test_body_length_threshold_is_4000(self):
        short = analyze(article(prose_hanzi(3999)))
        self.assertEqual(short["hanzi"], 3999)
        self.assertIn(
            "正文汉字 3999，少于 4000，可能讲得太浅；回 facts.md 看有没有没讲开的事",
            short["warnings"],
        )
        self.assertEqual(short["errors"], [])
        enough = analyze(article(prose_hanzi(4000)))
        self.assertEqual(enough["hanzi"], 4000)
        self.assertFalse(any("少于 4000" in w for w in enough["warnings"]))
        self.assertEqual(enough["errors"], [])


class ImageTests(unittest.TestCase):
    def test_count_threshold_and_readable_report(self):
        for n, warned in ((0, True), (1, True), (4, True), (5, True), (6, False)):
            report = analyze(with_images(n))
            self.assertEqual(report["images"], n, msg=n)
            self.assertIn(f"配图：{n} 张", format_report(report), msg=n)
            message = f"配图 {n} 张，少于 6 张"
            if warned:
                self.assertIn(message, report["warnings"], msg=n)
            else:
                self.assertNotIn(message, report["warnings"], msg=n)
            self.assertFalse(any("缺图注" in w for w in report["warnings"]), msg=n)
            self.assertEqual(
                sum("外链" in w for w in report["warnings"]),
                n,
                msg=n,
            )

    def test_markup_anywhere_before_references(self):
        body = "果" * 30 + "。\n\n见 ![白眼](eye.png) 这一张。\n\n*白眼雄蝇。*"
        report = analyze(article(body))
        self.assertEqual(report["images"], 1)
        self.assertFalse(any("缺图注" in w for w in report["warnings"]))
        self.assertFalse(any("图片文件不存在" in e for e in report["errors"]))

    def test_local_file_relative_to_base_dir(self):
        body = "\n\n".join(
            [
                "![缺](figures/missing.png)",
                "*没有这张。*",
                "![有](figures/map.png)",
                "*染色体图。*",
                "果" * 30 + "。",
            ]
        )
        text = article(body)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "figures").mkdir()
            (root / "figures" / "map.png").write_bytes(b"x")
            report = analyze(text, base_dir=root)
        self.assertEqual(report["errors"], ["图片文件不存在：figures/missing.png"])
        self.assertFalse(any("缺图注" in w for w in report["warnings"]))
        self.assertEqual(analyze(text)["errors"], [])

    def test_remote_warns_and_is_not_a_missing_file(self):
        body = "\n\n".join(
            [
                "![远](https://example.com/a.png)",
                "这里不是图注。",
                "![另](http://example.com/b.png)",
                "_下划线图注。_",
                "果" * 30 + "。",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            report = analyze(article(body), base_dir=tmp)
        self.assertIn("图片是外链，没有下载到本地：https://example.com/a.png", report["warnings"])
        self.assertIn("图片缺图注：https://example.com/a.png", report["warnings"])
        self.assertIn("图片是外链，没有下载到本地：http://example.com/b.png", report["warnings"])
        self.assertFalse(any("缺图注：http://example.com/b.png" in w for w in report["warnings"]))
        self.assertFalse(any("图片文件不存在" in e for e in report["errors"]))

    def test_caption_markers_and_missing_caption(self):
        body = "\n".join(
            [
                "![甲](a.png)",
                "*星号图注。*",
                "",
                "![乙](b.png)",
                "",
                "_下划线图注。_",
                "",
                "![丙](c.png)",
                "这行不是图注。",
                "",
                "果" * 30 + "。",
            ]
        )
        report = analyze(article(body))
        self.assertFalse(any(w == "图片缺图注：a.png" for w in report["warnings"]))
        self.assertFalse(any(w == "图片缺图注：b.png" for w in report["warnings"]))
        self.assertIn("图片缺图注：c.png", report["warnings"])
        self.assertEqual(report["errors"], [])

    def test_images_after_references_are_ignored(self):
        refs = "\n".join(
            [
                "![图](https://example.com/late.png)",
                "",
                "*图注。*",
                "",
                "## " + "注" * 13,
                "",
                "[1] Morgan.",
            ]
        )
        report = analyze(article("果" * 30 + "。", refs=refs))
        self.assertEqual(report["images"], 0)
        self.assertFalse(any("外链" in w for w in report["warnings"]))
        self.assertFalse(any("缺图注" in w for w in report["warnings"]))
        self.assertFalse(any("小标题" in w for w in report["warnings"]))

    def test_main_uses_article_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "fly.png").write_bytes(b"x")
            path = root / "post.md"
            body = "\n\n".join(
                [
                    "![有](fly.png)",
                    "*图。*",
                    "![缺](nope.png)",
                    "*图。*",
                    "果" * 30 + "。",
                ]
            )
            path.write_text(article(body), encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main([str(path)])
            text = buf.getvalue()
        self.assertEqual(code, 1)
        self.assertIn("图片文件不存在：nope.png", text)
        self.assertNotIn("图片文件不存在：fly.png", text)
        self.assertIn("配图：2 张", text)

    def test_svg_chinese_passes_and_garbage_bytes_fail(self):
        good = '<svg xmlns="http://www.w3.org/2000/svg"><text>白眼雄蝇</text></svg>'
        bad = (
            b'<svg xmlns="http://www.w3.org/2000/svg"><text>'
            b"\xff\xfe"
            b"</text></svg>"
        )
        body = "\n\n".join(
            [
                "![好](figures/ok.svg)",
                "*图。*",
                "![坏](figures/bad.svg)",
                "*图。*",
                "果" * 30 + "。",
            ]
        )
        text = article(body)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "figures").mkdir()
            (root / "figures" / "ok.svg").write_text(good, encoding="utf-8")
            (root / "figures" / "bad.svg").write_bytes(bad)
            report = analyze(text, base_dir=root)
        self.assertFalse(any("ok.svg" in e for e in report["errors"]))
        self.assertIn("SVG 无法解析（多半是中文乱码）：figures/bad.svg", report["errors"])
        self.assertIn("用了自绘 SVG 图 2 张，改找网上现成的图", report["warnings"])
        bare = analyze(text)
        self.assertFalse(any("SVG" in e for e in bare["errors"]))
        self.assertIn("用了自绘 SVG 图 2 张，改找网上现成的图", bare["warnings"])

    def test_svg_replacement_character_and_broken_xml(self):
        replaced = '<svg xmlns="http://www.w3.org/2000/svg"><text>白眼\ufffd</text></svg>'
        broken = '<svg xmlns="http://www.w3.org/2000/svg"><text>白眼</text>'
        body = "\n\n".join(
            [
                "![乱](figures/replaced.svg)",
                "*图。*",
                "![残](figures/broken.svg)",
                "*图。*",
                "果" * 30 + "。",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "figures").mkdir()
            (root / "figures" / "replaced.svg").write_text(replaced, encoding="utf-8")
            (root / "figures" / "broken.svg").write_text(broken, encoding="utf-8")
            report = analyze(article(body), base_dir=root)
        self.assertIn(
            "SVG 无法解析（多半是中文乱码）：figures/replaced.svg",
            report["errors"],
        )
        self.assertIn(
            "SVG 无法解析（多半是中文乱码）：figures/broken.svg",
            report["errors"],
        )

    def test_svg_paths_warn(self):
        body = "\n\n".join(
            [
                "![甲](figures/a.svg)",
                "*甲。*",
                "![乙](https://example.com/b.svg)",
                "*乙。*",
                "![丙](figures/c.png)",
                "*丙。*",
                "果" * 30 + "。",
            ]
        )
        report = analyze(article(body))
        self.assertIn("用了自绘 SVG 图 2 张，改找网上现成的图", report["warnings"])
        self.assertFalse(any("SVG 无法解析" in e for e in report["errors"]))
        png = analyze(with_images(6))
        self.assertFalse(any("自绘 SVG" in w for w in png["warnings"]))
        self.assertFalse(any("少于 6" in w for w in png["warnings"]))


class PacingTests(unittest.TestCase):
    def test_choppy_median_warns_with_connective_advice(self):
        choppy = analyze(article("果" * 20 + "。"))
        normal = analyze(article("果" * 26 + "。"))
        self.assertTrue(any("偏碎" in w and "连接" not in w and "因为" in w for w in choppy["warnings"]))
        self.assertTrue(any("不要只把句号改成逗号" in w for w in choppy["warnings"]))
        self.assertFalse(any("偏碎" in w for w in normal["warnings"]))

    def test_many_gene_symbols_and_notebook_details_warn(self):
        many = analyze(article("基因 C、c、Wx、wx、a1、A2、Dt 和 c-m1 都出现了，插入长 4.3 kb，编号 338 的那株。" + "果" * 30 + "。"))
        few = analyze(article("Ac 和 Ds 在 X 染色体旁边，DNA 也提到了。" + "果" * 30 + "。"))
        self.assertTrue(any("字母符号" in w for w in many["warnings"]))
        self.assertTrue(any("kb / 编号" in w for w in many["warnings"]))
        self.assertFalse(any("字母符号" in w for w in few["warnings"]))
        self.assertFalse(any("kb / 编号" in w for w in few["warnings"]))

    def test_follow_up_must_reach_recent_decade(self):
        old = analyze(article("1931 年她发表了论文，1983 年得奖。" + "果" * 30 + "。"))
        new = analyze(article("1931 年她发表了论文，2022 年有人读完了整个基因组。" + "果" * 30 + "。"))
        self.assertTrue(any("最近十年" in w for w in old["warnings"]))
        self.assertFalse(any("最近十年" in w for w in new["warnings"]))

    def test_defining_textbook_words_warns(self):
        bad = analyze(article("植株长大时，细胞一分为二，这种分裂叫有丝分裂。DNA 是构成基因的化学物质。" + "果" * 30 + "。"))
        good = analyze(article("她叫它们控制因子，因为它们管着旁边的基因。减数分裂时同源染色体配对。" + "果" * 30 + "。"))
        self.assertTrue(any("课本里的词" in w for w in bad["warnings"]))
        self.assertFalse(any("课本里的词" in w for w in good["warnings"]))

    def test_short_lead_in_before_image_warns(self):
        long_para = "果" * 60 + "。"
        lead = "1935年的一张照片里，他和鲍林站在一起。"
        img = "![照片](figures/a.jpg)\n\n*图注。*"
        bad = analyze(article(f"{long_para}\n\n{lead}\n\n{img}"))
        good = analyze(article(f"{long_para}\n\n{img}"))
        self.assertTrue(any("为放图补写" in w for w in bad["warnings"]))
        self.assertFalse(any("为放图补写" in w for w in good["warnings"]))

    def test_median_below_15_keeps_error(self):
        report = analyze(article("果" * 14 + "。"))
        self.assertIn("句子中位长度 14 字，低于 15 字", report["errors"])


class SubheadingTests(unittest.TestCase):
    def test_h2_longer_than_12_hanzi(self):
        short = "白眼雄果蝇的发现过程说明"
        long_a = short + "完"
        long_b = "丁" * 13
        self.assertEqual(hanzi_count(short), 12)
        self.assertEqual(hanzi_count(long_a), 13)
        self.assertEqual(hanzi_count(long_b), 13)
        body = "\n".join(
            [
                "## " + short,
                "## " + long_a,
                "## " + long_b,
                "# " + "甲" * 13,
                "### " + "乙" * 13,
                "果" * 30 + "。",
            ]
        )
        refs = "## " + "丙" * 13 + "\n\n[1] x"
        report = analyze(article(body, refs=refs))
        self.assertEqual(
            [w for w in report["warnings"] if w.startswith("小标题太长")],
            [f"小标题太长：{long_a}", f"小标题太长：{long_b}"],
        )


class TitleTests(unittest.TestCase):
    def test_tail_after_last_colon_else_pipe(self):
        long = "白" * 19
        short = "白" * 18
        over = analyze(article(f"# 生物学名人系列｜摩尔根：{long}\n\n" + "果" * 30 + "。"))
        self.assertIn(
            f"题目后半句 19 字，太长（真人题目多在 4–18 字）：{long}",
            over["warnings"],
        )
        exact = analyze(article(f"# 生物学名人系列｜摩尔根：{short}\n\n" + "果" * 30 + "。"))
        self.assertFalse(any(w.startswith("题目后半句") for w in exact["warnings"]))
        colon_wins = analyze(
            article(f"# 生物学名人系列｜{'甲' * 20}：白眼雄蝇\n\n" + "果" * 30 + "。")
        )
        self.assertFalse(any(w.startswith("题目后半句") for w in colon_wins["warnings"]))
        last = analyze(article(f"# 系列｜人名：前半：{long}\n\n" + "果" * 30 + "。"))
        self.assertIn(
            f"题目后半句 19 字，太长（真人题目多在 4–18 字）：{long}",
            last["warnings"],
        )
        pipe = analyze(article(f"# 生物学名人系列｜{long}\n\n" + "果" * 30 + "。"))
        self.assertIn(
            f"题目后半句 19 字，太长（真人题目多在 4–18 字）：{long}",
            pipe["warnings"],
        )
        ascii_colon = analyze(article(f"# 人名:{long}\n\n" + "果" * 30 + "。"))
        self.assertFalse(any(w.startswith("题目后半句") for w in ascii_colon["warnings"]))

    def test_first_hash_line_after_frontmatter(self):
        long = "白" * 19
        body = "\n".join(
            [
                "## " + "甲" * 20,
                "# 生物学名人系列｜摩尔根：白眼雄蝇",
                "# 生物学名人系列｜后来的标题：" + long,
                "果" * 30 + "。",
            ]
        )
        text = f"---\ntitle: 试\n# 生物学名人系列｜忽略：{long}\n---\n\n" + article(body)
        report = analyze(text)
        self.assertFalse(any(w.startswith("题目后半句") for w in report["warnings"]))

    def test_suspense_words_warn_only_on_h1(self):
        samples = [
            "生物学名人系列｜摩尔根：白眼怎样改了他的看法",
            "生物学名人系列｜艾弗里：为什么没有获奖",
            "生物学名人系列｜摩尔根：他如何看见连锁",
            "生物学名人系列｜摩尔根：白眼竟然遗传",
            "生物学名人系列｜摩尔根：白眼竟能遗传",
        ]
        for title in samples:
            report = analyze(article(f"# {title}\n\n" + "果" * 30 + "。"))
            self.assertIn(f"题目在设悬念：{title}", report["warnings"], msg=title)
            self.assertEqual(
                sum(w.startswith("题目在设悬念") for w in report["warnings"]),
                1,
                msg=title,
            )
        plain = "生物学名人系列｜摩尔根：果蝇的白眼改变了他对遗传学的看法"
        body = "\n".join(
            [
                f"# {plain}",
                "",
                "他问为什么白眼只在雄蝇身上。",
                "",
                "## 怎样遗传",
                "",
                "果" * 30 + "。",
            ]
        )
        report = analyze(article(body))
        self.assertFalse(any("设悬念" in w for w in report["warnings"]))
        buried = (
            "---\n# 生物学名人系列｜摩尔根：白眼怎样改了他的看法\n---\n\n"
            + article(f"# {plain}\n\n" + "果" * 30 + "。")
        )
        report = analyze(buried)
        self.assertFalse(any("设悬念" in w for w in report["warnings"]))


if __name__ == "__main__":
    unittest.main()
