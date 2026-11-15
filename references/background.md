# 模式二：认识一位导师或合作者（职业背景调查）

用在：学生选导师、博士后找组、找合作者之前，想把这个人在学术上的情况摸清楚。
只查公开的、和职业有关的信息。官方主页只是起点，要用别的公开来源去核对和补全。

## 能查什么

1. 履历：学位、导师、博士后、职位变动。来源：本人或实验室主页、ORCID、机构页面、学会会员页、诺奖或基金会公开简介。
2. 论文产出：每年发多少、发在哪、引用、近五年是否还在一线做事、常合作的人。来源：OpenAlex（https://docs.openalex.org/api-entities/authors ）、Crossref；用 `scripts/background_data.py` 拉一份数据附录。
3. 经费：拿过哪些项目、什么类型、哪年到哪年。来源：NIH RePORTER（https://reporter.nih.gov/ ，API https://api.reporter.nih.gov/ ）、NSF Award API（https://resources.research.gov/common/webapi/awardapisearch-v1.htm ）、欧盟 CORDIS（https://cordis.europa.eu/ ）、英国 UKRI Gateway to Research（https://gtr.ukri.org/ ）、国家自然科学基金大数据知识管理服务门户（https://kd.nsfc.cn/ ）。
4. 实验室和学生去向：实验室 alumni 页、学生论文致谢、Academic Family Tree（https://academictree.org/ ）、学生本人主页和公开的职位信息。看毕业年限、去学术界和业界的比例、有没有人很快离组。
5. 公开讲话：学术报告视频、播客、科普书、媒体采访。看他怎么讲自己的工作、怎么谈学生。
6. 新闻和争议：专利纠纷、撤稿、更正、学术不端调查、伦理争论、公司持股和利益冲突声明。来源：Retraction Watch 数据库（https://retractionwatch.com/retraction-watch-database-user-guide/ ）、PubPeer（https://pubpeer.com/ ）、法院和专利局公开文书、科学媒体报道、机构公告。
7. 公开评价：论坛里关于这个组的讨论，例如小木虫（https://muchong.com/ ）。知乎、一亩三分地、Reddit r/PhD 也常有这类讨论 [待确认：2026-11-15 从 box 抓取这三个站点被拦截，没有读到页面]。只记和指导方式、组内氛围、毕业情况、经费稳定性有关的内容。

## 不查什么

下面这些不查、不记、不写，哪怕网上能找到：

- 住址、电话、私人邮箱、车牌、行踪
- 配偶、子女、父母等家庭成员信息，感情和婚姻
- 健康、病史、宗教、政治倾向、性取向
- 非职业场合的私人照片和私人社交账号
- 把零散信息拼起来定位一个人（人肉）

如果材料里顺带出现了这些内容，不摘录，只写「材料涉及私人信息，未记录」。

## 怎么判断信息靠不靠谱

- 每条事实带出处链接和查阅日期。
- 数据库数字注明来自哪个库，不同库的数字互相不一样。
- 论坛评价是线索，不是事实。单条匿名帖不写进结论；要写，就写「论坛上有 N 条帖子提到……」，附链接，并说明无法核实。
- 和他本人的说法冲突时，两边都记。
- 老信息标年份。实验室主页上的去向常常多年不更新。

## 产出

`work/<slug>/brief.md`，照 `templates/brief.md`。写完运行：

```bash
python3 scripts/check_brief.py work/<slug>/brief.md
```

它会查出私人信息类词语和没有出处的事实行。有 ERROR 就改。

结论部分写给读者自己做决定用：哪些是优势，哪些需要当面问清（例如毕业年限、经费周期、署名规则），列出可以问导师或现在学生的具体问题。不给人下品德结论。
