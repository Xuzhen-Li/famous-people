# famous-people

Homemade Cursor skill. One person, one checkable question, one evidence-grounded biography.

Not biologists only. The bundled Mendel example is a worked case, not the scope.

It writes a Chinese WeChat-ready draft with research, claim boundaries, figure provenance, and mechanical checks kept in separate files. It does not post unless you say so.

## Install

```bash
git clone https://github.com/Xuzhen-Li/famous-people.git
mkdir -p ~/.cursor/skills
ln -sfn "$(pwd)/famous-people" ~/.cursor/skills/famous-people
```

Needs Python 3.10+ and Cursor. Optional companion skills are listed in `references/companion-skills.md`. None are required.

## Use

In the workspace where you want `drafts/`, `runs/`, `figures/`, `qc/`, and `dist/`:

```text
/famous-people Write one biography of [person], centered on [one checkable question].
```

Then:

1. Read `SKILL.md` and the root references.
2. Build `runs/<ID>_vN/` (S1 evidence, S2 claim boundary).
3. Draft Chinese from verified evidence, not from English wording.
4. Run the gates, export a reader-clean file to `dist/`.

```bash
python3 ~/.cursor/skills/famous-people/scripts/qc_gate.py \
  --profile wechat --file drafts/PERSON_vN.md
python3 ~/.cursor/skills/famous-people/scripts/verify_dois.py \
  --file drafts/PERSON_vN.md --out runs/PERSON_vN/S7-verify-log.txt
python3 ~/.cursor/skills/famous-people/scripts/export_ship.py \
  --in drafts/PERSON_vN.md --out dist/PERSON_vN.md
python3 ~/.cursor/skills/famous-people/scripts/publish_lint.py \
  --file dist/PERSON_vN.md
```

Full steps: [USAGE.md](USAGE.md). Worked example: [Mendel v21](examples/BG-001-mendel-v21/README.md).

## License

MIT for code and docs. Example images keep the licenses in that example's `figures/SOURCES.md`.
