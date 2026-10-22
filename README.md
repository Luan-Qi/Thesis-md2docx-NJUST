# Thesis-md2docx-NJUST

**南京理工大学硕士学位论文（学术硕士）的 Markdown → DOCX → PDF 导出工具。**

论文正文、图表、公式和参考文献用 Markdown 维护与版本管理；导出器把它们渲染成符合
《南理工硕士论文格式》的 Word 文档，并可直接导出 PDF 做版式检查。

本项目在架构上源自 [haodongcui/Thesis-md2docx](https://github.com/haodongcui/Thesis-md2docx)（MIT），详见 [来源与协议](#来源与协议)。

---

## 目录

- [快速开始](#快速开始)
  - [1. 准备 Python 环境](#1-准备-python-环境)
  - [2. 怎么运行它（最容易踩的坑）](#2-怎么运行它最容易踩的坑)
  - [3. 公式依赖（可选）](#3-公式依赖可选)
  - [4. 常用命令](#4-常用命令)
  - [5. 目录页码：为什么需要 refresh-fields](#5-目录页码为什么需要-refresh-fields)
  - [6. PDF 后端](#6-pdf-后端)
- [Markdown 写法](#markdown-写法)
- [格式依据与规则来源](#格式依据与规则来源)
- [页面与分节结构](#页面与分节结构)
- [页眉、页脚与页码](#页眉页脚与页码)
- [匿名版与实名版](#匿名版与实名版)
- [使用提醒](#使用提醒)
- [项目结构](#项目结构)
- [扩展其他学校](#扩展其他学校)
- [测试](#测试)
- [来源与协议](#来源与协议)

> **AGENT使用请直接让他读这两份**：
> [`docs/markdown-format.md`](docs/markdown-format.md)（Markdown 内容格式 + 手把手使用步骤）、
> [`example/thesis-template.md`](example/thesis-template.md)（直接复制就能开始写的新论文骨架）。
>
> **要改这个项目本身的代码，先读 [`AGENT.md`](AGENT.md)**：里面记录了迭代过程、
> 已实测排除的假设、Word / OOXML 的隐性行为坑（域提示、分节符吞段前距、双面排版插页、
> 图片行距、封面与声明页的逐项数值），以及**「规范未明确项」的完整采用值表**。

---

## 快速开始

### 1. 准备 Python 环境

本工具是一个 **Python 程序**：所有命令都要在**已经装好依赖的 Python 解释器**里执行
（系统 Python、`venv`、`conda` 都行）。要求 **Python ≥ 3.10** 与 **Pillow**；
导出 PDF 与刷新目录页码额外需要本机装有 **Microsoft Word**（推荐）或 LibreOffice。

```bash
# 方式 A：conda
conda create -n thesis python=3.12 -y
conda activate thesis
python -m pip install -e .

# 方式 B：venv
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux
python -m pip install -e .
```

`python -m pip install -e .` 会装好 Pillow，并顺带注册一个 `md2docx` 命令（见下一节）。

### 2. 怎么运行它

**它不是一个双击/直接敲名字就能用的程序。** 直接在终端里敲 `md2docx` 很可能报
`command not found` / `不是内部或外部命令`——因为这个命令只有在**装过本项目并且激活了那个
环境**之后才会出现在 PATH 上。

两种可靠写法，任选其一：

```bash
# 写法一（最稳，不需要 pip install）：用 python 调用仓库里的入口脚本
python md2docx.py thesis.md --out output

# 写法二：先 python -m pip install -e . 并激活环境，之后才能直接用命令名
md2docx thesis.md --out output
```

两个前提缺一不可：

1. **`python` 指向装好依赖的那个解释器**——用 conda/venv 就先激活，别在系统 Python 里跑；
2. **当前目录是仓库根目录**（或给 `md2docx.py` 写绝对路径），否则找不到入口脚本。

不确定当前用的是哪个解释器时，先确认：

```bash
python -c "import sys; print(sys.executable)"      # 看路径对不对
python -c "import PIL; print(PIL.__version__)"     # 看 Pillow 在不在
```

> 本文档下面的示例统一写成 `python md2docx.py ...`。如果你已经 `pip install -e .` 并激活了
> 环境，把 `python md2docx.py` 换成 `md2docx` 即可，参数完全一样。

> **本机（作者本人）常用的一行命令**——只对这台机器有效，其他人请用上面的通用写法：
>
> ```powershell
> & 'E:\Anaconda\envs\myui\python.exe' 'D:\Users\Desktop\HarnessThesis\Thesis-md2docx-NJUST\md2docx.py' D:\Users\Desktop\UAV_SUPER\UAV_SUPER_THESIS\thesis.md --pdf --pages --out output --backend word
> ```

### 3. 公式依赖（可选）

公式会被转换成 Word 原生 OMML。转换依赖两个**公开 npm 包**（`temml`、`@hungknguyen/mathml2omml`，
均未被本项目修改，`package-lock.json` 中的 `resolved` 指向 `registry.npmjs.org`）：

```bash
npm install --prefix thesis_md2docx/math/latex2omml_node
```

不安装也能导出，公式会以 LaTeX 文本写入 DOCX。

### 4. 常用命令

```bash
# 检查环境（同时校验 profile 的样式目录、语义角色与前置页计划）
python md2docx.py check

# 生成 DOCX
python md2docx.py example/thesis-demo.md --out example/output

# 生成 DOCX + PDF + 分页图
python md2docx.py example/thesis-demo.md --pdf --pages --out example/output --backend word

# 只把已有 DOCX 转 PDF
python md2docx.py pdf output/thesis.docx output/thesis.pdf --backend word

# 用 Word 刷新域，把真实目录页码写回 DOCX（生成后建议跑一次）
python md2docx.py refresh-fields output/thesis.docx

# 对照学校范例审计版式
python md2docx.py compare-docx reference.docx output/thesis.docx --out output/audit.md
python md2docx.py compare-pdf reference.pdf output/thesis.pdf --out output/pdf-audit.md --diff-dir output/pdf-diff

# 封面像素级对版：把生成封面与学校参考封面各自经 Word 导出 PDF、同 DPI 渲染、逐线比较
python tools/compare_cover.py
```

运行时会先打印「md2docx 开始」与本次命令，结束时打印总耗时；导出 PDF 的环节会明确提示
正在调用 Word——这一步单次 30~60 秒属正常，不要急着中断。

`njust-master-thesis` 是唯一的 profile，也是默认 profile，因此普通导出不需要 `--profile`。
一键脚本 `export-example.ps1` / `.cmd` / `.sh` 会把示例论文完整导出到 `example/output/`。

### 5. 目录页码：为什么需要 refresh-fields

生成 DOCX 时，目录里每一条的页码是**占位值**——真实页码只有在 Word 完成分页之后才存在。
把占位值换成真实页码有两条路：

```bash
# 推荐：由 Word 刷新后回存（需要本机有 Microsoft Word）
python md2docx.py refresh-fields output/thesis.docx

# 或者在 Word 里打开文档，Ctrl+A 然后按 F9（或右键目录 → 更新域 → 更新整个目录），再保存
```

导出 PDF 时不需要这一步：`python md2docx.py pdf --backend word` 会在导出前自动更新域，
因此 PDF 里的目录页码始终正确。

> **不要**用「给目录域加 `w:dirty`」或「打开 `w:updateFields`」来让 Word 自动刷新——那会让 Word 每次
> 打开文档都弹出「该文档包含的域可能引用了其他文件」，即使文档里没有任何外部引用。本项目两者都不写，
> 这也正是参考论文 `_anno.docx` 的做法。

### 6. PDF 后端

| 后端 | 环境 | 定位 |
| --- | --- | --- |
| `word` | Windows + Microsoft Word | **推荐**，高保真，最终验收基准 |
| `libreoffice` | 跨平台，无需 Word | 快速预览，分页与字体可能与 Word 不一致 |
| `auto` | 任意 | 优先 `word`，否则 `libreoffice` |

> **不需要 LibreOffice**：本机装有 Word 时请直接用 `--backend word`。
> pandoc 与 MiKTeX **不能**替代这两个后端——pandoc 的 docx→pdf 会经过 LaTeX 重排而破坏 Word 版式，
> MiKTeX 只从 `.tex` 生成 PDF、不读 DOCX。

导出 PDF 失败时，先确认本机 Word 是否可用（`python md2docx.py check --backend word`）；
若在受限沙箱/自动化环境里运行，Word 需要写 `%APPDATA%\Microsoft\Word`，这类失败要放宽权限后重试。

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

当规范与范例冲突时，**以规范为准**；规范（含附件批注）没有写死、而生成时必须确定的值，
采用值逐条记录在 [`AGENT.md` 第 5 节](AGENT.md)，可复核、可覆盖。

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

## 使用提醒

导出前后值得知道的几件事（逐条成因、实测结论与取舍都在 [`AGENT.md`](AGENT.md)，这里只留结论）：

1. **目录页码要刷新一次。** DOCX 里目录条目的页码是占位值，跑
   `python md2docx.py refresh-fields output/thesis.docx`，或在 Word 里 `Ctrl+A` → `F9` 后保存，
   才有真实页码。导出 PDF 不需要这一步（`--backend word` 会自动刷新）。

2. **打开生成的 DOCX 不会弹「该文档包含的域可能引用了其他文件」。** 这是刻意的：本项目既不写
   `w:updateFields`，也不写任何 `dirty` 域。代价就是上一条那次手动刷新。

3. **前置部分可能多出一页只有页眉页码的空白页。** 与「双面排版 + 正文重启页码」有关，是否出现
   取决于前置部分（摘要 / Abstract / 目录）合计页数的奇偶，因此**换论文可能复现**。本示例不会
   出现；真遇到时在 Word 里删掉该页，或调整目录长度让前置部分凑成偶数页。

4. **公式输出为 Word 原生 OMML**，不生成 MathType/OLE 对象。源论文里若含 OLE 公式，重新生成后
   是可编辑的 Word 公式——视觉一致，对象类型不同。

5. **只实现了学术硕士版式。** 专业硕士封面（「硕士专业学位论文」/「专 业 名 称」）未实现，
   需要时按 `njust_master_thesis` 的写法新增一个 profile。

6. **不覆盖浮动对象、脚注尾注、修订痕迹**等深度 Word 排版。

7. **最终验收请在 Word/WPS 里人工过一遍**：分页、图表是否跨页、孤行、页码。自动导出保证格式
   数值正确，但最终分页依赖本机字体与 Word 版本。

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
└── tools/
    ├── regenerate_golden.py            # 有意改格式后重生 OOXML golden 哈希
    └── compare_cover.py                # 封面像素级对版（参考封面 vs 生成封面）
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
python md2docx.py check
python md2docx.py example/thesis-demo.md --pdf --pages --out example/output --backend word
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
