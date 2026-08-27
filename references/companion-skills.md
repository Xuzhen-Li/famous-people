# Optional integrations and sources

The package has no companion runtime dependency. Its references, scripts, and S0/S1/S2 templates provide the complete workflow.

The following public integrations are optional accelerators. If one is installed and used, read its `SKILL.md` first. If it is absent, use the bundled fallback named in the last column.

| Stage | Optional integration | Public source | Bundled fallback |
|---|---|---|---|
| Research | `storm-research` | https://github.com/openwhat007/storm-research | `templates/S1-evidence.md` plus `references/pipeline.md` |
| Claims and structure | `nature-writing` | https://github.com/Yuan1z0825/nature-skills | Both bundled S2 templates |
| Chinese revision | `human-writing` | https://github.com/KKKKhazix/human-writing | `references/teaching-walk.md`, `continuity.md`, `write-body.md`, and `reader-voice.md` |
| Mechanism figures | `baoyu-article-illustrator` | https://github.com/JimLiu/baoyu-skills | Omit generated art or provide documented instructions for later generation |

Optional research and structure tools must not write the WeChat body. Do not apply English academic polishing to Chinese prose. Do not invoke a posting integration unless the user asks to publish in the current request.
