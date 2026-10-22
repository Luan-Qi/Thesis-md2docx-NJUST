# 贡献指南

感谢关注 `thesis-md2docx-njust`。本项目的目标是把**南京理工大学硕士毕业论文**的 Markdown 主稿
稳定导出为符合《南理工硕士论文格式》的 DOCX，并提供可检查的 PDF 预览流程。

当前内置且默认的 profile 是 `njust-master-thesis`（学术硕士）。

> **动手改代码前先读 [`AGENT.md`](AGENT.md)。** 它记录了本项目的迭代过程、已经实测排除的假设
> （省得重走弯路），以及 OOXML / Word 的隐性行为坑：域更新提示的两个触发器、手动分页符吞掉
> 段前距、双面排版 + 页码重启插页、图片必须用单倍行距、封面与声明页的规范数值出处等。

## 基本原则

- Markdown 是源文件，DOCX/PDF 是生成物。
- 优先修导出器或 Markdown 示例，不建议把手工修改后的 DOCX 作为长期来源。
- 格式改动应尽量对齐学校规范和范例，避免只针对单篇论文做特殊处理。
- 新功能应保持可选和可回退，避免破坏已有论文导出。

## 本地检查

建议先安装开发依赖：

```bash
python3 -m pip install -e ".[dev]"
```

提交前建议至少运行：

```bash
python3 -m py_compile md2docx.py $(find thesis_md2docx tests -name '*.py' -type f | sort)
python3 -m pytest tests
./export-example.sh
python md2docx.py check --backend auto
```

`./export-example.sh` 会生成 DOCX、PDF 和分页图片，因此需要可用的 PDF 后端以及 `pdftoppm`。如果只改了非 PDF 相关代码且当前机器没有 PDF 后端，可至少运行前两条命令和 `md2docx check`。

改动了封面/声明页（`profiles/njust_master_thesis/frontmatter.py`、`constants.py`）时，
**必须**额外跑一次封面像素对版：

```bash
python tools/compare_cover.py        # 参考封面 vs 生成封面，默认容差 2.5mm，超差退出码 1
```

`tools/regenerate_golden.py` 只锁 OOXML 字节，锁不住"横线画歪了"；这条命令
把两边都经 Word 导出 PDF、同 DPI 渲染后逐条量横线的起点/长度/竖直位置。

如果修改了公式转换或 PDF 预览相关代码，还建议运行：

```bash
python md2docx.py check --backend word
python md2docx.py example/thesis-demo.md --pdf --out example/output --backend word
```

如果修改了 LibreOffice 后端，还建议运行：

```bash
python md2docx.py check --backend libreoffice
python md2docx.py example/thesis-demo.md --pdf --out example/output --backend libreoffice
```

## 提交内容

建议提交：

- `thesis_md2docx/` 中的源码改动；
- `example/thesis-demo.md` 中的示例更新；
- `README.md`、`CONTRIBUTING.md` 等文档更新。

不建议提交：

- `example/output/*.docx`；
- `example/output/*.pdf`；
- `example/output/pages/*.png`；
- `example/preview/`；
- `thesis_md2docx/math/latex2omml_node/node_modules/`；
- 本地临时文件、缓存和手工备份文件。

## 格式类改动

如果改动标题、页边距、正文、图题、表题、参考文献、公式或目录相关逻辑，请在说明中写清楚：

- 修改前的问题；
- 对应的学校规范或范例位置；
- 导出后的检查方式；
- 是否会影响已有 Markdown 写法。

`tests/test_docx_golden.py` 会检查示例 DOCX 的稳定 OOXML 部件 hash。若确实有意调整版式，
运行 `python tools/regenerate_golden.py` 更新 hash，并在提交说明中写清楚变更原因。

`tests/test_docx_golden.py` 还固定了两条与版面无关的约束，改动时不要破坏它们：

- `word/settings.xml` 不写 `<w:updateFields/>`，且文档里**不能有任何 `w:dirty="true"` 的域**。
  这两者都会让 Word 在打开文档时弹出「该文档包含的域可能引用了其他文件」，而文档其实没有任何
  外部引用。目录页码改由 `md2docx refresh-fields`（或用户在 Word 中更新一次目录）写入。
- 文档内不出现外部关系与 `INCLUDETEXT` / `INCLUDEPICTURE` / `RD` 等引用外部文件的域。

改动 Word 自动化相关代码时，建议实测一次完整链路：

```bash
python md2docx.py example/thesis-demo.md --out example/output
python md2docx.py refresh-fields example/output/thesis-demo.docx
python md2docx.py pdf example/output/thesis-demo.docx example/output/thesis-demo.pdf --backend word
```
