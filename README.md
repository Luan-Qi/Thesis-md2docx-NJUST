# Thesis-md2docx-NJUST

**南京理工大学硕士学位论文（学术硕士）的 Markdown → DOCX → PDF 导出工具。**

论文正文、图表、公式和参考文献用 Markdown 维护与版本管理；导出器把它们渲染成符合
《南理工硕士论文格式》的 Word 文档，并可直接导出 PDF 做版式检查。

本项目在架构上源自 [haodongcui/Thesis-md2docx](https://github.com/haodongcui/Thesis-md2docx)（MIT），详见 [来源与协议](#来源与协议)。

---

## 目录

- [快速开始](#快速开始)
- [Markdown 写法](#markdown-写法)
- [格式依据与规则来源](#格式依据与规则来源)
- [规范未明确的排版项](#规范未明确的排版项)
- [页面与分节结构](#页面与分节结构)
- [页眉、页脚与页码](#页眉页脚与页码)
- [匿名版与实名版](#匿名版与实名版)
- [已知行为与限制](#已知行为与限制)
- [项目结构](#项目结构)
- [扩展其他学校](#扩展其他学校)
- [测试](#测试)
- [来源与协议](#来源与协议)

> **第一次使用请先读这两份**：
> [`docs/markdown-format.md`](docs/markdown-format.md)（Markdown 内容格式 + 手把手使用步骤）、
> [`example/thesis-template.md`](example/thesis-template.md)（直接复制就能开始写的新论文骨架）。
>
> **要改这个项目本身的代码，先读 [`AGENT.md`](AGENT.md)**：里面记录了迭代过程、
> 已实测排除的假设，以及 Word / OOXML 的一堆隐性行为坑（域提示、分节符吞段前距、
> 双面排版插页、图片行距、封面与声明页的规范数值等）。

---

## 快速开始

### 环境

只需要 Python ≥ 3.10 与 Pillow；导出 PDF 需要本机装有 Microsoft Word（推荐）或 LibreOffice。

本项目在 `conda` 环境下验证通过。若使用仓库附带的 `conda-manual.ps1`：

```powershell
. "D:\Users\Desktop\HarnessThesis\conda-manual.ps1" myui
cd D:\Users\Desktop\HarnessThesis\Thesis-md2docx-NJUST
python -m pip install -e .
```

### 公式（可选，但建议安装）

公式会被转换成 Word 原生 OMML。转换依赖两个**公开 npm 包**（`temml`、`@hungknguyen/mathml2omml`，
均未被本项目修改，`package-lock.json` 中的 `resolved` 指向 `registry.npmjs.org`）：

```bash
npm install --prefix thesis_md2docx/math/latex2omml_node
```

不安装也能导出，公式会以 LaTeX 文本写入 DOCX。

### 常用命令

```bash
# 检查环境（同时校验 profile 的样式目录、语义角色与前置页计划）
md2docx check

# 生成 DOCX
md2docx example/thesis-demo.md --out example/output

# 生成 DOCX + PDF + 分页图
md2docx example/thesis-demo.md --pdf --pages --out example/output --backend word

# 只把已有 DOCX 转 PDF
md2docx pdf output/thesis.docx output/thesis.pdf --backend word

# 用 Word 刷新域，把真实目录页码写回 DOCX（生成后建议跑一次）
md2docx refresh-fields output/thesis.docx

# 对照学校范例审计版式
md2docx compare-docx reference.docx output/thesis.docx --out output/audit.md
md2docx compare-pdf reference.pdf output/thesis.pdf --out output/pdf-audit.md --diff-dir output/pdf-diff

# 封面像素级对版：把生成封面与学校参考封面各自经 Word 导出 PDF、同 DPI 渲染、逐线比较
python tools/compare_cover.py
```

`njust-master-thesis` 是唯一的 profile，也是默认 profile，因此普通导出不需要 `--profile`。
一键脚本 `export-example.ps1` / `.cmd` / `.sh` 会把示例论文完整导出到 `example/output/`。

### 目录页码：为什么需要 refresh-fields

生成 DOCX 时，目录里每一条的页码是**占位值**——真实页码只有在 Word 完成分页之后才存在。
把占位值换成真实页码有两条路：

```bash
# 推荐：由 Word 刷新后回存（需要本机有 Microsoft Word）
md2docx refresh-fields output/thesis.docx

# 或者在 Word 里打开文档，Ctrl+A 然后按 F9（或右键目录 → 更新域 → 更新整个目录），再保存
```

导出 PDF 时不需要这一步：`md2docx pdf --backend word` 会在导出前自动更新域，因此 PDF 里的目录页码
始终正确。

> **不要**用「给目录域加 `w:dirty`」或「打开 `w:updateFields`」来让 Word 自动刷新——那会让 Word 每次
> 打开文档都弹出「该文档包含的域可能引用了其他文件」，即使文档里没有任何外部引用。本项目两者都不写，
> 这也正是参考论文 `_anno.docx` 的做法。

### PDF 后端

| 后端 | 环境 | 定位 |
| --- | --- | --- |
| `word` | Windows + Microsoft Word | **推荐**，高保真，最终验收基准 |
| `libreoffice` | 跨平台，无需 Word | 快速预览，分页与字体可能与 Word 不一致 |
| `auto` | 任意 | 优先 `word`，否则 `libreoffice` |

> **不需要 LibreOffice**：本机装有 Word 时请直接用 `--backend word`。
> pandoc 与 MiKTeX **不能**替代这两个后端——pandoc 的 docx→pdf 会经过 LaTeX 重排而破坏 Word 版式，
> MiKTeX 只从 `.tex` 生成 PDF、不读 DOCX。

Word 自动化需要写入 `%APPDATA%\Microsoft\Word`。在受限沙箱中该路径可能被拒绝，此时为命令申请更宽的权限即可。

---

## Markdown 写法

**完整的内容格式与使用步骤见 [docs/markdown-format.md](docs/markdown-format.md)。**
想直接开始写，复制 [example/thesis-template.md](example/thesis-template.md)；
想看一份完整可导出的样例，看 [example/thesis-demo.md](example/thesis-demo.md)。

下面是速览版。

### 最小结构

```markdown
# 基于雷达-视觉融合的
不良天气船舶检测技术研究

## 封面信息
论文题目：基于雷达-视觉融合的
不良天气船舶检测技术研究
分类号：
密级：
UDC：
作者姓名：***
导师姓名：***
导师职称：教授
学位类别：工学硕士
学科名称：通信与信息系统
研究方向：交通智能感知
论文提交时间：2026 年 1 月

---

## 声明
研究生签名：
签字日期：

---

## 摘要
中文摘要正文。

关键词：关键词1，关键词2，关键词3

---

## ABSTRACT
English abstract.

Key word: keyword one, keyword two

---

## 目录
导出器会在此处写入 Word 目录域。

---

# 1 绪论
## 1.1 研究背景
正文。

# 2 …

# 5 结论与展望

# 致谢
# 参考文献
# 附录
## 附录A 附加材料
```

### 南理工特有的约定

| 项目 | 写法 | 说明 |
| --- | --- | --- |
| 正文起点 | `# 1 绪论` | 第一个以数字开头的一级标题；之前的 `##` 标题都是前置页 |
| 前置页 | `## 封面信息` / `## 声明` / `## 摘要` / `## ABSTRACT` / `## 目录` | **没有任务书**（南理工硕士论文不含该部分） |
| 声明页 | 只写 `研究生签名：` / `签字日期：` | 两段声明正文按附件 2.5 由导出器原样写入，Markdown 无法覆盖（规范要求内容不得改动） |
| 结论 | `# 5 结论与展望` 或独立的 `# 结论` | 两种写法都支持；后者不编号且强制另页 |
| 致谢 / 参考文献 / 附录 | `# 致谢` / `# 参考文献` / `# 附录` | 不编号，各自另页；顺序为 **结论 → 致谢 → 参考文献 → 附录** |
| 图题、表题 | `图2.1 xxx` / `表2.1 xxx`（单独成行） | 按章编号，点号分隔；表题在表上方，图题在图下方 |
| 附录图题、表题 | `图B1 xxx` / `表B1 xxx` | 附录内按字母编号；写成 `图 A-1` 也会被自动规范化 |
| 公式编号 | 自动生成 | 按章编号，格式 `（2.3）`；附录公式为 `（A.1）` |
| 公式引用 | `式（2.3）` | 与规范示例一致 |
| 关键词分隔 | 分号或逗号都可以 | 导出时统一改成逗号（中文 `，`、英文 `, `） |
| 参考文献引用 | `[1]`、`[1-3]`、`[1，3-4]` | 导出为上标并生成文末跳转 |

### 图表与公式语法

普通 Markdown 表格与 `$$ ... $$` 块公式直接可用。需要合并表头、固定列宽或控制三线表线宽时用
`::: table` 扩展语法：

```markdown
::: table {width=8525 width_type=dxa widths=2251,1546,1548,1547 top_border=12 bottom_border=12 header_rows=2}
| 项目 {rowspan=2} | 层流 {colspan=2} | 紊流 {colspan=2} |
| 0°截面 | 90°截面 | 0°截面 | 90°截面 |
| 理论值 | 0.04 | 0.03 | 1.30 | 1.25 |
:::
```

长表跨页时用 `<!-- thesis-table-split: 4 -->` 标记拆分点，导出器会重复表头并补 `（续）` 题注。
并排图用 `::: figure-row` … `:::` 包裹。完整参数列表见 [docs/usage.md](docs/usage.md)。

---

## 格式依据与规则来源

本项目严格区分三类规则来源：

| 类型 | 来源 | 用途 |
| --- | --- | --- |
| 明文规则 | 《南理工硕士论文格式.doc》正文条款 | 硬性约束，优先级最高 |
| 附件批注 | 同一文档附件 2.1–2.13 的文字说明与批注 | 逐项字号、字体、段距等参数 |
| 范例反推 | 学校已排版论文（`基于雷视融合…_anno.docx`） | 补齐规范未写清、但生成时必须确定的排版值 |

仓库里保留了两类依据材料：**原始文件**放在 `format_requirements/`（不提交到 Git），
**规则拆解稿**是根目录的 `format.md`：

```text
format.md                                    # 规范条款的拆解稿（含「原文未明确」清单）
format_requirements/
├── 南理工硕士论文格式.doc                      # 学校规范原文（正文条款 + 附件 2.1-2.13 + 59 条批注）
├── 南理工硕士论文格式.docx                     # 同一规范的 docx 版（可读附件 2.1/2.5 的段距与 run）
├── 基于雷视融合的不良天气船舶检测研究_anno.docx   # 学校已排版论文，用于范例反推与对照
├── 参考封面.docx                              # 从中抽出的封面 + 声明页，封面数值逐属性比对用
└── 校徽 + 校名 logo.png                       # 封面校徽与校名的源素材
```

封面校徽由导出器从随 profile 分发的副本
`thesis_md2docx/profiles/njust_master_thesis/assets/njust-logo.png` 读取，
因此 `format_requirements/` 缺失时仍能正常生成。换校徽时覆盖那个副本即可，
尺寸常数在 `constants.py`。详见 [format_requirements/README.md](format_requirements/README.md)。

当规范与范例冲突时，**以规范为准**；规范未明确的项目按下表取值。

---

## 规范未明确的排版项

规范（含其附件批注）明确把下列项目列为"原文未明确"，并要求不依据模板实际格式反推。
但自动生成必须给出确定值，因此这里逐项记录采用值，便于复核与覆盖。

| 项目 | 规范表述 | 本项目采用值 | 依据 |
| --- | --- | --- | --- |
| 封面字段位置 | 未明确 | 标签首行缩进 843 twips，值列制表位 4200 twips | 范例反推；原范例 8280 的制表位被 Tab 触发时会使值折行，故左移 |
| 封面题名/作者下方横线 | 未明确 | **每行题名各一条** 140.5mm（单行题名也补画第二条），作者姓名下 **50.7mm**；均居中、粗 0.75pt | 范例 `mc:AlternateContent` 里 wps 浮动线的 `cx` 实测（5057775 / 1824990 EMU，两条题名线相距 11mm） |
| 横线的实现方式 | — | 段落下框线 + 左右等距缩进 | 不引入 VML/形状；代价是线只能落在段落底部（作者线比范例低 2.1mm） |
| 封面填空位宽度与值的对齐 | 未明确 | 六行下划线**等宽 86.8mm（246pt）**，值**居中**在填空位里（中心距填空位起点 113.1pt） | 范例像素实测：六条线都 69.6→156.4mm，三条中文值的中心都在 109.5mm |
| 封面顶部的段前 | 规范 156 / 范例 163 | `before=163` + `beforeLines=50`（Word 取 0.5 行 = 10pt） | 范例；两个值都写，实际以 beforeLines 为准 |
| 「论文提交时间」行的字符间距 | 未明确 | 文字 run 加 `w:spacing=-10`（-0.5pt），空格不加（否则下划线会缩短） | 范例该行所有 run 都是 -10 |
| UDC 行「注1」的字体 | 未明确 | 华文中宋，上标 + 下划线 | 范例该 run 写死 `w:eastAsia="华文中宋"` |
| 声明页标题行距 | 未明确 | 「声  明」固定值 20 磅；「学位论文使用授权声明」单倍 | 范例：前者无 spacing 覆盖（继承 Normal），后者显式 `line=240 auto` |
| 声明页行距（★★） | 未明确 | 该页段落**吸附行网格**：节的 `docGrid type="linesAndChars" linePitch="326"`，14pt 正文吸附成 **2 格 = 32.6pt**；空行的字号写进 `pPr/rPr` | 范例该页每个段落都带 `<w:snapToGrid/>`，且空行的段落标记写 `sz=28`（16pt 标题后那条写 `sz=32`） |
| 声明页签名下划线长度 | 未明确 | 声明页 12 个空格、授权页 13 个，其后 13 个普通空格 | 范例逐 run 实测 |
| 封面「32号楷体」磅值 | 未明确 | 32pt 楷体加粗 | 学校排版件 `w:sz=64` |
| 封面未批注字段的字体 | 未明确 | 四号宋体加粗 | 与已批注的「学位类别」标签一致 |
| 正文首行缩进 | 未明确 | 2 字符（firstLineChars=200 / 480 twips） | 范例 |
| 目录缩进与制表位 | 未明确 | TOC1 = 0、TOC2 = 420、TOC3 = 839 twips；右对齐点线制表位 9070 twips | 范例 |
| 参考文献悬挂缩进 | 未明确 | 0（不悬挂） | 规范未明确则不设；如需悬挂改 `styles.py` 中的 `STYLE_REFERENCE` |
| 图题对齐与段距 | 未明确 | 居中、段前段后 0、固定值 20 磅 | 范例 |
| 图片默认宽度 / 居中 / 环绕 | 未明确 | 居中、段前后 0；宽度按图片 DPI 与页面宽度推导 | 范例 |
| 公式居中与编号右对齐 | 未明确 | 居中制表位 4535 + 右对齐制表位 9070 | 范例 |
| 表格三线表与边框粗细 | 未明确 | 正文表格默认三线表（上下线 1.5 磅、无内线） | 范例；可用 `::: table` 逐表覆盖 |
| 表内行距 | 未明确 | 单倍行距 | 避免固定行距裁切单元格 |
| 页眉横线 | 未明确 | 单线 0.75 磅（`w:sz="6"`） | 范例 |
| 附录公式编号 | 未明确 | `（A.1）`、`（B.3）` | 与规范 11.4 的 `图B1`／`表B1` 保持一致 |
| 伪代码 / 算法 | 未规定 | 不设专用样式，按普通正文与代码块渲染 | 规范未设规则 |

其余项目均按规范明文或附件批注实现，例如：页面 30/24/25/25mm、固定值 20 磅行距、
一级标题小三号加粗居左段前后 18 磅、二级四号 12 磅、三级小四 6 磅、
摘要/Abstract/目录/致谢/参考文献/附录标题三号加粗居中段前后 18 磅
（目录标题上空按规范批注为 18mm，见 `constants.BEFORE_TOC_TITLE`）。

---

## 页面与分节结构

规范 2.1 / 3.1 / 3.2 要求：

```text
A 节   封面 + 声明 / 学位论文使用授权声明     隐藏页眉与页码
B 节   中文摘要 + 英文摘要 + 目录             显示页眉，罗马数字页码（从 I 起）
C 节   绪论 … 附录                            显示页眉，阿拉伯数字页码（从 1 起）
```

页边距 A4、上 30mm、下 24mm、左右各 25mm（正文可用宽度 160mm）、页眉页脚距边界各 20mm，
并启用对称页边距。

**正文每一章不强制另页**（规范 3.2）；只有 结论 / 致谢 / 参考文献 / 附录 另页开始。

---

## 页眉、页脚与页码

规范 11.1 / 11.2：

| 位置 | 内容 |
| --- | --- |
| 奇数页页眉 | 左「硕士学位论文」 + 右「本论文题目」 |
| 偶数页页眉 | 左「章节号和章节名」（`STYLEREF` 域） + 右「硕士学位论文」 |
| 奇数页页脚 | 页码，靠右（页面外侧） |
| 偶数页页脚 | 页码，靠左（页面外侧） |

页眉为小五号（9pt）宋体，西文 Times New Roman；页眉段落左对齐，左右缩进与首行缩进均为 0，
用一个落在正文右边界（160mm）的右对齐制表位定位右侧内容。

实现上需要**奇偶页不同的页眉页脚**：`word/header3.xml` 与 `word/footer3.xml` 是两个额外部件，
`settings.xml` 打开 `<w:evenAndOddHeaders/>`，各节通过 `headerReference type="even"` 引用。

---

## 匿名版与实名版

`example/thesis-demo.md` 是**匿名版**：`作者姓名` 与 `导师姓名` 用 `***` 占位
（规范 11.5 匿名送审要求隐去作者与导师信息），分类号、密级、UDC 留空。

实名提交时只需修改 Markdown 前置区的对应字段，无需改动代码：

```markdown
## 封面信息
分类号：TP391
密级：★ 公开
UDC：621.3
作者姓名：张三
导师姓名：李四
导师职称：教授
```

密级若填写，须以 `★` 标注并注明保密期限。声明页的签名与日期可写在 `## 声明` 小节内，
留空则打印空白下划线。

---

## 已知行为与限制

1. **打开生成的 DOCX 时不会弹出「该文档包含的域可能引用了其他文件」。**

   触发这个提示的是两件事，本项目两者都不写：

   | 触发条件 | 说明 | 本项目 |
   | --- | --- | --- |
   | `<w:updateFields w:val="true"/>` | 让 Word 在打开时更新**所有**域 | 不写 |
   | 任何 `w:dirty="true"` 的域 | 让 Word 在打开时更新**该**域；目录域最容易踩到 | 不写 |

   Word 对「有待更新的域」一律使用上述措辞，即使文档里只有引用文档自身的目录域和 PAGEREF 域。
   实测确认：生成的 DOCX 里 `dirty` 域数量为 0、无 `updateFields`，且所有 `.rels` 中没有
   `TargetMode="External"`、没有 `INCLUDETEXT` / `INCLUDEPICTURE` / `RD` 等外部引用域，
   任何部件里都不含文件路径字符串。参考论文 `_anno.docx` 也是同样的结构，所以它不弹。

   代价是目录页码需要刷新一次——见[目录页码：为什么需要 refresh-fields](#目录页码为什么需要-refresh-fields)。

2. **「目录」之后可能多出一页只有页眉与页码的页面（成因已定位，已缓解）。**

   > **当前状态**：前置部分现在**逐页分节**（摘要 / Abstract / 目录 各自成节，见
   > `document.py` 的 `front_continue_sect`）。这既让各页标题的段前距生效，也让前置部分
   > 更容易凑成偶数页——本示例为 4 页，正文正好落在奇数页，因此**不再出现这一页**。
   > 但页数奇偶仍取决于目录长度，换一篇论文仍可能复现，故保留下面的成因与取舍说明。

   现象：目录页（罗马数字 III）之后出现一页罗马数字 IV，没有正文，只有页眉与页码；
   正文顺延到再下一页，从阿拉伯数字 1 开始。逐页像素检测确认它不是文本提取的假象
   （该页墨迹约 0.07%）。在 Word 中打开也在同一页，`docProps/app.xml` 记录的页数与 PDF 一致。

   **根因**：只要文档带有「双面排版」属性，Word 就会在**重启页码的分节**处插入一页，
   让重启后的第 1 页（奇数）落在奇数物理页上。触发「双面排版」的是下面两个设置中的**任意一个**：

   - `<w:evenAndOddHeaders/>` —— 规范 11.1 要求奇偶页眉不同，**必须保留**
   - `<w:mirrorMargins/>` —— 规范 2.1 的「对称页边距」；因左右同为 25mm，它本身没有视觉效果

   判断依据是**前置部分的页数奇偶**：前置部分为奇数页时，正文落在偶数物理页，
   Word 就插一页把它推到奇数页。改版前本示例的前置部分为 5 页（封面、声明、摘要、
   Abstract、目录），恰好是奇数，因此会多出这一页；逐页分节后变成 4 页（目录跨到第二页），
   正文落在第 7 页（奇数），于是不再需要插页。

   已实测**排除**的原因：目录长度（5 条与 30 条同样出现）、目录标题段前段后（压到 0 也出现）、
   `w:type` 取值、分节段高度与是否独立成段、导出前是否更新域、`ExportAsFixedFormat` 与
   `SaveAs2` 的差别。

   实测可行的规避方式及其代价：

   | 方式 | 空页 | 页码 | 代价 |
   | --- | --- | --- | --- |
   | 同时去掉奇偶页眉与对称页边距 | 无 | 正确 | 偶数页页眉与奇数页相同，**违反规范 11.1** |
   | 正文节不重启页码 | 无 | 4/5… | 正文不从 1 开始，违反规范 6 |
   | 正文节改用 `evenPage` | 无 | 2/3… | 正文从 2 开始，违反规范 6 |
   | 前置部分占偶数页 | 无 | 正确 | 依赖前置内容恰好凑成偶数页，无法先验保证 |
   | **逐页分节（当前做法）** | 本示例无 | 正确 | 不致保证——前置页数仍随目录长度变化 |
   | 去掉奇偶页眉（仅当学校不强制） | 无 | 正确 | 偶数页页眉与奇数页相同，**违反规范 11.1** |

   当前采用逐页分节：它既让各页标题的段前距生效，也顺带把本示例的前置部分凑成偶数页。
   如果换一篇论文后这一页又出现，可选的做法是调整前置部分的分页使其为偶数页，
   或按上表评估取舍。真要彻底去掉，就改
   `thesis_md2docx/profiles/njust_master_thesis/styles.py` 的 `njust_settings_xml()`，
   不再传 `even_and_odd_headers=True` 与 `mirror_margins=True`（代价是偶数页页眉）。

3. **公式以 OMML 输出，不生成 MathType/OLE 公式对象。**
   源论文中若含 OLE 公式对象，重新生成后会是可编辑的 Word 公式而非 OLE 对象，视觉一致但对象类型不同。

4. **只实现学术硕士版本。** 专业硕士封面使用「硕士专业学位论文」与「专 业 名 称」标签，
   当前未实现；需要时按 `njust_master_thesis` 的写法新增一个 profile。

5. **不覆盖浮动对象、脚注尾注、修订痕迹等深度 Word 排版。**

6. **最终验收仍需在 Word/WPS 中人工确认**分页、图表跨页、孤行与页码。

---

## 项目结构

```text
Thesis-md2docx-NJUST/
├── md2docx.py                          # 统一入口
├── thesis_md2docx/
│   ├── profiles/
│   │   └── njust_master_thesis/        # 唯一的格式实现
│   │       ├── profile.py              #   页面几何、分节、封面资源、装配入口
│   │       ├── constants.py            #   规范数值：页面、字号、段距、封面坐标
│   │       ├── styles.py               #   20 个 Word 样式 + 编号 + 字体表 + 奇偶页设置
│   │       ├── frontmatter.py          #   封面 / 双声明 / 中英摘要 / 关键词 / 目录标题
│   │       ├── body.py                 #   解析规则与渲染钩子
│   │       ├── header_footer.py        #   奇偶页眉、外侧页码
│   │       ├── document.py             #   三节装配
│   │       ├── assets/njust-logo.png
│   │       └── format_requirements/    #   规则出处说明
│   ├── builders/                       # 通用 IR -> OOXML 调度
│   ├── ooxml/                          # 段落、表格、图片、包部件
│   ├── styles/                         # 样式目录、语义角色、编号、字体表
│   ├── math/                           # LaTeX -> OMML
│   ├── pdf/                            # DOCX -> PDF 后端（含 Word 刷新域）
│   └── audit.py / pdf_compare.py       # 版式审计
├── example/
│   ├── thesis-template.md              # 新论文骨架，直接复制着写
│   ├── thesis-demo.md                  # 完整示例（可导出）
│   └── output/                         # 示例导出产物
├── docs/
│   ├── markdown-format.md              # ★ Markdown 内容格式与使用指南
│   ├── usage.md                        # 元素语法参考
│   ├── profiles.md                     # profile 扩展指南
│   └── backends.md                     # PDF 后端
├── skill/                              # Agent skill
├── tests/
├── tools/
│   ├── regenerate_golden.py            # 有意改格式后重生 OOXML golden 哈希
│   └── compare_cover.py                # 封面像素级对版（参考封面 vs 生成封面）
├── format.md                           # 规范条款拆解稿
└── format_requirements/                # 学校原始依据材料（不提交）
    ├── 南理工硕士论文格式.doc
    ├── 南理工硕士论文格式.docx
    ├── 基于雷视融合..._anno.docx
    ├── 参考封面.docx                     # 封面 + 声明页抽取件（对版基准）
    └── 校徽 + 校名 logo.png
```

---

## 扩展其他学校

仓库当前的 `njust_master_thesis` 就是一个完整范例。新增学校或学位时：

1. 新建 `thesis_md2docx/profiles/<school>_<degree>_thesis/`，按上面的文件清单实现
   `profile.py`、`styles.py`、`frontmatter.py`、`body.py`、`header_footer.py`、`document.py`。
2. 在 `profiles/registry.py` 的 `PROFILES` 中注册，并决定是否改 `DEFAULT_PROFILE_NAME`。
3. 把学校原始规范与范例放到根目录的 `format_requirements/`，并在 profile 的
   `format_requirements/` 中说明来源。

页面尺寸与页边距通过 `PageGeometry` 传入，不需要改动通用层：

```python
from thesis_md2docx.layout import PageGeometry, mm

PAGE_GEOMETRY = PageGeometry(
    width=11906, height=mm(297),
    top=mm(30), bottom=mm(24), left=mm(25), right=mm(25),
    header=mm(20), footer=mm(20), mirror_margins=True,
)
```

`md2docx check` 会校验默认 profile 的样式目录、必需语义角色、前置页计划与正文渲染 profile，
能提前发现样式 id 重复、`basedOn` 悬空、角色未覆盖等问题。

---

## 测试

```bash
python -m pip install -e ".[dev]"
python -m pytest tests
```

导出格式改动后，若确认是**有意**改动，用下列命令更新 golden 哈希：

```bash
python tools/regenerate_golden.py
```

提交前建议完整跑一遍：

```bash
python -m pytest tests
md2docx check
md2docx example/thesis-demo.md --pdf --pages --out example/output --backend word
python tools/compare_cover.py        # 封面像素对版，超差退出码 1
```

`tools/compare_cover.py` 会把 `format_requirements/参考封面.docx` 与当前生成的封面
各自经 Word 导出 PDF、以同一 DPI 渲染成 PNG，然后逐条量横线的起点/长度/竖直位置并打印
对照表（默认容差 2.5mm，报告写到 `example/output/cover-audit.md`）。改动封面相关代码后
一定要跑它——`regenerate_golden.py` 只锁 OOXML 字节，锁不住"线画歪了"。
它的前置条件与 `md2docx pdf --backend word` 相同（需要 Microsoft Word 与 `pdftoppm`）。

> **受限环境提示**：pytest 的 `tmp_path` 需要在临时目录中创建并枚举子目录。若运行环境禁止
> 目录枚举（例如某些沙箱），依赖 `tmp_path` 的用例会以 `PermissionError` 报错，
> 这属于环境限制而非用例失败。此时可改用 `--basetemp` 指向可写目录，或在不受限环境中运行。

---

## 来源与协议

本项目在**架构与通用引擎**上源自
[haodongcui/Thesis-md2docx](https://github.com/haodongcui/Thesis-md2docx)：profile 分层、
Markdown → 中间表示 → 手写 OOXML 的转换链路、样式/编号/字体表的结构化声明、DOCX→PDF 双后端，
以及格式审计工具都来自上游。

在此之上，本仓库把**格式层替换为原生的南京理工大学硕士学位论文实现**：

- `thesis_md2docx/profiles/njust_master_thesis/` 是仓库里唯一的 profile，也是默认 profile；
  不携带任何其他学校的模板、示例、封面资源或测试。
- 通用层按南理工的需要做了追加式扩展（`PageGeometry`、奇偶页眉页脚部件、四级标题、
  按标题另页、目录段落参数可配置、OMML 命名空间前缀），并且这些扩展对不使用它们的人没有副作用。
- 页面几何、封面资源文件名、默认 profile、环境自检等原先写死为上游学校的地方都已改为
  profile 驱动，仓库中不再出现上游学校的名称或文件名。

**License：MIT**，版权声明保留上游署名：

```text
MIT License

Copyright (c) 2026 xju-thesis-md2docx contributors
```

本仓库对上游代码与架构的复用、修改与再分发均遵循 MIT 协议；新增的南京理工大学格式实现
同样以 MIT 协议发布。完整协议文本见 [LICENSE](LICENSE)。
