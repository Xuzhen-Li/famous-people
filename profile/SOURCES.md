# Source checklist / 来源清单

Tick a source only after you opened it and wrote it in section 17 of the profile. Addresses checked on 2026-11-26. Services change: if one stops working, say so in section 16 and use another.

只有真正打开并登记到档案第 17 节的来源才打勾。地址于 2026-11-26 检查。服务会变：某个失效了，在第 16 节写明，换一个。

## A. Identity / 身份

| Done | Source | Address | Gives | Watch out for |
|---|---|---|---|---|
| [ ] | OpenAlex authors | https://api.openalex.org/authors?search=NAME | Author ids, ORCID, institutions, topics, counts | Split and merged records. Without a free key the daily budget is shared by everyone on your network address; the scripts use page numbers, which need no key. Set OPENALEX_API_KEY if the service asks for one |
| [ ] | ORCID public API | https://pub.orcid.org/v3.0/ORCID/record | Public employment, education, funding, works | Often empty or old. Never guess an ORCID: a valid number can belong to someone else or be locked |
| [ ] | Institution directory page | the department or university site | Current post, department, sometimes CV | Out of date pages: write the date you read it |
| [ ] | Lab or group page | found from the institution page | Members, alumni, news, openings, contact route | Written by the lab: it shows what the lab chooses to show |
| [ ] | Google Scholar page | https://scholar.google.com | Works and counts, if the person keeps a page | Look by eye. It has no public API and blocks scripts. Do not scrape |
| [ ] | ROR | https://api.ror.org/v2/organizations?query=NAME | Standard name of an institution | Only for matching institution names |
| [ ] | Wikidata | https://www.wikidata.org | Linked identifiers (ORCID, Scholar, institution) | Community edited: a lead, not a final source |

## B. Career, training, lineage / 经历和师承

| Done | Source | Address | Gives | Watch out for |
|---|---|---|---|---|
| [ ] | Researcher CV or biography page | lab or institution site | Degrees, posts, advisors | Self-reported: fine for a career, label it as such |
| [ ] | Academy, prize, or society biography | for example nobelprize.org, academy pages | Education and training with advisors named | Check which year the text was written |
| [ ] | PhD thesis | open repositories: the university library, OATD (https://oatd.org), DASH, eScholarship | Acknowledgments, committee, dedication of credit | Access varies; use only open copies |
| [ ] | Academic Tree, Mathematics Genealogy | https://academictree.org, https://www.mathgenealogy.org | Leads on advisor and student links | User-built. A lead only: confirm each link in a first-hand source |
| [ ] | Chinese researchers: institution faculty page, 院士或学会的传记, 学位论文公开库 | the institution site, the Academy site | Education, posts, 导师 | Chinese and English pages can differ: record both |

## C. Papers and metrics / 论文和指标

| Done | Source | Address | Gives | Watch out for |
|---|---|---|---|---|
| [ ] | OpenAlex works | via openalex_author.py | Works list, citations, authors, topics | Counts differ from other databases. The author record count can differ from the works found by id |
| [ ] | Crossref | https://api.crossref.org/works/DOI | DOI, title, year, publisher notices | The title check is a word overlap, not a proof |
| [ ] | Semantic Scholar, DBLP (computer science) | https://api.semanticscholar.org, https://dblp.org | A second opinion on papers | Rate limited. A key may be needed |
| [ ] | The papers themselves | publisher or preprint server | Authors, contributions, funding statements | Read the contribution statement when there is one |

## D. Funding / 经费

| Done | Source | Address | Gives | Watch out for |
|---|---|---|---|---|
| [ ] | NIH RePORTER | https://api.reporter.nih.gov | US NIH awards, years, organization | NIH only. Amounts are per fiscal year |
| [ ] | NSF Award Search | https://api.nsf.gov/services/v1/awards.json?pdPIName=NAME | US NSF awards | Name search matches several people |
| [ ] | UKRI Gateway to Research | https://gtr.ukri.org/gtr/api/persons?q=NAME | UK awards | Name search |
| [ ] | EU CORDIS, ERC | https://cordis.europa.eu | EU awards | Coordinator versus partner roles differ |
| [ ] | 国家自然科学基金 | https://kd.nsfc.cn | Chinese NSFC projects | May ask for a security check: then check by hand or leave unknown |
| [ ] | Funding lines in papers and on the lab page | the papers, the lab page | Fellowships, institute support, private funders | Funding statements list support, not the size of the group |

## E. Lab, members, outcomes / 课题组和去向

| Done | Source | Address | Gives | Watch out for |
|---|---|---|---|---|
| [ ] | Lab people page, news list, alumni list | via lab_page.py | Counts of members, announcements, next posts | Survivorship; out of date; a missing name is unknown |
| [ ] | Lab policy pages | the lab site | How the lab asks to be contacted, conflict of interest, safety | These are signals about process, not about daily life |
| [ ] | Thesis acknowledgments of former students | open thesis repositories | Who supervised day to day | Use only to confirm a link, never to quote feelings of a named student |

## F. Network / 合作网络

| Done | Source | Address | Gives | Watch out for |
|---|---|---|---|---|
| [ ] | OpenAlex co-authorship | via coauthors.py | Frequent co-authors, years | Consortium papers, split ids |
| [ ] | Contribution statements in papers | the papers | Who did what | Not every journal has them |

## G. Mentoring signals / 带学生方式的信号

| Done | Source | Address | Gives | Watch out for |
|---|---|---|---|---|
| [ ] | Researcher interviews, talks, oral histories, podcasts | university news, society sites, YouTube, library oral history | The researcher’s own account of how the lab is run | Self description. One remark is one signal |
| [ ] | Mentoring awards and citations | the awarding body | An outside statement about mentoring | Rare, and written by nominators |
| [ ] | Alumni writing under their own name | personal sites, lab alumni pages, society newsletters | First-hand accounts | One person view. Keep their words short and cited |
| [ ] | Anonymous forums and rating sites | not used | Nothing you can verify | Do not use or repeat. Note it in section 16 if you saw it |

## H. Records to check / 需要核对的记录

| Done | Source | Address | Gives | Watch out for |
|---|---|---|---|---|
| [ ] | Crossref notices (retractions, corrections, expressions of concern) | via check_dois.py | Notice type, issuer, DOI, date | Read the notice for the reason |
| [ ] | Retraction Watch data | carried in Crossref; data at https://gitlab.com/crossref/retraction-watch-data | Retractions with reasons | Reasons range widely: read the entry |
| [ ] | PubPeer | https://pubpeer.com | Public comments on a paper | Shows a security check to scripts: search by hand or write not checked. Comments are comments, not findings |
| [ ] | Institution or funder statements | their sites | Formal outcomes, if public | Absence of a statement is unknown |

## J. Public personal background / 公开的个人背景

| Done | Source | Address | Gives | Watch out for |
|---|---|---|---|---|
| [ ] | Autobiography or prize biography | for example nobelprize.org, academy sites | Where the person grew up, why they chose the field, in their words | Self-description, written for an audience |
| [ ] | Interviews, podcasts, public talks, oral histories | university news, society sites, YouTube, library oral history | The person’s own account | One remark is one remark; date it |
| [ ] | Profiles in named outlets | magazines, university news offices | An outside account of the path | Written for readers; note the outlet and the date; may be behind a sign-in |
| [ ] | Lab or institution "people" or "about" page | the lab site | What the person chooses to show | Chosen by the person or the lab |

## K. Social media and public presence / 社交媒体和公开形象

| Done | Source | Address | Gives | Watch out for |
|---|---|---|---|---|
| [ ] | Links on official pages | via social_links.py page | Accounts that an official page ties to the person | A link on a lab page can point to an institute account, not the person |
| [ ] | Mastodon public profile | https://INSTANCE/api/v1/accounts/lookup?acct=NAME (via social_links.py) | Bio, creation date, post count, date of last post | Same name is not the same person; needs an official link |
| [ ] | Bluesky public profile | https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile (via social_links.py) | Bio, post count | Same as above |
| [ ] | X, Facebook, Instagram, LinkedIn | the platform | Public posts, if visible without signing in | Usually need a sign-in: write not checked: sign-in needed |
| [ ] | Google Scholar, ResearchGate | the platform | A profile page, if the person keeps one | Look by eye; they block scripts. Do not scrape |
| [ ] | Personal site, blog, GitHub, YouTube | linked from official pages | Public writing, code, talks | Check the account is the person via a link both ways |
| [ ] | WeChat public account, Weibo, Zhihu | the platform | Public posts by a Chinese researcher | Often need an app or a sign-in: write not checked if so |

## L. Community reactions / 社区反应

| Done | Source | Address | Gives | Watch out for |
|---|---|---|---|---|
| [ ] | PubPeer | https://pubpeer.com | Public comments on a paper | Shows a security check to scripts: search by hand or write not checked. Comments are comments, not findings |
| [ ] | Retraction Watch | https://retractionwatch.com/?s=NAME | Reporting on retractions and disputes | Absence of a post is unknown |
| [ ] | News search | the outlet or a news search engine | Press coverage of the person or a dispute | Note the outlet and date; a headline is not a finding |
| [ ] | Public blogs and forums by named authors | the site | Named community views | One view. Keep quotes short and cited; skip anonymous posts |
| [ ] | Public social commentary by named accounts | the platform | Public reactions to a talk or a paper | Only what is visible without signing in; a post is a reaction |
| [ ] | Court, institution and funder documents | their sites | Formal outcomes | Read the document; say who the parties are |

## M. Not used / 不使用

LinkedIn and other sign-in sites, Scopus and Web of Science (login), anything behind a paywall you do not hold, private social media, rating sites and anonymous posts, any page that shows a security check to a script, and any private message. 需要登录的站点、没有权限的付费库、私人社交媒体、评分网站和匿名帖子、对脚本出现安全验证的页面、任何私人消息，都不使用。
