"""Self-contained tests for the WeChat QC profile."""
from __future__ import annotations

import re
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from qc_gate import ABSTRACT_NOTE_PATTERNS, audit
from publish_lint import scan as publish_scan
from verify_dois import main as verify_main


def audit_text(text: str) -> dict:
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        path = Path(tmp) / "case.md"
        path.write_text(text, encoding="utf-8")
        return audit(path, "wechat")


class QcGateWechatTests(unittest.TestCase):
    def test_generic_methods_summary_patterns_are_detected(self):
        text = "重复测量未观察到组间差异，故合并统计。"
        hits = [p for p in ABSTRACT_NOTE_PATTERNS if re.search(p, text)]
        self.assertGreaterEqual(len(hits), 2)

    def test_generic_methods_summary_fails(self):
        result = audit_text(
            "# 人物与实验\n\n"
            "重复测量未观察到组间差异，故合并统计。[1]\n"
        )
        self.assertFalse(result["mech_pass"])
        self.assertTrue(any("压缩式编辑/方法说明" in e for e in result["errors"]))

    def test_generic_editor_aside_fails(self):
        result = audit_text("# 人物与实验\n\n这里补一句背景，正文以核对表为准。\n")
        self.assertFalse(result["mech_pass"])
        self.assertTrue(any("作者旁白" in e for e in result["errors"]))

    def test_missing_local_image_fails_verification(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            draft = Path(tmp) / "draft.md"
            log = Path(tmp) / "verify.txt"
            draft.write_text("![missing](figures/not-here.jpg)\n", encoding="utf-8")
            argv = [
                "verify_dois.py",
                "--file", str(draft),
                "--out", str(log),
            ]
            with patch.object(sys, "argv", argv):
                self.assertEqual(verify_main(), 1)
            self.assertIn(
                "LOCAL | FAIL | figures/not-here.jpg",
                log.read_text(encoding="utf-8"),
            )

    def test_packaged_example_passes(self):
        draft = ROOT / "examples" / "BG-001-mendel-v21" / "draft.md"
        self.assertTrue(draft.is_file())
        result = audit(draft, "wechat")
        self.assertTrue(result["mech_pass"], result["errors"])

    def test_publish_lint_accepts_clean_biography(self):
        errors, warnings = publish_scan(
            "# 生物学名人系列｜某人：一个具体问题\n\n他记录了实验结果。[1]\n"
        )
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_publish_lint_rejects_internal_id_and_draft_section(self):
        errors, _ = publish_scan(
            "# 生物学名人系列｜BG-123 某人\n\n## 数字与出处\n"
        )
        joined = "\n".join(errors)
        self.assertIn("内部 ID 外泄", joined)
        self.assertIn("草稿专用标题外泄", joined)

    def test_publish_lint_rejects_package_process_note(self):
        errors, _ = publish_scan("本示例不附带位图，生成说明见附件。\n")
        self.assertTrue(any("作者或打包过程外泄" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
