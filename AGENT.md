# AGENT.md — 项目迭代记录与经验沉淀

本文件记录 `Thesis-md2docx-NJUST` 从上游项目分叉到当前状态的全过程，重点是**踩过的坑**和
**已经验证过的结论**。给后续接手的人（或 AI agent）看：哪些事情已经查清楚了、哪些路是死路、
哪些数值是直接从规范抄来的（不要凭感觉改）。

面向使用者的写作说明见 [`docs/markdown-format.md`](docs/markdown-format.md)；
规则出处见 [`format.md`](format.md) 与
[`thesis_md2docx/profiles/njust_master_thesis/format_requirements/README.md`](thesis_md2docx/profiles/njust_master_thesis/format_requirements/README.md)。

---

## ⚠ 开工前必读：Word 相关命令要**主动申请权限**

**这一条是为了省时间，不是教条。** 本项目的导出 PDF、刷新目录页码、封面像素对版**都必须调用
Microsoft Word**；在受限沙箱里它们一定失败（失败点在工作目录暂存，早于 Word 启动），
**但那不是代码坏了，是权限不够**。

因此每次开新对话、只要任务会跑下面这些命令，**第一次就带上更宽权限**并写明理由，
不要"先不提权试一下"再重试——每轮重试要白花 30–60 秒，还容易误判成代码 bug：

```text
python md2docx.py <任意> --pdf ...
python md2docx.py <任意> --pages ...
python md2docx.py pdf ...
python md2docx.py refresh-fields ...
python tools/compare_cover.py ...
```

配套的三条经验：

1. **`check --backend word` 的 ok 不算数**：它只做 `CreateObject` + `Quit()`、不碰文件，
   在沙箱里照样报 `[ok] Microsoft Word COM automation is available`——不能拿它当"能导出"的判据。
2. **不要为了绕开权限去写裸 COM**（PowerShell `New-Object -ComObject Word.Application`）。
   本项目历史上这样卡死过 3 次，见第 4 节坑 2；只用项目自带的 cscript + VBS 路径。
3. 加了权限仍然失败，才去翻第 4 节坑 3 的排查清单（含"任何 `tempfile.mkdtemp` 建的目录
   在沙箱里不可写"这一条，它同时解释了 pytest `tmp_path` 的 `WinError 5`）。

> 判据：**只要命令里出现 `--pdf` / `pdf` / `--pages` / `refresh-fields` / `compare_cover`，
> 就默认它需要 Word，默认它需要权限。**

---

## 0. 维护约定（每次迭代都要做）

**这份文档是活的。新增的坑和迭代记录，必须在同一次改动里同步写进来。**

1. **踩到新坑就加进第 4 节**，标题里点明"重踩代价"（会不会浪费一整轮排查）。
   如果这个坑是证伪了若干假设之后才定位的，把**试错路径也写下来**——
   对后来人来说，排除清单比结论更省时间。
2. **改了结构或数值就更新对应章节**：
   - 页面 / 分节 / 页眉页脚 → 第 4、5 节
   - 封面、声明页 → 第 5 节（并核对数值是否仍与附件 2.1 / 2.5 一致）
   - 新阶段或方向性调整 → 第 3 节
3. **基线变了就改数字**：第 7 节的测试通过数、页数、端到端命令；第 8 节的已知局限。
4. **新增文件或入口时**，加进第 1 节的分层表或第 8 节的清单。
5. **严格区分「已实测排除」与「尚未验证」**。前者可以直接跳过，后者不要写成结论。
6. 提交说明里写明改了本文档的哪一节；确实不需要更新的，在提交说明里写明理由。

> 判据：新接手的人读完本文档，能**不重走**你已经走过的弯路就够用。
> 如果你这一轮花在排查上的时间超过 30 分钟，那多半就该有一条新记录。

---

## 1. 项目定位

- **上游**：`Thesis-md2docx`（新疆大学本科毕业论文模板，MIT）。上游目录保持 pristine，不要改。
- **本项目**：`Thesis-md2docx-NJUST` —— 南京理工大学**硕士学位论文**。与上游是**并行关系**，
  不是在上游基础上"加一个 njust 模块"。因此仓库里**不存在任何 XJU 的 profile、资源、示例或测试**
  （唯一保留的上游痕迹是 README 里的 MIT 署名）。
- **唯一 profile**：`njust-master-thesis`，同时是默认 profile。

### 生成流程

```
Markdown
  → parser.py           解析为 IR block（标题/段落/图/并排图/表/公式/引用/代码块）
  → builders/document.py  按 profile 的渲染钩子调度
  → ooxml/*.py          手写 OOXML（段、表、图、包部件）+ profiles/<x>/ 负责校别差异
  → zipfile             打包成 .docx
  → pdf/backends/word   Word COM（cscript + VBS）导出 PDF
```

**不使用 python-docx**，所有 XML 手写。好处是完全可控、可用 golden 哈希锁定；代价是每个
Word 行为坑都要自己踩。

### 分层约定

| 层 | 位置 | 职责 |
| --- | --- | --- |
| 通用 | `thesis_md2docx/{parser,ir,builders,ooxml,styles,math,pdf}` | 与学校无关 |
| 语义角色 | `styles/roles.py` | `body.normal`、`body.heading.level1` 等，隔开通用层与学校样式 ID |
| 学校 | `profiles/njust_master_thesis/` | 样式表、编号、页面、封面、页眉页脚、三节装配 |
| 数值 | `profiles/njust_master_thesis/constants.py` | **所有**页边距/字号/段距/坐标的唯一来源 |

---

## 2. 环境与工具链

> 下面这一段是**本机（作者这台机器）专用**的快捷写法，不属于通用安装步骤——通用写法见
> README「快速开始 → 准备 Python 环境」。换机器时只替换解释器路径即可。

```powershell
# 本机专用：conda 环境 myui
. 'D:\Users\Desktop\HarnessThesis\conda-manual.ps1'; $py = Get-CondaPython myui
$env:PYTHONIOENCODING='utf-8'; $env:PYTHONUTF8='1'   # 中文输出必设
```

```powershell
# 通用写法：任意装好依赖的解释器都能跑（不需要 pip install）
python md2docx.py check
```

| 组件 | 版本/位置 | 用途 |
| --- | --- | --- |
| Python | `myui` 环境，3.12.11 | 必须是 3.12（见坑 #1） |
| Node | v24.14.0 | LaTeX → MathML(temml) → OMML(mathml2omml)，公网 npm，未改源码 |
| poppler | `pdftoppm` / `pdftotext` / `pdfinfo`（随 MiKTeX） | PDF 取证 |
| Microsoft Word 2019 | cscript + VBS | DOCX → PDF、刷新域 |

**不需要 LibreOffice**、不需要 pandoc（pandoc 的 docx→pdf 会经 LaTeX 重排，破坏 Word 版式）。

### 为什么用 cscript + VBS，而不是在 Python 里直接调 COM

**项目仍然在用 Word COM**（VBS 里的 `CreateObject("Word.Application")` 就是 COM），
区别只在**宿主进程**：Word 由 `cscript.exe` 在独立进程里启动，而不是在 Python 进程内持有
COM 对象。这么做的原因：

| 理由 | 说明 |
| --- | --- |
| 进程隔离 | Word 挂在模态对话框上时，可以直接杀掉 `WINWORD.EXE`，父进程不会被拖死。**进程内 COM 没有这个退路**——本项目的裸 PowerShell COM 尝试就是这样卡死 3 次的 |
| 线程套间 | Word COM 需要 STA。`cscript` 是干净的 STA 宿主；非 STA 宿主（或没有消息泵的 PowerShell 宿主）里的模态对话框无人应答，必然挂住 |
| 免依赖 | Python 侧只需要 `subprocess` + `cscript`，不必引入 `pywin32` / `comtypes`，也不做 COM 编组 |
| 参数确定 | `Documents.Open` 有 16 个参数，VBS 里把「只读/不修复/不转换/不弹宏提示」这套组合固定下来，避免 Word 弹修复或转换对话框 |
| 提示抑制 | `DisplayAlerts = 0` 在 Open 之前就设好 |
| 错误协议 | VBS 用 `OPEN_ERROR:<hresult>:<描述>` / `EXPORT_ERROR:...` 写 stdout，并以不同退出码结束；Python 直接解析文本，不用处理 COM 异常编组 |
| 复用 | 同一份 VBS 可以经 PowerShell 互操作从 WSL 调用（`_call_cscript_wsl`） |

**唯一仍用进程内 COM 的地方**是 `backend.py` 的 `_word_com_check()`（可用性探测，
取 `$w = New-Object -ComObject Word.Application` 后立即 `Quit()`）。它只做一次探测、
不打开文档，因此不会遇到对话框；`--skip-word-check` 可以跳过。

> 注意：换成 cscript 并**不能**免除 Word 需要写 `%APPDATA%\Microsoft\Word` 这一要求——
> 那是 Word 自身的行为。而且沙箱里还会更早地卡在工作目录暂存上，见坑 3。

### 沙箱里哪些操作能做、哪些不能

| 操作 | 沙箱内 | 说明 |
| --- | --- | --- |
| 生成 DOCX（`md2docx thesis.md --out ...`） | ✅ | 纯 Python 写文件，不碰 Word |
| `md2docx check` / `profiles` / `backends` | ✅ | —— |
| `md2docx check --backend word` | ✅ 但会**误导** | 探测只 CreateObject + Quit，报 ok 也不代表能导出 |
| `md2docx pdf --backend word` | ❌ | 失败在工作目录暂存，早于 Word 启动 |
| `md2docx refresh-fields` | ❌ | 同上 |
| `md2docx pdf --backend libreoffice` | ❌（本机未装 LO） | 装上 LibreOffice 后应可在沙箱内用 |
| `python tools/compare_cover.py` | ❌ | 内部要跑两次 Word 导出，与 `md2docx pdf` 同理——**给命令申请更宽权限即可** |

`THESIS_WORD_DOCX2PDF_METHOD`（`export` / `saveas`）可选择 `ExportAsFixedFormat`
或 `SaveAs2(wdFormatPDF)`；实测两者输出一致。

---

## 3. 迭代过程

### 阶段 0：读上游
弄清代码结构、生成原理、可改程度（profile 机制是主要扩展点），确认可行后分叉。

### 阶段 1：XJU → NJUST 移植
建立 `njust_master_thesis` profile：20 个样式、4 级编号、A4 + 三节（封面声明 / 前置 / 正文）。
数值逐条从《南理工硕士论文格式.doc》正文条款 + 附件 2.1–2.13 + 59 条批注 + 学校范例反推。

### 阶段 2：改成"原生 NJUST"
用户纠正：NJUST 与 XJU 是并行的，不是"在上游里加 njust"。于是删除
`profiles/xju_undergraduate_thesis/`、`thesis_md2docx/resources/`、上游 `example/`、`example_xju/`，
重写 `profiles/registry.py`（只剩一个 profile）、清理 `constants.py` / `profiles/base.py` /
`doctor.py` / `layout.py` 里的 XJU 默认值，重命名 `example_njust/` → `example/`，
重写 golden 测试与 `tools/regenerate_golden.py`。

### 阶段 3：Word 域提示（耗时最多的一段弯路）
打开生成的 DOCX 会弹「该文档包含的域可能引用了其他文件」。经过 **7 轮**排查才定位。详见坑 #4。

### 阶段 4：封面与声明页对齐
用户提供学校规范的 `.docx` 版本后（关键是能读到附件 2.1 / 2.5 的段距与 run 结构），
按规范逐 run 还原封面；声明页按附件 2.5 的结构与单倍行距。详见第 5 节。

### 阶段 5：资源整理与使用文档
学校原始材料移入 `format_requirements/`（gitignore），新增 `docs/markdown-format.md`（写作格式 +
手把手步骤）与 `example/thesis-template.md`（可复制的新论文骨架），并实测从模板走通完整流程。

---

## 4. 踩过的坑（按"重踩代价"排序）

### 坑 1：Python 3.8/3.9 无法 import
`styles/roles.py` 等处用了 `StyleProperty = XmlProperty | str` 这类**运行时**类型别名，
3.9 及以下直接 `TypeError`。**必须用 3.12**，不要试图改源码去兼容。

### 坑 2：不要用裸 PowerShell 调 Word COM
```powershell
# ✗ 这一晚用这个方式卡死/超时过 3 次
$w = New-Object -ComObject Word.Application
$doc.Fields.Update(); $doc.ExportAsFixedFormat(...)
```
Word 弹任何对话框都会挂住。**只用项目自带的路径**：

```powershell
python md2docx.py pdf in.docx out.pdf --backend word        # cscript + word_export.vbs
python md2docx.py refresh-fields in.docx                     # cscript + word_update_fields.vbs
```
VBS 里已设 `DisplayAlerts = 0` 且用正确的 `Documents.Open` 参数。每次 Word 任务前先
`Get-Process WINWORD | Stop-Process -Force`，并 `Start-Sleep 2`。

### 坑 3：沙箱下的拦路虎（**已实测复现，结论如下**）

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `md2docx pdf --backend word` 直接失败，**连 Word 都没启动** | 后端要先把输入复制到 `--tmp-root` 下的 `job-*/` 工作目录；沙箱里这个写入被拒（`PermissionError ... job-xxxx\input.docx`），默认 tmp 与工作区内的 tmp 都一样 | 需要更宽权限 |
| `PermissionError` 写 `%APPDATA%\Microsoft\Word` | Word 自身启动时要写该目录 | 同上，需要更宽权限 |
| `tempfile.TemporaryDirectory()` 失败 | 系统临时目录不可写/不可枚举 | 改成仓库内临时目录（`tools/regenerate_golden.py` 用 `.golden-tmp`） |
| pytest `tmp_path` → `WinError 5` | basetemp 目录枚举被拒 | 自写 runner，显式传入 tmp 目录（见第 7 节） |

**实测结论（不要凭推测）**：

1. 在受限沙箱里 **Word 后端做不了任何事**——PDF 导出、`refresh-fields` 都不行，
   而且**失败点在工作目录暂存，早于 Word 启动**。所以"沙箱里能不能用 Word"与
   "Word 要不要写 AppData"是两个独立原因，前者先触发。
2. `md2docx check --backend word` 在沙箱里**会报 `[ok] Microsoft Word COM automation is available`**，
   因为那个探测只做 `CreateObject` + `Quit()`、不碰文件。**这个 ok 不代表真能导出**，
   不要拿它当作可用的判据（`--skip-word-check` 只是跳过这个探测）。
3. `--tmp-root` 指到工作区内**也不能**绕过——实测同样被拒。
4. 本机**未安装 LibreOffice**（`soffice.exe` 不存在），所以沙箱内没有 PDF 导出的替代后端。
   要用 `--backend libreoffice` 需要先自行安装。

pytest 还会在仓库里留下**删不掉**的空目录（`pytest-cache-files-*`，ACL 拒绝删除），
只能手动清理。

### 坑 4：Word 域更新提示——两个独立触发器（★ 最大的坑）
提示文案是「**该文档包含的域可能引用了其他文件**」，但**文档里可以一个外部引用都没有**。
Word 对"有待更新的域"一律用这句措辞。触发器有两个，**两个都不能写**：

| 触发器 | 作用 | 结论 |
| --- | --- | --- |
| `<w:updateFields w:val="true"/>` | 打开时更新**所有**域 | **不写** |
| 任何带 `w:dirty="true"` 的域 | 打开时更新**该**域；目录域最容易踩 | **不写** |

**迭代弯路**（记录下来避免重走）：

1. 先以为 `updateFields` 是唯一原因 → 去掉后**仍然弹**。
2. 又怀疑文档真有外部引用 → 逐部件检查：`TargetMode="External"` 0 个、
   `INCLUDETEXT`/`INCLUDEPICTURE`/`RD`/`DDE` 全无、任何部件里都没有文件路径字符串。**排除**。
3. 怀疑是 PDF 导出环节 → 对比 `ExportAsFixedFormat` 与 `SaveAs2(wdFormatPDF)`：
   **输出完全一致**。**排除**。
4. 怀疑 `--no-update-fields` → 结果一致。**排除**。
5. 最后做**差分对比**：把 `_anno.docx`（学校范例，不弹）与自己的产物逐项比 →
   范例 TOC 域 `begin` **没有** `w:dirty`，我们有。**这才是真因**。

**结论**：`exports.py` 生成的 TOC 域不写 `dirty`；页码由
`md2docx refresh-fields`（Word 更新域后回存）或用户在 Word 里 `Ctrl+A`→`F9` 写入。
`tests/test_docx_golden.py` 有两条回归测试锁死：无 `updateFields`、`dirty` 域数为 0。

> **教训**：遇到"文档属性导致的 Word 行为"，最快的方法是**找一个不触发该行为的确切文件做差分**，
> 不要靠推测逐一排除。

### 坑 5：手动分页符会吞掉段前距
现象：`Abstract` 与 `目录` 标题设置了段前距却**完全不显示**（实测 +1.6pt / +2.2pt，
而摘要页 +20.2pt 正常）。

**原因**：Word 丢弃**手动分页符**之后第一段的「段前距」；而**分节符**不会。

**修法**：前置部分改为**逐页分节**（摘要 / Abstract / 目录 各自成节，只有摘要重启罗马页码，
其余续排），`document.py` 里的 `front_continue_sect`。

```python
# profiles/njust_master_thesis/document.py
front_continue_sect = section_profile.replace(layout.front_matter, page_number_start=None)
```

修后实测：摘要 +20.2pt、Abstract +19.6pt、目录 +53.2pt ✓

### 坑 6：双面排版 + 页码重启 = 多出一页
现象：目录页（罗马 III）之后多出一页罗马 IV，**只有页眉页码、没有正文**，
正文顺延到再下一页从 1 开始。

**原因**：只要文档带「双面排版」属性，Word 就会在**重启页码的分节**处插一页，
让重启后的第 1 页（奇数）落在奇数物理页上。触发属性是下面两个中的**任意一个**：

- `<w:evenAndOddHeaders/>`（规范 11.1 要求奇偶页眉不同，**必须保留**）
- `<w:mirrorMargins/>`（规范 2.1 的对称页边距；左右同为 25mm，**没有视觉效果**）

**已实测排除**（不要再试）：目录长度（5 条与 30 条一样）、目录标题段前段后（压到 0 也一样）、
`w:type` 取值、分节段高度与是否独立成段、导出前是否更新域、两种导出方式、
正文节用 `evenPage`（页码会变 2/3）、正文节不重启页码（页码会变 4/5）。

**当前状态**：逐页分节后前置部分为 4 页（偶数），正文自然落在奇数页 p7，
**本示例不再出现这一页**。但页数奇偶取决于目录长度，换论文可能复现。

实测可行的规避方式及其代价（README 里不再展开，留在这里备查）：

| 方式 | 空页 | 页码 | 代价 |
| --- | --- | --- | --- |
| 同时去掉奇偶页眉与对称页边距 | 无 | 正确 | 偶数页页眉与奇数页相同，**违反规范 11.1** |
| 正文节不重启页码 | 无 | 4/5… | 正文不从 1 开始，违反规范 6 |
| 正文节改用 `evenPage` | 无 | 2/3… | 正文从 2 开始，违反规范 6 |
| 前置部分占偶数页 | 无 | 正确 | 依赖前置内容恰好凑成偶数页，无法先验保证 |
| **逐页分节（当前做法）** | 本示例无 | 正确 | 不保证——前置页数仍随目录长度变化 |
| 去掉奇偶页眉（仅当学校不强制） | 无 | 正确 | 偶数页页眉与奇数页相同，**违反规范 11.1** |

真要彻底去掉，就改 `thesis_md2docx/profiles/njust_master_thesis/styles.py` 的
`njust_settings_xml()`，不再传 `even_and_odd_headers=True` 与 `mirror_margins=True`
（代价是偶数页页眉）。

### 坑 7：图片被固定值行距压扁
现象：图片显示不全，被压在一行里。

**原因**：图片段落用了 `line=400 lineRule="exact"`（固定值 20 磅），Word 按行高裁剪整幅图。
参考论文的图片段落实测是 `line=240 lineRule="auto"`（单倍）。

**修法（两处，容易漏第二处）**：
1. 样式 `NjustFigureImage` 与 `body.py` 的 `figure_image_paragraph_xml()`
2. **`ooxml/images.py` 的 `figure_row_xml()`** —— 并排图放在表格单元格里，
   会继承正文的固定值行距，第一处改了它仍然坏

### 坑 8：制表位前导符 ≠ 字体下划线
封面填空位一开始用「右对齐制表位 + `w:leader="underscore"`」补齐，视觉上是断续的
下划线**字符**，与字体下划线（`w:u`）的粗细、基线位置都不同。用户一眼看出不对。

**修法**：填空位一律用**空格 + 字体下划线**（`w:u val="single"`），包括标签与值之间那段空格。

### 坑 9：按字体宽度算对齐是个陷阱
我曾试图用"全角字 = 字号、空格 = 半字号"的模型推算补空格数量，让每行下划线等长。
结果是数值反复对不上，越改越乱。

**结论（用户原话）**：「不知道你在改什么没必要的对齐？」
**做法**：直接照抄范例的空格个数（`COVER_FIELD_GAP_SPACES = 12`、
`COVER_FIELD_UNDERLINE_UNITS = 18`），不换算。

### 坑 10：`sectPr` 的语义
`w:sectPr` 出现在**结束该节的那个段落**的 `pPr` 里；其中 `w:type` 描述的是**该节如何开始**。
最后一节的 `sectPr` 直接放在 `w:body` 末尾。搞反会导致节的页眉/页码错位。

### 坑 11：文本提取会骗人
判断"某页是否空白"时，`pdftotext` 说空、但那一页其实有页眉页码（它们也是文字），
反之亦然。**必须以像素为准**：

```python
from PIL import Image
im = Image.open(png).convert("L"); px = im.load()
dark = sum(1 for y in range(0, H, 6) for x in range(0, W, 6) if px[x, y] < 200)
# 墨迹 < 0.5% ≈ 只有页眉页码 / 全空白
```
下划线的**横向范围**同样只能靠像素扫行来量（下划线不进文本层）。

### 坑 12：不要在特定环境下反复重试同一条命令
`tools/regenerate_golden.py` 原本用 `tempfile.TemporaryDirectory()`，在沙箱里必然失败。
遇到这种"环境性失败"，改代码（用仓库内临时目录），不要反复重跑。

---

## 5. 封面与声明页：数值来自规范，不要凭感觉改

规范文件：`format_requirements/南理工硕士论文格式.docx`（附件 2.1 = 封面，附件 2.5 = 声明）。

### 附件 2.1（封面）

```
[122] 分类号/密级  spacing(before=156 beforeLines=50 line=400 exact)
                   ind(firstLineChars=200 firstLine=420)
                   runs: 分类号 + 下划线空格 + 普通空格 + 密级 + 下划线空格
                   ← 密级是靠**普通空格**推到右侧的，不是下划线铺满整行
[123] UDC         line=400 exact；runs: UDC + 下划线**上标**「注1」+ 下划线空格
[126] 硕 士 学 位 论 文   sz=64 居中
[127][128] 两个空行，均 line=400 exact   ← 学位类别与题名之间是**两个**空行
[129] 题名        sz=48 居中
[132] （题名和副题名）  line=360 exact sz=24
[134] ×××         line=600 exact sz=36 ind(right=55)
[135] （作者姓名）  line=340 exact sz=24
[137] 指导教师姓名  before=312 beforeLines=100 line=560 exact
                   ind(firstLineChars=300 firstLine=843)
                   ← 范例该处 before=326，两者差 0.7pt；因都写 beforeLines=100，
                     Word 取 1 行 = 28pt，实际渲染无差别（本项目取范例值 326）
```

其他已经确认的封面事实：

- **校徽上方的空行是固定值 20 磅**，不是单倍。
- 题名与作者姓名下方各有**一条独立横线**。范例里它们是 `mc:AlternateContent`
  包着的 **wps 浮动直线**（Choice=DrawingML `<wp:anchor>`，Fallback=VML `<v:line>`；
  共 3 个，粗细都是 `a:ln w=9525` = 0.75pt）。实测线宽与位置：

  | 线 | 线段宽 | 位置 |
  | --- | --- | --- |
  | 题名第 1 行下方 | `cx=5057775` EMU = **7965 twips = 140.5mm** | 水平 `column`+350520 EMU(9.74mm，即居中)；垂直 +395604 EMU(31.15pt) |
  | 题名第 2 行下方 | 同上 7965 twips | 水平 `align=center`；垂直 +2539 EMU(0.2pt) |
  | 作者姓名下（`***` 段） | `cx=1824990` EMU = **2874 twips = 50.7mm** | 水平 `align=center`；垂直 +342264 EMU(26.95pt) |

  **两条题名线是"每行题名一条"，不是重复**——早先按 XML 偏移量算错，把它们当成
  重叠的一条（错了：像素实测两条相距 11mm = 一行题名高）。现在的实现是
  `_cover_title_block()`：每个题名行后各跟一条线；题名只有一行时补一条空行再补线，
  也就是**永远两条**（用户明确要求"单行标题也要两行下划线"）。

  本项目改用**段落下框线 + 左右等距缩进**实现（`_cover_rule(width_twips)`），
  不引入 VML/形状；因此函数收的是**线宽**，缩进按 `TEXT_WIDTH` 均分
  （题名 7965 → 552/553，作者 2874 → 3098/3098）。代价是线只能落在段落底部，
  无法复刻范例那种"相对段落任意偏移"的浮动位置（作者线实测低 2.1mm）。
  左右缩进之和必须小于正文宽 9070 twips，否则被 Word 截断（踩过，已加断言）。
- **填空位是等宽 + 值居中**，不是左对齐。像素实测六行下划线都从 69.6mm 到 156.4mm
  （86.8mm ≈ 246pt = `COVER_FIELD_FILL_PT`），而值的位置随字数变化，三条中文值的
  中心都落在 109.5mm（页面坐标）附近。所以：
  - 标签列固定 6 个全角字宽（84pt），短的标签（`学 位 类 别`）用**不带下划线**的空格补齐；
  - 值的水平中心固定在 `COVER_FIELD_VALUE_CENTER_PT`（相对填空位 113.1pt）；
  - 补齐空格按**宽度**算（不是固定个数），值的字数一变，两端空格跟着变。
  这就是"`***`/`教授` 比下面几行靠右、`通信与信息系统` 比它们靠左"的原因——
  照抄空格个数做不到这一点（踩过：早期用固定 18 个单位，长值行反而更长）。
- 无标签行（导师职称）的前导空格**不带下划线**：范例前 16 个是普通空格，
  下划线从 69.6mm 才开始。早期把它们一起画了线，整条线左伸了 29.8mm。
- 「论文提交时间」行的所有文字 run 带 `w:spacing=-10`（-0.5pt 字符间距）。
  **只加在文字上，不要加在决定下划线几何的空格上**——否则整行填空位会缩短
  （踩过：一加就成了 76mm）。
- 分类号/密级行的段前同时写了 `before=163` 与 `beforeLines=50`；**Word 取
  beforeLines**，所以实际段前是 0.5 行 = 10pt，不是 8.15pt。
- UDC 行「注1」的中文字体在范例里是**华文中宋**（run 上写死 `w:eastAsia`），
  与整行其余部分的宋体不同。
- 填写内容：**中文楷体 + 西文 Times New Roman**，且**值本身也带下划线**。
- 标签字号固定**四号**，不跟随填写内容的字号
  （踩过：导师行填写内容是三号，标签被一起放大成三号）。
- 两行括号提示 `(题名和副题名)` / `(作者姓名)` **保留**（用户要求封面就是模板状态）。
- `(作者姓名)` 之下有一个 **30 磅**行距的空行。

### 附件 2.5（声明页）

```
[260] 声  明            居中；无段距覆盖
[261] 声明正文          ind(firstLineChars=200 firstLine=560)
[262] 空行
[263] 研究生签名：___ 年 月 日
[264][265][266] 三个空行
[267] 学位论文使用授权声明   居中
[268] 空行
[269] 授权正文          ind(firstLineChars=200 firstLine=560)
[270][271] 两个空行
[272] 研究生签名：___ 年 月 日
```

- **两段声明同页**（上、下两部分），标题与正文之间、两份声明之间的间隔照附件 2.5，
  不套用正文段距、也不压成紧凑的一段。
- **正文与签名行是单倍行距**（`line=240 auto`），不是正文的固定值 20 磅
  （踩过：我一度以为继承 Normal 就是固定值 20 磅，实际规范文档的 Normal 是单倍）。
  但**「声  明」这个标题例外**：范例该段不带 spacing 覆盖、继承 Normal 的固定值
  20 磅；而「学位论文使用授权声明」标题显式写了单倍（`line=240 auto`）。
- 签名行的下划线空格数**上下两份不同**：声明页 12 个、授权声明页 13 个，
  下划线之后还有 **13 个普通空格**才到「年 月 日」（范例逐 run 如此）。
  这些数直接决定下划线长度，别按"看起来差不多"去凑。
- 声明与授权声明**正文文字不得改动**（附件 2.5），因此硬编码在 profile 里，
  Markdown 只提供签名与日期。
- **这一页是"吸附行网格"的**（★ 曾经整页比范例短一半的根因）。范例该页每个段落都写
  了 `<w:snapToGrid/>`，而节的网格是 `docGrid type="linesAndChars" linePitch="326"`
  （16.3pt 一行）：14pt 正文放不进 16.3pt，于是向上吸附到 **2 格 = 32.6pt**，
  整页才铺得满。三个条件缺一不可：
  1. 节的 `docGrid` 必须有 `type="linesAndChars"`——只写 `linePitch` 时 `type` 默认
     是 `default`，等于没有行网格，吸附静默失效；
  2. 段落要写 `<w:snapToGrid/>`（我们的 Normal 是 `w:val="0"`，不能靠继承）；
  3. **空行的字号必须写进 `w:pPr/w:rPr`**。空段落的高度由**段落标记**的字号决定，
     写在空 run 上 Word 不认——12pt 的段落标记只占 1 格（16.3pt），14pt 才占 2 格
     （32.6pt）。表现就是整页正好少 5.7mm（≈1 格），且只从授权声明那一段开始错位。
  另外 `pPr` 的子元素顺序是 ECMA 硬约束：`w:snapToGrid` 必须排在 `w:spacing` **之前**，
  写反了 Word 会静默忽略其中一个（踩过：正文吸附了、空行没吸附）。

### 封面已知残差与一键对版

跑 `python tools/compare_cover.py`（参考件与生成件各自过 Word 导出 PDF、
`pdftoppm` 同 DPI 渲染第 1 页、按像素扫横线）后，当前残差如下，均已 ≤ 2.5mm：

| 元素 | 残差 | 原因 |
| --- | --- | --- |
| 题名两条线、作者线 | 长度 +1.1mm | `pBdr` 线端各多约半像素（范例是浮动线，端点更"干净"） |
| 作者姓名横线 | y +1.7mm | 范例的线是浮动的，落在作者行**内部** 26.95pt 处；段落下框线只能落在段落底部（把边框 `w:space` 从 1pt 调到 0pt 后已从 +2.8 收敛到 +1.7） |
| 指导教师姓名 | 长度 +2.3mm | 该行值是 16pt，补齐空格最小单位 8pt（246pt 的目标值取不到，只能 242 或 250） |
| 论文提交时间 | 长度 −1.3mm、起点 +1.1mm | 范例该行自己也比邻近行长 1mm（手工微调） |
| 字段行 | y +0.4 ~ +0.6mm | 网格/lines 单位影响段前 `beforeLines` 的解释，整体下移不到 1mm |

值的位置反而更准：`学位类别 / 学科名称 / 研究方向 / 论文提交时间` 四行的值墨迹范围与范例
**逐像素一致**（中心差 0.0mm）；`指导教师姓名 / 导师职称` 的中心差 −2.4~−2.8mm 是**内容差异**
（范例该行是 `* * *` 五个字符、`导师职称` 行还并排写着姓名），不是排版偏差。

> 用户决定暂不做两件事（记录备查，不要擅自开工）：**A** 把作者横线改成 wps 浮动线
> （可消掉 +1.7mm 的 y 差，但要引入 `mc:AlternateContent` 并放弃"不引入 VML/形状"的取舍）；
> **B** 用混合字号空格把指导教师姓名行的 +2.3mm 长度差消掉。

`tools/compare_cover.py` 用法：

```powershell
python tools/compare_cover.py                        # demo 封面 vs 参考封面，默认容差 2.5mm
python tools/compare_cover.py my-thesis.md           # 换自己的论文
python tools/compare_cover.py --tolerance-mm 1.5     # 收紧
python tools/compare_cover.py --no-export            # 复用已导出的 PDF，快速迭代
```

它需要 Microsoft Word（与 `md2docx pdf --backend word` 同）；报告写到
`example/output/cover-audit.md`，超差即退出码 1，可以直接挂进提交前检查。
检测器的判据是"连续墨迹 ≥18mm + 同一行墨迹覆盖率 ≥80% + 相邻行起止 x 都接近"，
这三条缺一条就会把校徽图片或加粗文字的长笔迹误判成横线（踩过）。

### 规范未明确项的采用值（全表，自 README 迁入）

规范（含附件批注）**明确列为"原文未明确"**、而生成时必须给出确定值的项目。采用值全部来自
范例实测或学校排版件，逐条可复核、可覆盖（常数都在 `constants.py`）。

| 项目 | 采用值 | 依据 / 备注 |
| --- | --- | --- |
| 封面字段位置 | 标签首行缩进 843 twips；值列不用制表位 | 范例反推；原范例 8280 的制表位被 Tab 触发时会使值折行 |
| 封面题名/作者横线 | **每行题名各一条** 140.5mm（单行题名也补第二条），作者线 **50.7mm**，粗 0.75pt | 范例 wps 浮动线 `cx` 实测（5057775 / 1824990 EMU） |
| 横线实现方式 | 段落下框线 + 左右等距缩进，边框 `w:space="0"` | 不引入 VML/形状；作者线比范例低 1.7mm |
| 封面填空位与值的对齐 | 六行下划线**等宽 86.8mm(246pt)**，值**居中**（中心距填空位起点 113.1pt） | 范例像素实测：六条线都 69.6→156.4mm，中文值中心都在 109.5mm |
| 封面顶部的段前 | `before=163` + `beforeLines=50`（Word 取 0.5 行 = 10pt） | 规范写 156、范例 163；两个值都写，以 beforeLines 为准 |
| 「论文提交时间」字符间距 | 仅**值** run 加 `w:spacing=-10` | 加在标签上会让整行左移 1mm，加在空格上会让下划线缩短 |
| UDC「注1」字体 | 华文中宋，上标 + 下划线 | 范例该 run 写死 `w:eastAsia` |
| 声明页标题行距 | 「声  明」固定值 20 磅；「学位论文使用授权声明」单倍 + 吸附网格 | 前者无 spacing 覆盖（继承 Normal），后者显式 `line=240 auto` |
| 声明页整页行距 | 吸附行网格：`docGrid type="linesAndChars" linePitch="326"`，14pt 正文 → **2 格 = 32.6pt** | 范例每个段落都带 `<w:snapToGrid/>`；空行字号写进 `pPr/rPr` |
| 声明页签名下划线 | 声明页 12 个空格、授权页 13 个，其后 13 个普通空格 | 范例逐 run 实测 |
| 封面「32号楷体」磅值 | 32pt 楷体加粗 | 学校排版件 `w:sz=64` |
| 封面未批注字段的字体 | 四号宋体加粗 | 与已批注的「学位类别」标签一致 |
| 正文首行缩进 | 2 字符（`firstLineChars=200` / 480 twips） | 范例 |
| 目录缩进与制表位 | TOC1=0、TOC2=420、TOC3=839 twips；右对齐点线制表位 9070 | 范例 |
| 参考文献悬挂缩进 | 0（不悬挂） | 规范未明确则不设；如需悬挂改 `styles.py` 的 `STYLE_REFERENCE` |
| 图题/表题对齐与段距 | 居中、段前段后 0、固定值 20 磅 | 范例 |
| 图片默认宽度/居中/环绕 | 居中、段前后 0；宽度按图片 DPI 与页宽推导 | 范例 |
| 公式居中与编号右对齐 | 居中制表位 4535 + 右对齐制表位 9070 | 范例 |
| 表格三线表与边框 | 上下线 1.5 磅、无内线 | 范例；可用 `::: table` 逐表覆盖 |
| 表内行距 | 单倍 | 避免固定行距裁切单元格 |
| 页眉横线 | 0.75 磅（`w:sz="6"`） | 范例 |
| 附录公式编号 | `（A.1）`、`（B.3）` | 与规范 11.4 的 `图B1`／`表B1` 保持一致 |
| 伪代码 / 算法 | 不设专用样式，按普通正文与代码块渲染 | 规范未设规则 |

### 规范/附件批注**已经明确**的常用值（备查，不要改）

这些不是"未明确项"，README 原先混在同一张表里容易被误读，单列出来：

| 项目 | 规范值 |
| --- | --- |
| 页面 | A4；上 30 / 下 24 / 左 25 / 右 25 mm；页眉页脚距边界 20 mm；对称页边距 |
| 正文 | 小四 12pt 宋体 + Times New Roman，固定值 20 磅，两端对齐，首行缩进 2 字符 |
| 一级标题 | 小三 15pt 加粗居左，段前段后 18 磅 |
| 二级标题 | 四号 14pt，段前 12 磅 |
| 三级标题 | 小四 12pt，段前 6 磅 |
| 摘要 / Abstract / 目录 / 致谢 / 参考文献 / 附录标题 | 三号 16pt 加粗居中，段前段后 18 磅；目录标题上空 18 mm |
| 页眉页脚 | 小五 9pt 宋体 + Times New Roman；奇偶页不同 |
| 图题 / 表题 | 五号 10.5pt |
| 参考文献正文 | 五号 10.5pt |
| 分节 | A：封面 + 声明（无页眉页码）；B：摘要 / Abstract / 目录（罗马页码从 I）；C：正文起（阿拉伯页码从 1） |
| 另页 | 只有 结论 / 致谢 / 参考文献 / 附录 另页；正文各章不强制另页 |

---

## 6. 方法论经验

1. **先找权威文件做差分，再动手改。** 本项目的绝大多数 bug 都是靠
   「把自己的产物与学校范例/规范逐属性对比」定位的，而不是靠推理。
2. **测出来的才算数。** 用像素量墨迹、用 `pdftotext -bbox` 量坐标、
   用 `docProps/app.xml <Pages>` 拿 Word 自己的页数。文本提取在判断"是否空白"上不可靠。
3. **提案要能被推翻。** 空白页那一项我连续错了 5 个假设，每个都用一次实验否掉，
   最后才发现是双面排版 + 页码重启。**不要在没有实验支撑时改结构。**
4. **规范 > 范例 > 实现便利。** 冲突时按此优先级；规范没写的项目在第 5 节
   「规范未明确项的采用值（全表）」里逐条记录。
5. **数值只写一处。** 页面/字号/段距/坐标全部进 `constants.py`。
6. **漏改的第二处最致命。** 同一类元素往往有多个构建器（普通图 vs 并排图、
   封面字段 vs 摘要字段），改完要全局 grep 同类调用。
7. **不要过度工程。** 用户明确说过"不知道你在改什么没必要的对齐"——
   照抄规范的固定值比自创一套宽度模型可靠得多。
8. **Word 相关的验证很贵**（每次导出 30–60s，还可能卡住）。批量测试变体、
   一次导出多份对比，比一次改一点跑一次高效得多。

---

## 7. 测试与验证

### 测试

```powershell
python md2docx.py check          # 环境 + profile 样式目录 + 语义角色 + 前置页计划
python tools/regenerate_golden.py
```

**pytest 在本沙箱不可用**（`tmp_path` 触发 `WinError 5`）。用自写 runner：
把 `tests/*.py` 的 `test_*` 函数逐个 import 后直接调用，为需要 `tmp_path` 的函数
显式传入工作区目录，并跳过需要 `capsys`/`monkeypatch` 的 4 个用例。
当前基线：**58 通过 / 4 跳过 / 0 失败**（`tests/test_cover_layout.py` 里的 9 条只锁
封面与声明页结构：题名永远两条横线、横线居中且窄于正文宽、填空位等宽 + 值居中、
提交时间行只有值带 -10 字符间距、声明页段落吸附行网格且 `docGrid` 是 `linesAndChars`）。

`tests/test_docx_golden.py` 除 15 个部件的哈希外，还有三条与版面无关的硬约束：

- `word/settings.xml` 不写 `<w:updateFields/>`
- 文档里**不能有任何** `w:dirty="true"` 的域
- 文档内不出现外部关系与 `INCLUDETEXT` / `INCLUDEPICTURE` / `RD` 等引用外部文件的域

**任何改动 OOXML 的提交都要重生 golden 并说明原因。**

### 端到端

```powershell
python md2docx.py example/thesis-demo.md --out example/output
python md2docx.py refresh-fields example/output/thesis-demo.docx
python md2docx.py pdf example/output/thesis-demo.docx example/output/thesis-demo.pdf --backend word

# 一条命令跑完整条链路（DOCX + 刷新域 + PDF + 逐页 PNG），再对封面做像素对版
python md2docx.py example/thesis-demo.md --pdf --pages --out example/output --backend word
python tools/compare_cover.py     # 参考封面 vs 生成封面，超差即退出码 1
```
当前基线：**19 页**，页码 I/II/III/IV（前置）+ 1/2/…（正文）；`compare_cover.py` 在
默认容差 2.5mm 下**通过**，逐条残差见第 5 节「封面已知残差与一键对版」。

声明页（第 2 页）不在 `compare_cover.py` 的自动判据里，但已实测与范例**逐行重合**：
13 个文本行的 y 坐标差全部 **+0.00mm**（此前每行少 5.7mm，原因见第 5 节的"吸附行网格"）。
回归时用 `example/output/declaration-compare.png` 目检即可。

> 上面这两条都要 Word，在受限沙箱里会失败——给命令申请更宽权限，不要把 Word 任务
> 换成裸 COM（AGENT 第 4 节坑 2）。

### 取证脚本片段

```python
# 页数与 Word 自己的记录对照
zipfile.ZipFile(p).read("docProps/app.xml")   # <Pages> = Word 保存时的页数

# 封面下划线的横向范围（只能靠像素）
from PIL import Image
im = Image.open(png).convert("L"); px = im.load()
for y in range(140, 1160):
    runs, s = [], None
    for x in range(im.size[0]):
        d = px[x, y] < 200
        if d and s is None: s = x
        elif not d and s is not None:
            if x - s > 50: runs.append((s, x))
            s = None
    if runs and sum(b - a for a, b in runs) > 100:
        print(y, runs)
# A4 @120dpi：正文区 x = 118 .. 874
```

---

## 8. 当前状态与待办

### 已完成

- 唯一 profile `njust-master-thesis`，仓库内无 XJU 残留（README 的 MIT 署名除外）
- 生成物不再触发 Word 域提示；目录页码由 `refresh-fields` 写入
- 前置部分逐页分节，各页标题段前距生效
- 封面按附件 2.1 逐 run 还原；声明页按附件 2.5 排版
- 图片（含并排图）为单倍行距，不再被裁剪
- `format_requirements/`（学校原件，gitignore）+ `docs/markdown-format.md` +
  `example/thesis-template.md`

### 已知局限

1. **「目录后多一页」可能复现**：前置部分页数为奇数时，Word 会为页码重启插页。
   成因与取舍见 README。规避方式都有规范代价。
2. **只实现学术硕士**。专业硕士封面（「硕士专业学位论文」/「专 业 名 称」）未实现。
3. **公式输出为 OMML**，源论文里的 OLE/MathType 公式对象会变成可编辑的 Word 公式，
   视觉一致但对象类型不同。
4. **不覆盖**浮动对象、脚注尾注、修订痕迹等深度 Word 排版。
5. 学校原始材料不随仓库分发（见 `format_requirements/README.md`），
   新机器上需要自行补齐。

### 改动时的检查清单

- [ ] 数值改在 `constants.py`，不在渲染代码里硬编码
- [ ] 同类元素的所有构建器都改了（普通图 / 并排图 / 封面 / 摘要 / 表格）
- [ ] 该数值能在规范或范例里找到出处；找不到就记入 README 的「原文未明确」表
- [ ] `python tools/regenerate_golden.py` 后跑测试
- [ ] 端到端导出一次，并用**像素**确认版面（不要只看文本）
- [ ] Word 任务只用 `md2docx pdf` / `md2docx refresh-fields`，不用裸 COM
- [ ] **回来更新 `AGENT.md`**：新坑进第 4 节、结构/数值变更进对应章节、基线数字进第 7 节
