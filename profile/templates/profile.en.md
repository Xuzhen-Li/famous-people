# Profile: <full name>

Prepared: <YYYY-MM-DD, time zone>. Purpose: <choosing an advisor / choosing a collaborator / getting to know the person>.
Scope: public information only (professional record, public personal background, public presence, public reactions). See PRIVACY.md. Every line below ends with a source tag such as [S3], or says unknown.

> How to use this file. Copy it to work/<slug>/PROFILE.md. Fill the sections in order. Add each page, record or paper you read to section 17 as S1, S2 and so on, with the address, what you read there, and the day you read it. Delete these quoted instructions when done. Run `python3 profile/scripts/check_profile.py work/<slug>/PROFILE.md` before you use or share the profile.

## 0. Summary

> Five lines at most. Each line is a finding with a tag, not an opinion. Write what is known, what is not, and the one thing to check first.

- <finding> [S1]

## 1. Identity check

> Show that every source below is about the same person. Same name is not enough. Use two independent links: for example an ORCID that the lab page also lists, or a paper that appears under both the institution page and the author record.

| Item | Value | Source |
|---|---|---|
| Full name and common variants | <name; variants> | [S1] |
| ORCID | <0000-0000-0000-0000, or unknown> | [S2] |
| OpenAlex author id | <A..., note any split or merged records> | [S3] |
| Google Scholar page | <address, or unknown. Look only; do not scrape> | [S4] |
| Current institution and department | <place> | [S5] |
| Lab or group page | <address, or unknown> | [S6] |
| Why this is one person | <the two links that tie the sources together> | [S2][S6] |
| Other people with the same name that were ruled out | <who, and how> | [S3] |

## 2. Career timeline and training lineage

> Degrees, postdocs, faculty posts. Name the advisor or host for each training step when a source says so. Mark a gap as unknown.

| Years | Position or degree | Place | Advisor or host | Source |
|---|---|---|---|---|
| <from-to> | <position> | <place> | <name, or unknown> | [S5] |

## 3. Research directions over time

> One row per period of about five years. Key papers need a DOI that Crossref confirms (script: check_dois.py). Say which papers are the subject first or last author on.

| Period | Direction | Key papers (DOI) | Source |
|---|---|---|---|
| <years> | <topic in plain words> | <author year journal, doi:10....> | [S3] |

## 4. Output and metrics

> Quote the database and the day with every number. Keep the caveats from openalex_author.py next to the numbers.

- Works in the record, first and last year, citations, h-index: <numbers and database> [S3]
- Share of papers as first author, last author, middle author: <numbers> [S3]
- Typical venues: <list> [S3]
- Caveats that apply here: <field norms, consortium papers, merged or split records, preprints counted twice> [S3]

## 5. Grants and funding

> Only what a funder or the researcher publishes. Say which funders were searched. Absence in one funder is not absence of funding.

- Funders searched: <NIH RePORTER, NSF, others, or unknown> [S7]
- Current and recent awards: <title, funder, years, role> [S7]
- Funding the lab says it has (fellowships, institute support): <what the page says> [S6]

## 6. Lab: size, members, and where people went

> Counts only, from the public lab page and the news list (script: lab_page.py). Do not profile individual trainees. A person missing from a page is unknown, not a finding.

- Current members listed by role, and the date of the page: <counts> [S6]
- Join announcements by year: <counts, or unknown> [S6]
- Alumni listed, with a next position shown: <counts> [S6]
- Of those, posts in academia, industry, other: <counts and how they were sorted> [S6]
- Typical time in lab: <median years and range> [S6]

## 7. Collaborators and network

> Script: coauthors.py. A frequent co-author is a lead to check, not proof of a close tie.

- Most frequent co-authors, with years: <names, counts, years> [S3]
- Long-running ties (same co-author across many years): <who> [S3]
- Papers with the subject as last author and a first author who looks like a trainee (first author when the subject is last): <counts, no names needed> [S3]
- Papers left out of the counts because of very long author lists: <number> [S3]

## 8. Mentoring signals

> Signals, not facts. Each item is one thing someone said or did in public, with the source and date. Prefer the researcher’s own words, the lab policy pages, and named alumni who wrote under their own name. Do not repeat anonymous claims. Do not turn one remark into a trait.

- Signal: <what was said or shown; quote short; who said it; when> [S8]
- Signal from the lab page: <for example how the lab asks to be contacted, or what it publishes about onboarding> [S6]
- Signal from alumni outcomes: <what section 6 suggests, and why that is weak evidence> [S6]
- Not found: <what you looked for and could not find: unknown>

## 9. Public personal background

> Only what the person, an official page or a named outlet has made public: interviews, autobiographies, talks, lab or institution pages, profiles in named outlets, and the person’s own public accounts. Label every item Self-stated (the person said it) or Reported by <outlet> (someone else wrote it), with the source and the date. This section may be short. If little is public, say so in one line and stop: do not pad it and do not go looking in non-public places. Leave out family members, children, partners, health, religion, politics, money and home address. See PRIVACY.md.

- Self-stated: <where they grew up, why they entered the field, what they say shaped them; short quote; where and when it was said> [S1]
- Reported by <outlet>: <what the named outlet wrote, and its date> [S2]
- Little public information: <write this line when it is true: only the professional record is public, and nothing about personal background was found in the sources searched: unknown>

## 10. Social media and public presence

> Look for an account that an official page ties to the person (a link from the lab or institution page, or a link from the account to the official site). The same name is not enough. Look only at what is public without signing in; if a platform needs a sign-in, write not checked: sign-in needed. Never read private or locked accounts. Script: social_links.py. For an ordinary person with a thin record this section matters more; it may still end as nothing found, and then it says so.

| Platform | Public address | Tied to the person by | What is public (type, last activity) | Source |
|---|---|---|---|---|
| X | <address, or none found> | <link from an official page, or none> | <topics, date of last post> | [S1] |
| Google Scholar | <address, or unknown> | <link from an official page, or none> | <what it shows> | [S2] |
| ResearchGate | <address, or unknown> | <link from an official page, or none> | <what it shows> | [S3] |
| Bluesky or Mastodon | <address, or none found> | <link from an official page, or none> | <bio, post count, date of last post> | [S4] |
| LinkedIn, Facebook, Instagram | <address, or not checked> | <link from an official page, or none> | <not checked: sign-in needed> | [S5] |
| Personal site, blog, GitHub, YouTube | <address, or none found> | <link from an official page, or none> | <what it holds> | [S6] |
| WeChat public account, Weibo, Zhihu | <address, or none found> | <link from an official page, or none> | <what it holds> | [S7] |

- Summary of public presence: <which channels are active, which are only institutional, which are absent> [S1]

## 11. Community reactions

> How others have publicly reacted, kept apart from the facts about the person. Label each item Formal (an institution, court, funder or publisher), Press (a named outlet), Community (a named person’s blog, forum post or public social post) or Reaction (anything else). Say who reacted and when. Look at PubPeer, Retraction Watch, news search, public blogs and forums, and public social commentary. A reaction is what someone said, not a finding. Do not repeat anonymous claims, rumors or unverified allegations. Praise and criticism are recorded in the same neutral words (PRIVACY.md). If nothing was found, write where you looked and the date.

- Formal: <issuer, what it says, date> [S1]
- Press: <outlet, date, what it reports> [S2]
- Community (named author): <who, where, date, what was said; short quote> [S3]
- Not found: <where you looked and the date: unknown>

## 12. Recent activity, openings, and how to contact

- Latest papers, talks, preprints: <list with dates> [S3]
- Open positions or an admissions statement: <what the page says on which date, or unknown> [S6]
- How the lab asks to be contacted: <the instruction on the page> [S6]
- Contact address that the institution or lab publishes for enquiries: <address, or unknown> [S6]

## 13. Records to check

> State only what a source says. A correction or erratum is routine. A retraction or an expression of concern needs the notice itself read, with its stated reason. Never write a conclusion about the person. If a site could not be checked, say so.

- Crossref and Retraction Watch data (script: check_dois.py): <number of DOIs checked; notices found, with type and notice DOI; or no notice found on this date> [S9]
- PubPeer: <what a manual search for the DOIs or the name showed on this date, or not checked> [S10]
- Institution or funder public statements about the researcher’s work: <what was found, or none found on this date> [S5]

## 14. Fit checklist

> Tick what you can answer from sections 1 to 13. An item you cannot tick is a question for section 15.

- [ ] Their current direction overlaps with what I want to do in the next three to five years.
- [ ] They have people at my level (student or postdoc) and I know what those people published with them.
- [ ] Alumni outcomes match what I want afterwards (faculty, industry, other).
- [ ] The lab is hiring or taking students in my cycle, and I know how to apply.
- [ ] Funding covers the length of the position I would hold.
- [ ] I know who would do the daily supervision.
- [ ] Authorship and credit practice is something I can ask about and have understood.
- [ ] I know the researcher’s availability (travel, sabbatical, move) in the period I would be there.
- [ ] I have read at least two recent papers in full.
- [ ] I have one specific idea or question that shows I have read their work.

## 15. Questions to ask

> Choose five to eight. Ask them in the first email only if short; keep the rest for a call or visit. Ask current members as well as the researcher.

1. <question about the project I would join>
2. <question about who supervises day to day>
3. <question about authorship and who decides the order>
4. <question about how often the group meets and what a typical week looks like>
5. <question about where recent trainees went next>
6. <question about funding and the length of the post>

## 16. Unknowns

> Everything you looked for and could not find, so the reader does not mistake silence for a finding.

- <item>: unknown, searched <where> on <date>

## 17. Sources

> One row per source. Use the address you really opened, a DOI for papers, and the day you read it. Say what you read there, not what you hope it says. A page that needed a login or showed a security check is not a source.

| Tag | Address or DOI | What was read | Read on | Note |
|---|---|---|---|---|
| S1 | <https://...> | <what the page says that is used above> | <YYYY-MM-DD> | <optional> |
