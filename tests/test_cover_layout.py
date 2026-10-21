from __future__ import annotations

import re

from thesis_md2docx.profiles.njust_master_thesis import frontmatter as fm
from thesis_md2docx.profiles.njust_master_thesis.constants import (
    COVER_FIELD_FILL_PT,
    COVER_TITLE_MIN_LINES,
)

PBDR = "<w:pBdr>"


def _cover_info(**overrides: str) -> dict[str, str]:
    info = {
        "分类号": "",
        "密级": "",
        "UDC": "",
        "作者姓名": "***",
        "导师姓名": "***",
        "导师职称": "教授",
        "学位类别": "工学硕士",
        "学科名称": "通信与信息系统",
        "研究方向": "交通智能感知",
        "论文提交时间": "2026年1月",
    }
    info.update(overrides)
    return info


def _spec(key: str) -> fm.CoverFieldSpec:
    return next(spec for spec in fm.NJUST_COVER_FIELD_ORDER if spec.source_key == key)


def _underlined_space_runs(paragraph: str) -> list[int]:
    """每段下划线 run 里的空格个数（按出现顺序）。"""

    counts: list[int] = []
    for run in re.findall(r"<w:r>.*?</w:r>", paragraph, re.S):
        if '<w:u w:val="single"/>' not in run:
            continue
        text = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", run))
        if text and not text.strip():
            counts.append(len(text))
    return counts


def _fill_width_pt(spec: fm.CoverFieldSpec, value: str) -> float:
    """按渲染模型的宽度（点）：前导空格 + 值 + 补齐空格。"""

    label_space = spec.label_size / 4.0
    value_space = spec.value_size / 4.0
    paragraph = fm._cover_field_row(spec, _cover_info()) or ""
    runs = _underlined_space_runs(paragraph)
    assert len(runs) == 2, paragraph  # 前导一段、补齐一段
    value_pt = sum(
        (spec.value_size / 2.0) if ord(ch) > 0x2000 else value_space for ch in value
    )
    return runs[0] * label_space + value_pt + runs[1] * value_space


def test_two_line_title_gets_one_rule_per_line() -> None:
    elements = fm._cover_title_block("基于雷达-视觉融合的\n不良天气船舶检测技术研究")

    assert len(elements) == 4  # 两行文字 + 两条横线
    assert PBDR not in elements[0]
    assert PBDR in elements[1]
    assert PBDR not in elements[2]
    assert PBDR in elements[3]


def test_single_line_title_still_gets_two_rules() -> None:
    elements = fm._cover_title_block("基于雷达-视觉融合的不良天气船舶检测技术研究")

    assert COVER_TITLE_MIN_LINES == 2
    assert len(elements) == 4
    assert sum(1 for element in elements if PBDR in element) == 2


def test_cover_rules_are_centered_and_narrower_than_the_text_column() -> None:
    title_rule = fm._cover_rule(7965)
    author_rule = fm._cover_rule(2874)

    for rule in (title_rule, author_rule):
        left = int(re.search(r'w:left="(\d+)"', rule).group(1))
        right = int(re.search(r'w:right="(\d+)"', rule).group(1))
        assert abs(left - right) <= 1  # 居中：左右缩进相等

    assert 'w:left="552"' in title_rule
    assert 'w:left="3098"' in author_rule


def test_cover_rule_rejects_widths_wider_than_the_text_column() -> None:
    try:
        fm._cover_rule(9070)
    except ValueError:
        return
    raise AssertionError("a rule as wide as the text column must be rejected")


def test_field_values_are_centered_so_longer_values_start_further_left() -> None:
    short = _underlined_space_runs(fm._cover_field_row(_spec("学位类别"), _cover_info()) or "")
    long = _underlined_space_runs(fm._cover_field_row(_spec("学科名称"), _cover_info()) or "")

    # 通信与信息系统（7 字）比 工学硕士（4 字）更长 → 值两边都要让出空间，
    # 所以前导空格与补齐空格**都**变少（这正是"居中"而不是"左对齐"的特征）。
    assert long[0] < short[0]
    assert long[1] < short[1]


def test_field_fill_width_stays_constant_across_values() -> None:
    for key in ("学位类别", "学科名称", "研究方向"):
        spec = _spec(key)
        value = _cover_info()[key]
        width = _fill_width_pt(spec, value)
        # 空格只能整数个，允许一格误差
        assert abs(width - COVER_FIELD_FILL_PT) <= 8, (key, width)


def test_declaration_page_paragraphs_snap_to_the_line_grid() -> None:
    elements = fm.build_declaration_elements("")

    # 「声  明」标题不吸附网格（范例继承 Normal 的固定值 20 磅）
    assert "<w:snapToGrid/>" not in elements[0]
    # 正文、签名行、空行、授权声明标题都吸附网格
    assert "".join(elements).count("<w:snapToGrid/>") >= 12


def test_page_geometry_declares_a_real_line_grid() -> None:
    from thesis_md2docx.profiles.njust_master_thesis.constants import PAGE_GEOMETRY

    assert PAGE_GEOMETRY.doc_grid_type in ("lines", "linesAndChars")
    assert PAGE_GEOMETRY.doc_grid_line_pitch == 326


def test_submit_date_row_only_condenses_the_value_run() -> None:
    spec = _spec("论文提交时间")
    paragraph = fm._cover_field_row(spec, _cover_info()) or ""

    runs = re.findall(r"<w:r>.*?</w:r>", paragraph, re.S)
    spaced = [run for run in runs if 'w:spacing w:val="-10"' in run]
    plain = [run for run in runs if 'w:spacing w:val="-10"' not in run]

    assert len(spaced) == 1, "只有值那一个 run 带 -10 字符间距"
    assert "2026" in "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", spaced[0]))
    # 标签与两段空格都不带字符间距——加了会让整行左移或变短（踩过）
    assert len(plain) == 3, "标签 + 前导空格 + 补齐空格 三段都不该带字符间距"
