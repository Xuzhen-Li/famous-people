# One-biography pipeline

Work in the user's current workspace:

1. **S0 scope** — person, concrete question, class, evidence limits.
2. **S1 evidence** — primary sources, metadata checks, locked numbers, contradictions, recent high-profile work on the core object.
3. **S2 claims** — 3–5 claims with evidence, allowed wording, and boundaries; then a separate outline.
4. **S0 English models** — reader-question order only.
5. **S3 draft** — Chinese reader prose in `drafts/`.
6. **S4 revision** — paragraph diagnosis, whole-paragraph rewriting, sentence integrity, reader cleanup, read-aloud check.
7. **S4.5 fact-check** — citation set, numbers, attribution, figures, and unresolved gaps.
8. **S5 figures** — local files plus source ledger.
9. **S6 mechanical QC** — `qc_gate.py`.
10. **S7 verification** — DOI metadata, image existence, and human spot-check record.
11. **S8 export** — `export_ship.py`, manual reader cleanup if needed, then `publish_lint.py`.

This sequence is self-contained. Use the bundled templates for S0, S1, and both S2 records, and the bundled references for drafting and revision. Public integrations listed in `companion-skills.md` may accelerate a stage but never block the fallback workflow.

Commands:

```bash
python3 ~/.cursor/skills/famous-bio/scripts/qc_gate.py --profile wechat \
  --file drafts/BG-XXX_SLUG_vN.md
python3 ~/.cursor/skills/famous-bio/scripts/verify_dois.py \
  --file drafts/BG-XXX_SLUG_vN.md --out runs/BG-XXX_vN/S7-verify-log.txt
python3 ~/.cursor/skills/famous-bio/scripts/export_ship.py \
  --in drafts/BG-XXX_SLUG_vN.md --out dist/BG-XXX_SLUG_vN.md
python3 ~/.cursor/skills/famous-bio/scripts/publish_lint.py \
  --file dist/BG-XXX_SLUG_vN.md
```

A mechanical pass means only that structural checks found no blocking issue. Stop after producing a clean local reader file unless publication was explicitly requested.
