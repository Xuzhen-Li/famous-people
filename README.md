# Famous Biologist Biography Skill

An evidence-grounded Cursor skill for writing one Chinese WeChat biography at a time. It keeps research, claims, prose revision, figure provenance, mechanical quality checks, and the reader-clean export separate.

## Package tree

```text
.
├── SKILL.md                 # the single agent entry
├── references/             # writing and evidence contracts
├── scripts/                # standard-library QC and export tools
├── templates/              # reusable run records
└── examples/BG-001-mendel-v21/
    ├── draft.md
    ├── dist.md
    ├── figures/
    └── runs/
```

## Prerequisites

- Python 3.10 or newer
- Cursor
- Network access for source research and optional DOI verification

This package is self-contained. Optional integrations can accelerate individual stages, but the bundled references and S0/S1/S2 templates provide the complete fallback workflow. See [references/companion-skills.md](references/companion-skills.md).

## Install

```bash
cd famous-biologist-biography-skill
mkdir -p "$HOME/.cursor/skills"
ln -s "$(pwd)" "$HOME/.cursor/skills/famous-bio"
```

## Usage

Open the workspace where you want `drafts/`, `runs/`, `figures/`, `qc/`, and `dist/`, then ask:

```text
/famous-bio Write an evidence-grounded biography of Gregor Mendel.
```

Follow [USAGE.md](USAGE.md). The skill creates files in the user's current workspace and handles one biography per run. It does not post to WeChat unless the user explicitly requests posting.

## Tests

```bash
python3 -m unittest scripts/test_qc_gate.py
python3 scripts/qc_gate.py --profile wechat \
  --file examples/BG-001-mendel-v21/draft.md \
  --json-out examples/BG-001-mendel-v21/runs/S6-qc.json
python3 scripts/verify_dois.py \
  --file examples/BG-001-mendel-v21/draft.md \
  --out examples/BG-001-mendel-v21/runs/S7-doi-image-log.txt
python3 scripts/publish_lint.py \
  --file examples/BG-001-mendel-v21/dist.md
```

Complete example: [BG-001 Mendel v21](examples/BG-001-mendel-v21/README.md).

## License

Code and documentation are released under the [MIT License](LICENSE). Individual example images retain the licenses recorded in the example's [figure source ledger](examples/BG-001-mendel-v21/figures/SOURCES.md).

---

# 生物学名人传记 Skill

这是一个为 Cursor 准备的单入口技能，用于一次写一篇有证据支撑的中文微信公众号人物稿。研究证据、主张边界、中文润色、图片来源、机械门禁和读者稿导出彼此分开。

## 前置条件

- Python 3.10 或更新版本
- Cursor
- 检索与可选 DOI 核验所需的网络

本包可以独立运行。可选集成只用于加速某些阶段；根目录参考文件与 S0/S1/S2 模板已经构成完整后备流程。

## 安装

下载或克隆仓库后，进入 `famous-biologist-biography-skill` 目录，再使用上方命令把当前目录链接到 `~/.cursor/skills/famous-bio`。

## 使用

在希望生成 `drafts/`、`runs/`、`figures/`、`qc/` 和 `dist/` 的工作区中调用 `/famous-bio`。完整步骤见 [USAGE.md](USAGE.md)，成品示例见 [孟德尔 v21](examples/BG-001-mendel-v21/README.md)。

除非用户明确要求发布，本技能不会执行微信公众号发布。
