# 配图

公众号长文要图文并茂。一篇 6–10 张，每个小节至少一张，图接在用到它的那一段后面。图为正文服务：先有正文讲到的东西，再找配它的图，不要为了放一张图补写一段正文。

## 一篇的搭配

- 人物肖像 1 张，最好是做这项工作那几年的。
- 地点、实验室、同事合影 1–2 张（果蝇室、冷泉港、湄潭、布林莫尔……）。
- 实验材料 1–2 张：果蝇、玉米穗、瓢虫、豌豆，标本或图版。
- 原始论文的图、表或图版 1 张：1929 年以前发表的论文和公有领域书籍，可以从 Biodiversity Heritage Library、Internet Archive、Commons 截取编号图直接用；仍有版权的论文图只写链接，不嵌入。
- 不自己画图。需要讲清一次杂交、染色体上的位置这类关系时，去找现成的图：原论文和 1929 年以前教科书里的图版（例如摩尔根等 1915 年的《孟德尔遗传的机制》）、Commons 上标明 CC 或公有领域的示意图。找不到合适的，就用文字讲清楚，不画。

## 找图

- 首选 Wikimedia Commons。用 API 核对许可和作者：
  `https://commons.wikimedia.org/w/api.php?action=query&titles=File:<文件名>&prop=imageinfo&iiprop=url|extmetadata&format=json`
  取 `LicenseShortName`、`Artist`、`url`。
- 也可以用 BHL、Internet Archive、美国国家医学图书馆、诺贝尔奖网站上标明公有领域的图。
- 不用：身份不确定的照片（文件名不等于身份）、只能按 fair use 使用的图、AI 生成的人像或假历史照片。
- 多搜几轮：英文和原语言关键词、人物全名、机构名都试；翻 Commons 的人物分类页（Category:<人名>）和机构分类页；在 BHL、Internet Archive 里翻原论文和老教科书的扫描页找图版。每张候选都打开看图本身，不只看文件名。

## 存放和登记

- 下载到 `work/<slug>/figures/`，文件名用英文 kebab-case；正文用相对路径 `figures/xxx.jpg`。公众号要上传本地文件，所以正文不用外链。
- 每张图在 `work/<slug>/figures.md` 登记一行：文件名、图上是什么、来源页链接、作者、许可。

## 图注

图片下一行单独一段，整行用 `*……*`。第一句写图上是什么、哪一年；第二句写来源和许可，CC 图写作者和许可名。图注不讲道理，道理在正文里。只有读者很可能认错时才加一句澄清，不要每张都写「这不是……」。

> *1947 年，冷泉港实验室里的芭芭拉·麦克林托克。Smithsonian Institution 摄，Wikimedia Commons，公有领域。*
