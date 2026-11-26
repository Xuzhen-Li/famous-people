# Researcher profile workflow / 研究者档案流程

Goal: given a researcher name, collect and organize public information that helps someone choose an advisor or a collaborator, or simply get to know the person. Every claim carries a source that was actually opened. What could not be found is marked unknown.

目标：给定一位研究者的姓名，从公开来源收集并整理信息，帮助选导师、选合作者，或者了解这个人。每一条都带一个真正打开过的来源，找不到的写未知。

Read PRIVACY.md first. Source list: SOURCES.md. Templates: templates/profile.en.md and templates/profile.zh.md. Scripts: scripts/. A finished example: examples/doudna/.

## Rules that apply to every step / 每一步都适用的规则

1. **Cite what you opened.** A claim gets a tag [S3] that points to section 17 of the profile: address or DOI, what you read there, and the day. If you did not open it, it is not a source. 引用你真正打开过的来源。
2. **Unknown is an answer.** Write unknown and where you looked. Never fill a gap with a guess, a model memory, or a reasonable assumption. 未知也是答案。
3. **Signals are not facts.** Anything about mentoring style, lab atmosphere or character is a signal: one dated thing someone said or did in public. 带学生方式只能写成信号。
4. **Neutral words about records.** Say what the notice says and who issued it. No adjectives about the person. 对记录只陈述来源上写的话。
5. **Public information only.** The professional record, personal background that the person or a named outlet made public, public accounts that an official page ties to the person, and public reactions. No home address, family, health, religion, politics, pay of a named person, anything non-public, anything behind a login or a security check, and no background checks. 只用公开信息，不查非公开内容，不做背景调查。
6. **Counts, not people, for trainees.** The subject is the researcher. Describe trainees in aggregate. 学生只写汇总数字。
7. **Date everything.** Pages change. Write the day you read each one, in the time zone you work in. 每条都写日期。
8. **Be polite to servers.** One request at a time, an honest user agent, robots.txt respected, no scraping of sites that refuse it. Set CONTACT_EMAIL in your own shell so site operators can reach you; never put it in a file you share. 对服务器要客气。

## Step 0. Purpose and folder / 目的和文件夹

Write one line: advisor, collaborator, or general. Choose a slug (family-name-given-name). Make `work/<slug>/` in your own workspace; `work/` is ignored by git on purpose, so a profile of a real person is never committed by accident. Copy the template for your language to `work/<slug>/PROFILE.md`.

写一行目的：导师、合作者或一般了解。取一个 slug。在自己的工作区建 `work/<slug>/`；`work/` 被 git 忽略，免得真人的档案被误提交。把对应语言的模板复制过去。

## Step 1. Identity / 身份

```text
python3 profile/scripts/openalex_author.py search --name "Given Family"
python3 profile/scripts/orcid_record.py --orcid 0000-0000-0000-0000 --out work/<slug>/orcid.md
```

List the candidates. Rule out the wrong ones with two independent links, for example: the ORCID on the OpenAlex record is also listed on the lab page; a paper under the OpenAlex record also appears on the institution page. Same name, same field is not enough. Note if OpenAlex has split one person into two ids or merged two people into one. Look at the Google Scholar page by eye if one exists; do not scrape it. An ORCID record is often empty: that says nothing about the person.

列出候选，用两条互相独立的链接排除错的。同名同领域不够。记下 OpenAlex 有没有把一个人拆成两个编号，或把两个人并成一个。Google Scholar 页面只用眼睛看，不抓取。ORCID 常常是空的，这说明不了什么。

## Step 2. Career timeline and training lineage / 职业经历和师承

Order of sources, best first: the researcher’s own CV or institution page; the lab page; an academy, prize or society biography; the PhD thesis (acknowledgments, committee page); the researcher’s own interviews; user-built genealogy sites such as academictree.org (a lead only, never the last source for a link). For each training step name the advisor or host only if a source says so. A gap is unknown.

来源由好到次：研究者本人的简历或机构页面；课题组页面；科学院、奖项或学会的传记；博士论文（致谢、答辩委员会页）；本人的访谈；用户自建的学术谱系网站只作线索。训练阶段的导师或接收人，来源写了才写，缺口写未知。

## Step 3. Research directions over time, key papers / 研究方向和关键论文

```text
python3 profile/scripts/openalex_author.py fetch --id A1234567890 --out work/<slug>/openalex
python3 profile/scripts/openalex_author.py summary --dir work/<slug>/openalex --out work/<slug>/openalex/summary.md
python3 profile/scripts/check_dois.py --works work/<slug>/openalex/works.jsonl --out work/<slug>/doi_check.tsv
```

The summary gives topics by five-year period and the most cited works. Use it to decide where to look; then open the abstracts of the key papers and describe each period in plain words. A key paper needs a DOI that Crossref confirms and a title that matches. Say whether the subject is first, last or middle author. The OpenAlex topic labels are machine assigned: do not treat them as the researcher’s own description.

摘要给出每五年的主题和被引最高的论文。用它决定看哪里，再打开关键论文的摘要，用平实的话写每个时期。关键论文的 DOI 要在 Crossref 里核对过，题目相符。写明是第一作者、末位作者还是中间作者。OpenAlex 的主题标签是机器打的，不要当作研究者自己的说法。

## Step 4. Output and metrics / 成果和指标

Use the numbers in the summary, with the database name and day. Print the caveats next to them. Counts do not measure quality, mentoring or fit. Compare with the typical numbers of the field, not with other fields.

用摘要里的数字，写明数据库和日期，并把注意事项放在旁边。数字不衡量质量、带学生的方式或是否适合你。要和同领域比，不要跨领域比。

## Step 5. Grants and funding / 经费

```text
python3 profile/scripts/nih_reporter.py find --last Family --first Given
python3 profile/scripts/nih_reporter.py grants --profile-id 1234567 --out work/<slug>/nih_grants.tsv
```

NIH only. For other funders follow SOURCES.md and record which funders you searched. Not finding an award is unknown, not "no funding". The lab page and institute pages often name fellowships and institute support: cite them.

只覆盖 NIH。其他基金机构按 SOURCES.md 查，并记录查过哪些。查不到是未知，不是没有经费。

## Step 6. Lab size, members, where people went / 课题组规模和去向

```text
python3 profile/scripts/lab_page.py --url https://example.org/people/ --save-html work/<slug>/lab_people.html --out work/<slug>/lab_people.md
```

The script refuses pages that robots.txt disallows or that show a sign-in or security check, and leaves trainee names out. If it finds no counts, read the page by eye and count by hand; record that it is a hand count. Remember survivorship: a page lists the people who went on to visible posts and often omits those who left science or left early. Alumni outcomes are weak evidence about mentoring.

脚本会拒绝 robots.txt 不允许的页面，以及需要登录或出现安全验证的页面，并且不输出学生姓名。数不出来就用眼睛看、手工数，并注明是手工计数。注意幸存者偏差：页面列出的多是后来有了明显职位的人，提前离开或离开科研的人常常不在。往届成员去向只是关于带学生方式的很弱的证据。

## Step 7. Collaborators and network / 合作者和网络

```text
python3 profile/scripts/coauthors.py --dir work/<slug>/openalex --out-dir work/<slug>/network --top 25
```

Report frequent co-authors, long-running ties, and how many papers had a trainee-looking first author with the subject last. Merge split ids by hand and say so. A frequent co-author is a lead.

写出合作最多的人、长期合作，以及研究者为末位作者而第一作者像学生的论文数。拆开的编号手工合并并说明。合作次数多只是线索。

## Step 8. Mentoring signals / 带学生方式的信号

Where to look: the lab page (how it asks to be contacted, onboarding, policies); the researcher’s own interviews, talks and podcasts; the researcher’s own writing on mentoring; alumni who wrote under their own name; award citations for mentoring. How to write it: one signal per line, who said it, when, a short quote or a close paraphrase, and the address. Do not repeat anonymous posts or one-off complaints; if you find them, note "anonymous claim, not verifiable" in section 16 and do not use them. Do not turn one remark into a trait. Say what you could not find.

去哪里找：课题组页面（怎样联系、入组、规定）；研究者本人的访谈、报告和播客；本人写的关于带学生的文章；署真名的往届成员；带学生方面的奖项。怎么写：每条一个信号，写谁说的、何时、短引语或贴近的转述、地址。不转述匿名帖子和孤立的抱怨；找到了就在第 16 节记为"匿名说法，无法核实"，不使用。不要把一句话写成性格。写出没找到的内容。

## Step 9. Public personal background / 公开的个人背景

Where to look: the researcher’s own autobiography or prize biography, interviews, podcasts and public talks, the lab and institution pages (a "people" or "about" page), and profiles in named outlets. Write one item per line, label it Self-stated or Reported by <outlet>, and give the address and date. Quote briefly. Keep to the path and the public roles: where they grew up, why they chose the field, what they say shaped them, public service and outreach. Leave out family members, children, partners, health, religion, politics, money and anything the person did not make public. If the record is thin, write one line that says so. An ordinary researcher may have nothing beyond a lab page, and that is a complete answer.

去哪里找：研究者本人的自传或奖项传记、访谈、播客和公开报告，课题组和机构页面（人员页或"关于"页），署名媒体的人物报道。每条一行，标"自述"或"报道：<媒体>"，带地址和日期，引语要短。只写经历和公开的角色：在哪里长大、为什么选这一行、本人说什么塑造了自己、公共服务和科普。家人、子女、伴侣、健康、宗教、政治、金钱，以及本人没有公开的内容，一律不写。资料很少就写一行说明。普通研究者可能除了课题组页面什么都没有，这就是完整的答案。

## Step 10. Social media and public presence / 社交媒体和公开形象

```text
python3 profile/scripts/social_links.py page --url https://example.org/lab/ --out work/<slug>/social_links.md
python3 profile/scripts/social_links.py mastodon --acct @name@instance.example --out work/<slug>/mastodon.md
python3 profile/scripts/social_links.py bluesky --handle name.bsky.social --out work/<slug>/bluesky.md
```

Start from the official pages: the lab page, the institution page and the ORCID record often link to accounts. Then check the platforms in the template: X, Google Scholar, ResearchGate, Bluesky or Mastodon, LinkedIn, Facebook, Instagram, a personal site or blog, GitHub, YouTube, and for Chinese researchers WeChat public accounts, Weibo and Zhihu. An account counts only if an official page links to it or the account links back to an official page; the same name is not enough, because many people share a name. Look only at what is public without signing in. X, LinkedIn, Facebook and Instagram usually need a sign-in: write not checked: sign-in needed, and do not sign in, do not use someone else’s session, do not scrape. Do not read locked or private accounts. Record type of content, date of the last post and the address. For an ordinary person this step may be the main source of public information, and it may still find nothing: write that.

先看官方页面：课题组页面、机构页面和 ORCID 记录常常链接到账号。再逐个查模板里的平台：X、Google Scholar、ResearchGate、Bluesky 或 Mastodon、LinkedIn、Facebook、Instagram、个人网站或博客、GitHub、YouTube，中国的研究者再查微信公众号、微博和知乎。账号要算数，必须官方页面链接到它，或者账号反过来链接到官方页面；同名不够，因为重名的人很多。只看不登录就能看到的公开内容。X、LinkedIn、Facebook、Instagram 通常要登录：写"未查：需要登录"，不要登录，不借用别人的会话，不抓取。不看加锁或私密的账号。记录内容类型、最近一条的日期和地址。对普通人，这一步可能是公开信息的主要来源，也可能什么都找不到：照实写。

## Step 11. Community reactions / 社区反应

Search by hand, in this order: PubPeer (DOIs and name), Retraction Watch (site search), news search for the name and the institution, public blogs and forum threads by a named author, and public social commentary by named accounts. Label each item Formal, Press, Community (named author) or Reaction, and give who said it, when, and the address. Record praise and criticism in the same neutral words. A reaction is what someone said. It is not a finding about the person, and an allegation that no formal body has reported is not repeated. Do not repeat anonymous posts or rumors; note "anonymous claim, not verifiable" in section 16 if you saw one, and do not use it. A legal or patent dispute between institutions is a formal item: say who the parties are and that it is not about research conduct unless the document says so. If a site shows a security check to a script, check by hand or write not checked. If nothing is found, write where you looked and the date.

按下面的顺序手工查：PubPeer（DOI 和姓名）、Retraction Watch（站内搜索）、用姓名和机构做新闻搜索、署名者的公开博客和论坛帖、署名账号的公开社交评论。每条标"正式""报道""社区（署名者）"或"反应"，写明谁说的、何时、地址。赞扬和批评用同样中立的话记录。反应是某人说了什么，不是关于这个人的结论；没有正式机构报告过的指控不转述。不转述匿名帖子和传闻；看到了就在第 16 节记为"匿名说法，无法核实"，不使用。机构之间的法律或专利纠纷算"正式"项：写明各方是谁，除非文件本身这样写，否则说明它不涉及研究行为。网站对脚本出现安全验证的，手工查或写未查。什么都没找到，就写查了哪里、哪一天。

## Step 12. Recent activity, openings, contact / 最近动态、招人、联系

Latest papers and talks with dates. Admissions or opening statements exactly as the page words them, with the day you read them. Use the contact route the lab asks for; if it names a form or an address for applicants, use that one. Take an address only from the institution or lab page.

最新论文和报告，带日期。招生或招人说明，照页面原话写，并写你读的那天。用课题组要求的联系渠道；如果页面给了申请人用的表单或地址，就用那个。地址只取自机构或课题组页面。

## Step 13. Records to check / 需要核对的记录

Run check_dois.py (Crossref carries Retraction Watch data and publisher notices). Open every retraction or expression of concern notice and read the stated reason before writing anything. Corrections and errata are routine; list only the count. Search PubPeer by hand with the DOIs or the name and write what you saw, or write not checked. A site that shows a security check to a script is checked by hand or not at all. Write the sentence in the form "Crossref lists a retraction notice (type, issuer, DOI, date) for paper X; the notice gives the reason as ...". No conclusion about the person.

运行 check_dois.py（Crossref 带有 Retraction Watch 数据和出版社通告）。每一条撤稿或关注声明，都要先读通告里写明的原因再写。更正和勘误很常见，只写数量。PubPeer 手工用 DOI 或姓名搜索，写你看到了什么，或写未查。对脚本出现安全验证的站点，只手工查或者不查。句式："Crossref 列出了论文 X 的一条撤稿通告（类型、发布者、DOI、日期），通告写明的原因是……"。不对人下结论。

## Step 14. Fit checklist and questions / 匹配度和问题

Tick the checklist in section 14 only from what sections 1 to 13 support. Turn the unticked items into questions (section 15). Use templates/outreach.en.md or outreach.zh.md for the first email and for questions to current and former members. Show the profile to nobody as a ranking or a recommendation: it is a way to ask better questions.

只根据第 1 到 13 节能支持的内容打勾。没勾上的转成问题（第 15 节）。第一封邮件和问现有、往届成员的问题，用 templates/outreach.en.md 或 outreach.zh.md。不要把档案当成排名或推荐拿给别人：它的用处是帮你问出更好的问题。

## Step 15. Check before you use it / 使用前检查

```text
python3 profile/scripts/check_profile.py work/<slug>/PROFILE.md
```

Fix every ERROR. Read every WARN. Then open ten of your own claims at random in their sources and check that each source says what the line says. The script only checks that tags and dates exist.

有 ERROR 就改，每条 WARN 都要读。然后随机挑十条自己写的内容，到来源里核对来源是不是真这样写。脚本只检查标签和日期是否存在。

## Optional output: WeChat longread / 可选输出：公众号长文

For a public figure whose life is worth a long article, use the profile as the fact sheet: copy the cited facts into `work/<slug>/facts.md` (templates/facts.md) and continue with the four steps in SKILL.md. The longread has its own rules and is a different product: it tells a story and does not carry a fit checklist or mentoring signals. A longread about a living person keeps to professional life and published work.

对值得写长文的公众人物，把档案当作事实表：把带出处的事实抄进 `work/<slug>/facts.md`（templates/facts.md），再按 SKILL.md 里的四步继续。长文是另一种产品：它讲故事，不带匹配度清单和带学生方式的信号。写在世人物的长文，只写职业生活和已发表的工作。
