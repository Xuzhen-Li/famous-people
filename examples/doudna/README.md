# Worked example: a profile of a well-known public scientist

This folder holds a finished profile built with the workflow in `profile/WORKFLOW.md`. The subject is Jennifer A. Doudna, chosen because a lot of public information exists and every part of the method has something to work on. It demonstrates the method and its limits. It is not an assessment of the person, not a recommendation, and not a ranking.

这个文件夹是按 `profile/WORKFLOW.md` 做完的一份档案，对象是 Jennifer A. Doudna：她的公开信息很多，方法的每个部分都有东西可做。它演示方法和局限，不是对这个人的评价、推荐或排名。

| File | What it is |
|---|---|
| `PROFILE.en.md` | The profile in English (sections 0 to 17 of the template) |
| `PROFILE.zh.md` | The same profile in Chinese |
| `data/` | The tables and records the profile cites, produced by the scripts |
| `data/SOURCES_LOG.tsv` | For every page read: address, day, size and sha256 of what was read |

Both profiles pass `python3 profile/scripts/check_profile.py` with no errors and no warnings. That check only confirms that tags, dates and labels exist; it cannot tell whether a source says what a line says.

## What the example shows

- Identity: an ORCID record and an OpenAlex record tied together by a shared paper, and a count mismatch kept visible (the record says 737 works, 654 were found by its id).
- Lineage: sources that disagree on a year, recorded as a difference instead of being resolved by guesswork.
- Metrics with caveats: author position understates her role on the 2012 paper.
- Unknowns kept visible: Google Scholar, other funders, openings and PubPeer are written as unknown or not checked.
- Public presence: one account tied to her by an official page, with a bio and no posts; the active channels seen are institutional.
- Reactions: formal, press and community items kept apart; the one patent dispute found is between institutions and is not about research conduct.
- Personal background: self-stated items and one outlet’s report only, with family details left out on purpose.

## Regenerating the data

The scripts are in `profile/scripts/`. These commands produced the files in `data/`. The downloaded works list (`works.jsonl`) is large and is not kept here; the fetch command recreates it.

```text
python3 profile/scripts/openalex_author.py search --name "Jennifer Doudna" --limit 5 --out data/openalex_search.md
python3 profile/scripts/openalex_author.py fetch --id A5067184382 --out work/doudna/openalex
python3 profile/scripts/openalex_author.py summary --dir work/doudna/openalex --out data/openalex/summary.md
python3 profile/scripts/coauthors.py --dir work/doudna/openalex --out-dir data/network --top 15
python3 profile/scripts/check_dois.py --works work/doudna/openalex/works.jsonl --out data/doi_check.tsv
python3 profile/scripts/orcid_record.py --orcid 0000-0001-9161-999X --out data/orcid.md
python3 profile/scripts/nih_reporter.py grants --profile-id 1900251 --out data/nih_grants.tsv
python3 profile/scripts/lab_page.py --url https://doudnalab.org/people/ --out data/lab_people.md
python3 profile/scripts/lab_page.py --url https://doudnalab.org/ --out data/lab_home.md
python3 profile/scripts/social_links.py page --url https://doudnalab.org/ --out data/social_links_lab_home.md
python3 profile/scripts/social_links.py mastodon --acct @jenniferdoudna@genomic.social --out data/mastodon.md
```

Counts change as the sources change. Pages and records were read on 2026-11-26 (China Standard Time); a later run gives a later picture. Names of lab members are left out of every lab-page file on purpose (counts only); `data/network/coauthors.tsv` lists co-authors of published papers, as the workflow describes.
