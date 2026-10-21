# Usage Guide

本文档说明南京理工大学硕士学位论文的 Markdown 源稿应该怎样组织，以及常见论文元素应该怎样写。
建议先复制 `example/thesis-demo.md`，再逐步替换为自己的论文内容。

## 输出文件建议

直接导出模式的 `--out` 表示输出目录；不传 `--out` 时，默认写入 Markdown 同级的 `output/`。
建议源稿和生成物分开：

```text
paper/
├── thesis.md
├── img/
└── output/
    ├── thesis.docx
    ├── thesis.pdf
    └── pages/
```

Markdown 和 `img/` 是源文件；`output/` 是可删除、可重建的导出产物目录。

## 基本结构

开始写作前建议先检查环境：

```bash
md2docx check
```

如果有公式，建议安装公式依赖：

```bash
npm install --prefix thesis_md2docx/math/latex2omml_node
```

推荐结构如下：

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
这里可以放占位文字；导出器会写入 Word 目录域。

---

# 1 绪论
## 1.1 研究背景
### 1.1.1 三级标题示例
正文。

# 2 …

# 5 结论与展望

# 致谢
致谢正文。

# 参考文献
[1] 作者. 文献题名[文献类型]. 出版信息.

# 附录
## 附录A 附加材料
附录正文。
```

注意顺序：南理工要求 **结论 → 致谢 → 参考文献 → 附录**，且 致谢/参考文献/附录 各自另页开始。

## 前置部分

前置部分使用二级标题组织。`njust-master-thesis` profile 识别这些标题：

- `## 封面信息`
- `## 声明`
- `## 摘要`
- `## ABSTRACT`
- `## 目录`

南理工硕士论文**没有任务书**，Markdown 里写了 `## 任务书` 也不会被渲染。

### 封面信息

字段名建议使用中文冒号或英文冒号，并保持稳定：

```markdown
论文题目：基于雷达-视觉融合的
不良天气船舶检测技术研究
分类号：TP391
密级：★ 公开
UDC：621.3
作者姓名：张三
导师姓名：李四
导师职称：教授
学位类别：工学硕士
学科名称：通信与信息系统
研究方向：交通智能感知
论文提交时间：2026 年 1 月
```

约定：

- `论文题目` 可以写多行，封面会按行显示；页眉会自动合并成一行。
- `分类号`、`密级`、`UDC` 留空时，封面打印空白下划线。
- 匿名送审时把 `作者姓名`、`导师姓名` 写成 `***`。
- `导师职称` 会显示在导师姓名下方的同一列。
- `学位类别` 学术硕士填 `工学硕士`，专业硕士填 `工程硕士`，并把 `学科名称` 改为 `专业名称`
  （南理工专业硕士封面用「专 业 名 称」标签，本项目当前实现的是学术硕士版本）。

### 声明

声明页由**两段固定声明**组成：`声明` 与 `学位论文使用授权声明`（规范附件 2.5）。
正文内容由导出器原样写入，**不要在 Markdown 里覆盖**；Markdown 只需要给出签名与日期：

```markdown
## 声明
研究生签名：
签字日期：
```

留空时打印空白下划线；如需电子签名图片，可写成图片引用：

```markdown
研究生签名：![电子签名](img/signature.png)
```

两段声明排在同一页的上、下两部分。

### 摘要与关键词

```markdown
## 摘要
中文摘要正文，400—600 字。

关键词：关键词1，关键词2，关键词3

---

## ABSTRACT
English abstract.

Key word: keyword one, keyword two
```

- `摘要` 与 `Abstract` 都是**不编号的一级标题**，会自动进入目录。
- 关键词与摘要正文之间会保留 2 个空白段落。
- 关键词分隔符用分号或逗号都可以，导出时统一改成逗号（中文 `，`、英文 `, `）。
- 中英文关键词行都不缩进。

### 目录

```markdown
## 目录
导出器会在此处写入 Word 目录域。
```

`目录` 小节里的文字会被忽略，导出器写入 Word 目录域并生成书签与页码引用。
目录列出 一、二、三级标题及致谢、参考文献、附录。

## 正文标题

正文从第一个编号一级标题开始：

```markdown
# 1 绪论
## 1.1 研究背景
### 1.1.1 三级标题示例
#### 1.1.1.1 四级标题示例
```

注意：

- 支持一到四级标题；一级到三级进入目录。
- 一级标题建议写成 `# 1 绪论`，二级 `## 1.1 研究背景`，三级 `### 1.1.1 …`，四级 `#### 1.1.1.1 …`。
- 导出器使用 Word 原生编号，不会把编号硬编码进标题文本。
- 规范 3.2 只要求 结论 / 致谢 / 参考文献 / 附录 另页；**正文每一章不强制另页**。

## 段落

普通正文直接写 Markdown 段落即可。软换行会被合并成同一个段落，空行会结束当前段落。

```markdown
这是第一段正文。正文段落按南京理工大学格式设置为小四号宋体、首行缩进两字符、固定值 20 磅行距。

这是第二段正文。
```

如果需要保留 Word 段落内部的人工换行，可以在 Markdown 行末写两个空格，或写反斜杠：

```markdown
这一行导出后仍会在同一段落内换行。\
这一行不会被合并到上一行末尾。
```

普通论文正文不建议大量手动断行；只有复刻学校范例、固定封面字段或控制个别段落分页时才建议使用。

引用块和代码块支持基础导出：

````markdown
> 这是一段引用说明。

```python
def example():
    return "hello"
```
````

代码块只适合少量示例，不建议放大段程序。

## 图片

图片建议放在 Markdown 同级目录下的 `img/` 中，并使用相对路径：

```markdown
![实验流程图](img/pipeline.png)
图2.1 实验流程图
```

约定：

- 规范 7：图号按章编排，形如 `图2.1`，图号与图名之间空一格。
- 图题单独成行，写在图片下方。
- 图题与图内文字为五号宋体，西文 Times New Roman。
- 图片缺失时导出器会放置占位文本，最终提交前必须检查。

如果需要复刻模板中的精确图片尺寸，可以在图片后追加尺寸属性：

```markdown
![实验流程图](img/pipeline.png){width_emu=4942840 height_emu=2432685 crop_bottom=7802}
```

`width_emu` 和 `height_emu` 使用 Word OOXML 的 EMU 单位；只写其中一个时会按图片原比例自动计算另一个。
`crop_top` / `crop_right` / `crop_bottom` / `crop_left` 使用 OOXML 的千分之一百分比裁剪值，适合复刻范例里
被 Word 手动裁剪过的图片。普通写作通常不需要这些属性。

需要复刻图片所在段落的样式和段前段后时，也可以追加图片段落属性：

```markdown
![图2.2 标题](img/figure.png){width_emu=4942840 height_emu=2432685 p_style=NjustCaption align=none line=400 before=0 after=0 keep_next=false}
```

常用属性包括 `p_style`、`align`、`line`、`before`、`after`、`before_lines`、`after_lines`、
`mark_style` 和 `keep_next`。这些属性偏底层，主要用于复刻范例，不建议普通写作时频繁手调。

## 并排图

并排图使用 `:::figure-row` 容器：

```markdown
:::figure-row
![方法 A](img/method-a.png)
![方法 B](img/method-b.png)
:::
图3.2 不同方法的可视化对比
```

建议并排图数量保持在 2 张。图片尺寸差异过大时，应先裁剪或统一图片比例，再导出。

## 表格

普通 Markdown 管道表格可以直接写：

```markdown
表2.1 实验参数设置

| 参数 | 取值 | 说明 |
| --- | --- | --- |
| 学习率 | 0.001 | 优化器初始学习率 |
| 批大小 | 64 | 每轮训练样本数 |
```

约定：

- 规范 8：表号按章编排，形如 `表2.1`，表号与表名之间空一格。
- 表题放在表格**上**一行。
- 表题及表内文字为五号宋体，数字与西文为 Times New Roman。
- 表格不适合写得过宽，列太多时建议拆分。

长表可以在表题和表格之间添加拆分标记：

```markdown
表4.3 长表结果

<!-- thesis-table-split: 8, 10 -->

| 指标 | 实验1 | 实验2 |
| --- | --- | --- |
| ... | ... | ... |
```

标记中的数字表示按数据行拆分续表，例如 `8, 10` 表示第一段 8 行，第二段 10 行，剩余行自动进入后续表；
每段续表都会重复表头并补 `（续）` 题注。

复杂表格使用 `::: table` 扩展语法，用于合并表头、固定列宽和特殊三线表线宽：

```markdown
表1.2 方弯管内流动最大速度比较

::: table {width=8529 width_type=dxa widths=2251,1546,1548,1547,1637 top_border=12 bottom_border=12 header_rows=2 header_bold=false}
| 项目 {rowspan=2 continue_left=44 continue_first_line=1764 continue_first_line_chars=840} | 层流 {colspan=2} | 紊流 {colspan=2} |
| 0°截面 | 90°截面 | 0°截面 | 90°截面 |
| 理论值 Vmax/m·s-1 | 0.04 | 0.03 | 1.30 | 1.25 |
| 计算值 Vmax/m·s-1 | 0.04 | 0.03 | 1.26 | 1.21 |
:::
```

可用参数：

- `width` / `width_type`：表格总宽度和单位，常用 `width_type=dxa` 或 `pct`。
- `widths`：逗号分隔的列宽，单位 dxa。
- `top_border` / `mid_border` / `bottom_border`：顶线、中线、底线线宽，OOXML 中 `8` 约等于 1 磅，
  `12` 约等于 1.5 磅。规范未规定三线表线宽，本项目默认按学校范例取上下线 1.5 磅、无内线。
- `header_rows`：没有 Markdown 分隔线时，显式声明前几行是表头。
- `header_bold=false`：表头不加粗。
- `caption="表2.1 标题"`：把表题作为表格第一行。
- `row_height` / `row_heights`：设置统一行高或逐行行高，单位 dxa。
- `repeat_header_rows` / `cant_split_rows`：精确控制重复表头行和禁止跨页拆分的行。
- `layout` / `look` / `cell_margins`：控制底层 Word 表布局、`tblLook` 和表格单元格边距。
- `cell_width_type` / `cell_widths`：当表宽用 `pct` 但网格列宽仍用 dxa 时，可单独控制单元格 `tcW`。
- `cell_style=none` / `font_size=inherit` / `paragraph_after=omit`：少写直接属性，尽量复刻模板继承出来的单元格样式。
- `header_bold_cs=true` / `rowspan_restart_bottom_border=false`：复刻复杂表头里只写复杂字体加粗、纵向合并起始格不写底线的情况。
- `body_bold_cs=true`：复刻表体 run 带复杂字体加粗标记的情况。
- `paragraph_first_line` / `paragraph_first_line_chars` / `header_top_border_size`：控制单元格内段落缩进和表头单元格顶线粗细。
- `row_top_borders` / `row_bottom_borders`：逐行声明单元格顶线/底线，值可写 `12`、`8`、`nil`、`none`。
- 单元格 `{colspan=2}`、`{rowspan=2}`：横向/纵向合并。
- 单元格 `{left=44}`、`{first_line=480}`、`{first_line_chars=200}`：覆盖单个单元格内段落缩进。
- 单元格 `{continue_left=44}`、`{continue_first_line=1764}`、`{continue_first_line_chars=840}`：覆盖纵向合并续接单元格的段落缩进。
- 单元格 `{bold_cs=false}`、`{style=10}`、`{font_size=21}`、`{font_size_cs=false}`、`{first_line=omit}`：覆盖单元格内 run 和段落属性。
- `{{sym:Times New Roman:0000}}` 可写入 Word 符号 run。
- `{{sup:-1}}` / `{{sub:max}}` 可写入 Word 上标/下标 run；结合 `*...*` 可表达斜体变量下标，如 `*V{{sub:max}}*`。

## 公式

行内公式使用单个 `$`：

```markdown
状态表示为 $s_t$，动作表示为 $a_t$。
```

块公式使用独立的 `$$`：

```markdown
$$
J(\theta)=\mathbb{E}_{\tau \sim \pi_\theta}\left[\sum_{t=0}^{T}\gamma^t r_t\right]
$$
```

公式**自动按章编号**，格式为 `（2.3）`，其中 `2` 是所在章号；附录中的公式按附录字母编号，如 `（B.3）`。
正文引用写成 `式（2.3）`。

如果安装了公式转换依赖，公式会尽量转换为 Word 原生 OMML；否则会以 LaTeX 文本保底导出。

需要复刻 Word 模板中已经排好的公式视觉效果时，可以给公式块指定图片：

```markdown
$$ {image=img/formula-1-1.wmf image_alt="公式1.1" width_emu=750570 height_emu=284480}
q = k_d H^x
$$
```

这种写法保留 LaTeX 作为源文本，但导出时优先嵌入 `image` 指定的图片，并继续使用自动公式编号。
`width_emu` / `height_emu` 使用 Word OOXML 的 EMU 单位；普通写作优先使用纯 LaTeX 公式。

安装公式依赖：

```bash
cd thesis_md2docx/math/latex2omml_node
npm install
```

常见 `\hat{}`、`\bar{}` 等重音公式已经有后处理，但复杂公式仍建议最终在 Word/WPS 中检查。

## 参考文献与引用

正文引用建议写成：

```markdown
已有研究表明该方法能够提升样本效率[1-2]。
也可以引用多个来源[1，3-4]。
```

参考文献列表写在 `# 参考文献` 后：

```markdown
# 参考文献

[1] 作者. 文献题名[文献类型]. 出版信息.
[2] 作者. 文献题名[文献类型]. 出版信息.
```

- 规范 11.3：条目为小四号宋体、固定值 20 磅行距，西文 Times New Roman。
- 规范允许 `文献[4]` 或右上角标注 `[4]`，两种写法都可以。
- 导出器会生成正文上标引用和文末跳转链接。
- 规范 13 把「悬挂缩进」列为未明确，本项目默认不设悬挂缩进；如需悬挂缩进，改
  `thesis_md2docx/profiles/njust_master_thesis/styles.py` 中的 `STYLE_REFERENCE`。
- 参考文献条目的真实性和 GB/T 7714 细节仍需要人工核对。

## 致谢和附录

致谢使用一级标题，不编号、另页开始：

```markdown
# 致谢

致谢正文。
```

附录结构：

```markdown
# 附录

## 附录A 附加材料

附录正文。
```

- 附录标题会规范化为 `附录A`、`附录B`…；写成 `## 附录 A 附加材料` 也可以。
- 规范 11.4：附录图表编号为 `图B1`、`表B1`（字母 + 序号，无点号），写成 `图 B-1` 会被自动规范化。

## 常见问题

- 不要把正文内容写在 `## 目录` 前面，否则可能被当作前置部分。
- 不要跳过一级标题直接从 `## 1.1` 开始正文。
- 图题、表题不要和正文混在同一段。
- 图片路径尽量使用相对路径，不要使用本机绝对路径。
- 生成 DOCX 后建议在 Word/WPS 中确认目录页码与分页；目录域带 `dirty` 标记，Word 打开时会自动刷新。
- 最终提交前必须人工检查分页、孤行、表格跨页、公式和参考文献格式。

## 推荐导出流程

日常写作时：

```bash
md2docx thesis.md
```

需要预览版式时：

```bash
md2docx thesis.md --pdf --pages --out output --backend auto
```

最终检查时，优先使用 Microsoft Word 后端导出 PDF：

```bash
md2docx thesis.md --pdf --out output --backend word
```

导出 PDF 时 Word 会顺带更新域，因此 PDF 里的目录页码始终正确。但**提交用的 DOCX** 需要单独刷新一次
目录页码，否则目录里显示的是生成时的占位值：

```bash
md2docx thesis.md --out output
md2docx refresh-fields output/thesis.docx
```

`refresh-fields` 用 Word 打开文档、更新所有域并把结果存回原文件。刷新后的文档既没有
`w:dirty` 域也没有 `w:updateFields`，所以以后每次打开都不会再弹出
「该文档包含的域可能引用了其他文件」。

如果本机没有 Word，也可以在 Word/WPS 里手动打开文档，`Ctrl+A` 后按 `F9`
（或右键目录 → 更新域 → 更新整个目录），再保存。

LibreOffice 后端适合快速预览或没有 Word 的环境，但最终分页和字体效果仍以 Word/WPS 人工检查为准。
仓库里的 `export-example.ps1` / `.cmd` / `.sh` 会把示例论文完整导出到 `example/output/`，
并在有 Word 时顺便刷新目录页码。

如果要和学校范例或历史版本做视觉回归，可以对比 PDF 页面像素：

```bash
md2docx compare-pdf reference.pdf output/thesis.pdf --out output/pdf-audit.md --diff-dir output/pdf-diff
```

`--diff-dir` 会为存在差异的页面生成红色差异图。该命令依赖 `pdftoppm`，DPI 可用 `--dpi` 调整。
