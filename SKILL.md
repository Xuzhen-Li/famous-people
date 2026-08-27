---
name: famous-bio
description: Write one evidence-grounded Chinese 生物学名人系列 biography about a scientist and a concrete biological question, with research records, figures, QC, and a reader-clean export.
---

# famous-bio

This is the package's only agent entry. It writes one biography at a time into a generic user workspace.

## Read before drafting

1. [references/voice-contract.md](references/voice-contract.md)
2. [references/pipeline.md](references/pipeline.md)
3. [references/companion-skills.md](references/companion-skills.md) for optional accelerators
4. [references/fail-table.md](references/fail-table.md)
5. [references/teaching-walk.md](references/teaching-walk.md)
6. [references/english-models.md](references/english-models.md)
7. [references/continuity.md](references/continuity.md)
8. [references/write-body.md](references/write-body.md)
9. [references/reader-voice.md](references/reader-voice.md)
10. [references/figure-policy.md](references/figure-policy.md)
11. [references/quality-bar.md](references/quality-bar.md)

## Stage contract

1. Research primary and reliable secondary sources; write a complete S1 evidence record with the bundled template and identify gaps.
2. Use the bundled S2 templates to produce 3–5 claims, evidence, boundaries, and an outline. S2 does not write the WeChat body.
3. Fetch 1–3 English explainers. Save only `reader question → evidence → next question` in S0. Facts remain tied to primary `[n]` sources.
4. Draft Chinese with the bundled teaching, continuity, body, and reader-voice references. English wording, syntax, rhythm, and transitions are not drafting material.
5. Revise with the mandatory Chinese strategy in `references/write-body.md`.
6. Add a verified portrait, a legally usable primary table/plate or numbered paper figure, and useful explanatory images. Generated mechanism diagrams are optional.
7. Run `qc_gate.py`, `verify_dois.py`, `export_ship.py`, and `publish_lint.py` in that order.

Optional integrations may accelerate research, outlining, Chinese revision, or illustration. They are not required. If one is used, read its own `SKILL.md`; otherwise execute the bundled fallback workflow without simulating an unavailable tool.

## Output

```text
drafts/BG-XXX_SLUG_vN.md
runs/BG-XXX_vN/
figures/
qc/YYYYMMDD_BG-XXX_vN_factcheck.md
dist/BG-XXX_SLUG_vN.md
```

The visible title may retain `生物学名人系列`, but it must not show an internal ID. Work drafts may contain `## 数字与出处`; exports must not. Mechanical checks do not establish factual correctness. Do not post to WeChat unless explicitly requested.
