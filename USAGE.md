# Usage / 用法

## English

Install this repository as the single `famous-bio` skill. In a generic writing workspace, request one person and one concrete, checkable biological question.

```text
/famous-bio Write one 生物学名人系列 article about [person], centered on [question].
```

The agent must:

1. Read `SKILL.md` and all required root references.
2. Build `runs/<ID>_vN/S1-evidence.md`, then the two S2 records with the bundled templates.
3. Fetch 1–3 English explainers and record only the order of reader questions in S0.
4. Draft Chinese from verified evidence and the bundled writing references, not from English wording.
5. Revise whole paragraphs, check sentence integrity, remove editor-facing language, clarify captions only when a real misidentification risk exists, and run mechanical gates last.
6. Save the work file under `drafts/`, figures under `figures/`, fact-check records under `qc/`, and the reader-clean file under `dist/`.

Optional integrations listed in [references/companion-skills.md](references/companion-skills.md) may accelerate a stage. None is required. Read an integration's `SKILL.md` only when it is installed and actually used.

Example commands from the writing-workspace root:

```bash
python3 ~/.cursor/skills/famous-bio/scripts/qc_gate.py \
  --profile wechat --file drafts/BG-XXX_SLUG_vN.md
python3 ~/.cursor/skills/famous-bio/scripts/verify_dois.py \
  --file drafts/BG-XXX_SLUG_vN.md --out runs/BG-XXX_vN/S7-verify-log.txt
python3 ~/.cursor/skills/famous-bio/scripts/export_ship.py \
  --in drafts/BG-XXX_SLUG_vN.md --out dist/BG-XXX_SLUG_vN.md
python3 ~/.cursor/skills/famous-bio/scripts/publish_lint.py \
  --file dist/BG-XXX_SLUG_vN.md
```

Stop at a reader-clean local file. No WeChat posting occurs unless the user explicitly requests it.

## 中文

把本仓库作为唯一的 `famous-bio` 技能安装。在普通写作工作区中，一次指定一位人物和一个可核对的生物学问题。

Agent 使用本包模板建立 S1 证据和 S2 主张边界，再用英文讲解排列读者问题，随后关闭英文措辞，只从已核证据和本包写作参考起草。工作稿、运行记录、图片、核查记录和读者稿分别放入 `drafts/`、`runs/`、`figures/`、`qc/`、`dist/`。外部集成只用于可选加速，不是运行依赖。

默认只生成本地成品；用户没有明确要求时，不发布到微信公众号。
