"""表格行拆分：公式 / 行内代码里的 `|` 不能被当成列分隔符。"""

from __future__ import annotations

from thesis_md2docx.table_utils import (
    expanded_column_count,
    is_table_separator,
    parse_table_row,
    split_markdown_row,
)


def test_pipe_inside_inline_math_does_not_split_the_cell() -> None:
    row = r"| 方向门限 | $\left|\cos\theta\right|_{\min}$ | 0.15 | 低于该值跳过本周期 |"

    cells = split_markdown_row(row)

    assert len(cells) == 4
    assert cells[1] == r"$\left|\cos\theta\right|_{\min}$"


def test_pipe_inside_inline_code_does_not_split_the_cell() -> None:
    cells = split_markdown_row("| `a | b` | 0.15 |")

    assert len(cells) == 2
    assert cells[0] == "`a | b`"


def test_escaped_pipe_becomes_a_literal_pipe() -> None:
    cells = split_markdown_row(r"| a \| b | c |")

    assert len(cells) == 2
    assert cells[0] == "a | b"


def test_escaped_pipe_inside_math_stays_a_latex_command() -> None:
    cells = split_markdown_row(r"| $\|x\|_2$ | 范数 |")

    assert len(cells) == 2
    assert cells[0] == r"$\|x\|_2$"


def test_unbalanced_dollar_sign_does_not_swallow_the_rest_of_the_row() -> None:
    # 没有配对的 `$` 时按普通字符处理，否则整行后半段都会被吞进一个单元格。
    cells = split_markdown_row("| $x | y | z |")

    assert len(cells) == 3
    assert cells == ["$x", "y", "z"]


def test_table_rows_keep_the_header_column_count() -> None:
    header = "| 参数 | 取值 | 指标 | 说明 |"
    body = r"| 方向门限 | $\left|\cos\theta\right|_{\min}$ | 0.15 | 低于该值跳过本周期 |"
    other = r"| 测距 | $3\sigma$ | 0.30 m | 用于门限 |"

    rows = [parse_table_row(header), parse_table_row(body), parse_table_row(other)]

    assert expanded_column_count(rows) == 4
    assert all(len(row) == 4 for row in rows)


def test_separator_row_still_recognised() -> None:
    assert is_table_separator("| --- | :---: | ---: |")
    assert not is_table_separator(r"| $\left|x\right|$ | --- |")
