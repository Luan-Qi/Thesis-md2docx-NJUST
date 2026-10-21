# Markdown Usage

Use `example/thesis-demo.md` as the canonical sample.

## Minimal Structure

```markdown
# 基于雷达-视觉融合的不良天气船舶检测技术研究

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

关键词：关键词1，关键词2

---

## ABSTRACT
English abstract.

Key word: keyword one

---

## 目录
这里可以放占位文字；导出器会写入 Word 目录域。

---

# 1 绪论
## 1.1 研究背景
正文。

# 5 结论与展望

# 致谢
致谢正文。

# 参考文献
[1] 作者. 文献题名[文献类型]. 出版信息.

# 附录
## 附录A 附加材料
附录正文。
```

## Rules

- Front matter uses level-two headings: `## 封面信息`, `## 声明`, `## 摘要`, `## ABSTRACT`, `## 目录`.
  There is **no taskbook** in a NJUST master's thesis.
- The 声明 page wording comes from 附件 2.5 and is inserted by the exporter; do not rewrite it.
  Only supply `研究生签名：` / `签字日期：`.
- Body starts at numbered level-one headings such as `# 1 绪论`. Up to four heading levels are
  supported; levels one to three enter the table of contents.
- Back matter order is 结论 → 致谢 → 参考文献 → 附录, each starting on a new page. Chapters do
  **not** force a page break.
- Put figure captions and table captions on their own lines: `图2.1 xxx` (below the figure) and
  `表2.1 xxx` (above the table). Appendices use `图B1` / `表B1`.
- Formula numbers are generated automatically as `（章.序号）`, e.g. `（2.3）`; appendices use
  `（A.1）`. Cite them in text as `式（2.3）`.
- Use relative image paths such as `img/pipeline.png`.
- Use `:::figure-row` for side-by-side figures.
- Use `<!-- thesis-table-split: 8, 10 -->` between a table title and table when a long table
  needs continuation splits.
- Write citation markers as `[1]`, `[1-3]`, or `[1，3-4]`.
- Keyword separators may be semicolons or commas; the exporter normalizes them to commas.

## Formula Notes

- Inline formulas use `$...$`.
- Block formulas use `$$...$$`.
- Install the Node helper to convert LaTeX into Word OMML:

  ```bash
  npm install --prefix thesis_md2docx/math/latex2omml_node
  ```

- Without formula dependencies, export still succeeds and formulas fall back to LaTeX text.
