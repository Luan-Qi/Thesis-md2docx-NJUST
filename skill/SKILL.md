---
name: thesis-md2docx-njust
description: Use this skill when an agent needs to write, check, or export a Nanjing University of Science and Technology master's thesis as Markdown to DOCX/PDF with the Thesis-md2docx-NJUST repository. Covers environment checks, Markdown structure, formula conversion, PDF backend choice, and final layout verification.
---

# Thesis MD2DOCX NJUST Skill

Use this skill when the user wants an agent to work with a **Nanjing University of Science and
Technology master's thesis** maintained as Markdown and exported with the
`Thesis-md2docx-NJUST` repository.

Prefer Markdown as the source of truth. Treat DOCX/PDF files as generated outputs.

## Repository

The repository root must contain `md2docx.py`. If the current working directory is not the
repository root, set:

```bash
export THESIS_MD2DOCX_REPO=/path/to/Thesis-md2docx-NJUST
```

## Workflow

1. Locate the repository root. It must contain `md2docx.py`.
2. Check the environment:

   ```bash
   md2docx check
   ```

3. If the Markdown contains formulas, make sure the formula helper is installed:

   ```bash
   npm install --prefix thesis_md2docx/math/latex2omml_node
   ```

4. Check the source Markdown structure. Load `references/markdown-usage.md` when the document is
   missing front matter, numbered chapters, references, figures, tables, or appendices.
5. Export DOCX (the NJUST profile is the default, so `--profile` is not needed):

   ```bash
   md2docx thesis.md --out output
   ```

6. Export PDF and page images when layout preview is needed:

   ```bash
   md2docx thesis.md --pdf --pages --out output --backend word
   ```

7. Write real table-of-contents page numbers back into the DOCX before submission:

   ```bash
   md2docx refresh-fields output/thesis.docx
   ```

   The DOCX is generated **without** `w:updateFields` and **without** any
   `w:dirty` field, because either one makes Word pop up
   「该文档包含的域可能引用了其他文件」on every open even though the document
   references nothing external. The price is that the cached TOC page numbers
   are placeholders until this command (or a manual `Ctrl+A` + `F9` in Word)
   fills them in. The `--pdf` path does not need it: the Word backend updates
   fields before exporting.

8. For the repository example, `./export-example.sh` / `.ps1` / `.cmd` produce
   `example/output/thesis-demo.docx`, `example/output/thesis-demo.pdf`, and
   `example/output/pages/page-*.png`, and refresh the DOCX fields when Word is
   available.
9. Use the Word backend as the final layout baseline when available. Use LibreOffice for quick
   preview only; pandoc and MiKTeX cannot stand in for either.
10. Remind the user that final Word/WPS inspection is still required for pagination, figures,
    tables, formulas, and references.

## What the NJUST format requires

- Paper A4, margins 上 30mm / 下 24mm / 左右 25mm, header and footer 20mm, mirror margins.
- 固定值 20 磅行距; 正文小四号宋体; 标题一至三级 小三/四号/小四号加粗居左.
- 摘要 / Abstract / 目录 / 致谢 / 参考文献 / 附录 都是不编号的一级标题，三号加粗居中。
- 致谢 / 参考文献 / 附录 各自另页；**正文每一章不强制另页**。
- 图表编号为 `图2.1` / `表2.1`，附录为 `图B1` / `表B1`；公式按章编号为 `（2.3）`。
- 奇数页页眉「硕士学位论文 + 论文题目」，偶数页页眉「章节名 + 硕士学位论文」。
- 页码位于页面外侧：奇数页靠右、偶数页靠左；前置部分用罗马数字，正文起用阿拉伯数字。
- 声明页的声明与学位论文使用授权声明正文由导出器按附件 2.5 原样写入，
  **不要要求用户改写或覆盖这两段文字**。

## References

- `references/markdown-usage.md`: Markdown writing conventions and minimal structure.
- `references/pdf-backends.md`: Word, LibreOffice, and auto PDF backend guidance.
- `references/troubleshooting.md`: common warnings, formula dependency issues, and layout checks.

## Operating Rules

- Do not hand-edit generated DOCX as the long-term source.
- Fix Markdown, profile code, or exporter code instead.
- Keep generated DOCX/PDF files and preview images out of Git; prefer source files at the paper
  root and generated files under `output/`.
- Use profile `njust-master-thesis` (the default) for NJUST master's thesis output.
- When comparing output, focus first on page sections, headings, body indentation, captions,
  formulas, references, header/footer parity, and PDF pagination.
