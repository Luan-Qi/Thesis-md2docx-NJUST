from __future__ import annotations

from thesis_md2docx.profiles.njust_master_thesis.body import (
    body_parse_rules,
    normalize_appendix_heading,
    normalize_appendix_references,
)
from thesis_md2docx.profiles.njust_master_thesis.frontmatter import build_keyword_paragraph


def test_njust_formula_numbers_use_a_dot_separator() -> None:
    """规范 9：公式按所处层次编号并用圆括号括起来，示例 （2.3）。"""

    rules = body_parse_rules()
    scope = rules.formula_scope(
        in_appendix=False,
        current_appendix_index=0,
        current_chapter_number="2",
    )
    assert scope == "2"
    assert rules.format_formula_number("2", 3) == "（2.3）"
    assert rules.format_formula_number("1", 1) == "（1.1）"


def test_njust_appendix_formula_numbers_use_a_letter() -> None:
    rules = body_parse_rules()
    scope = rules.formula_scope(
        in_appendix=True,
        current_appendix_index=2,
        current_chapter_number="4",
    )
    assert scope == "B"
    assert rules.format_formula_number("B", 3) == "（B.3）"


def test_njust_caption_pattern_matches_figure_and_table_numbers() -> None:
    """规范 7 / 8：图号表号按章编排，形如 图2.1、表2.1；附录为 图B1、表B1。"""

    rules = body_parse_rules()
    assert rules.is_caption_paragraph("图2.1 实验装置示意图")
    assert rules.is_caption_paragraph("表2.1 主要性能指标")
    assert rules.is_caption_paragraph("图 2.1 带空格的写法")
    assert rules.is_caption_paragraph("图B1 附录中的图")
    assert rules.is_caption_paragraph("表B1 附录中的表")
    # 分图标记 a)、b)
    assert rules.is_caption_paragraph("图2.2(a) 分图示例")
    # 以句号结尾的普通正文不算图题
    assert not rules.is_caption_paragraph("图2.1 更适合用来展示最终回报，因为……。")
    assert rules.is_table_caption("表2.1 主要性能指标")
    assert not rules.is_table_caption("图2.1 实验装置示意图")


def test_njust_chapters_do_not_break_but_back_matter_does() -> None:
    """规范 3.2：正文各章不强制另页；结论/致谢/参考文献/附录 另页。"""

    rules = body_parse_rules()
    assert rules.level1_break_mode == "explicit"
    for text in ("绪论", "1 绪论", "2 相关工作", "5 结论与展望"):
        assert not rules.should_page_break_level1(text), text
    for text in ("结论", "致谢", "参考文献", "附录"):
        assert rules.should_page_break_level1(text), text
    # 带章号的写法同样命中
    assert rules.should_page_break_level1("6 结论")
    assert rules.should_page_break_level1("参考文献")


def test_njust_appendix_headings_and_references_are_normalised() -> None:
    """规范 11.4：附录A / 附录B，图表编号为 图B1 / 表B1。"""

    assert normalize_appendix_heading("附录 A 常用写法速查", 1) == "附录A 常用写法速查"
    assert normalize_appendix_heading("附录 B 常见公式速查", 2) == "附录B 常见公式速查"
    assert normalize_appendix_heading("附录", 2) == "附录B"
    assert normalize_appendix_references("如图A-1所示，见表A-2。", 2) == "如图B1所示，见表B2。"


def test_njust_headings_above_level_three_are_unnumbered_only_when_listed() -> None:
    rules = body_parse_rules()
    assert rules.is_unnumbered_heading("参考文献", in_appendix=False, level=1)
    assert rules.is_unnumbered_heading("致谢", in_appendix=False, level=1)
    assert not rules.is_unnumbered_heading("绪论", in_appendix=False, level=1)
    assert not rules.is_unnumbered_heading("结论与展望", in_appendix=False, level=1)


def test_njust_toc_includes_appendices_and_their_children() -> None:
    """规范 6.2：目录列出 一、二、三级标题及致谢、参考文献、附录等。"""

    rules = body_parse_rules()
    assert rules.is_toc_heading("附录", in_appendix=False, level=1)
    assert rules.is_toc_heading("附录A 常用写法速查", in_appendix=True, level=2)
    assert rules.is_unnumbered_heading("附录A 常用写法速查", in_appendix=True, level=2)
    assert not rules.is_toc_heading("四级标题", in_appendix=False, level=4)


def test_njust_keyword_separators_become_commas() -> None:
    """规范 6.1：关键词之间统一用逗号，不用分号。"""

    chinese = build_keyword_paragraph("排版；Markdown；OOXML", english=False)
    assert chinese is not None
    assert "关键词" in chinese
    assert "排版，Markdown，OOXML" in chinese
    assert "；" not in chinese

    english = build_keyword_paragraph("thesis formatting; Markdown; OOXML", english=True)
    assert english is not None
    assert "Key word" in english
    assert "thesis formatting, Markdown, OOXML" in english
    assert ";" not in english


def test_njust_keyword_paragraph_has_no_indentation() -> None:
    """规范 6.1：关键词段左右缩进与首行缩进均为 0。"""

    paragraph = build_keyword_paragraph("排版，Markdown", english=False)
    assert paragraph is not None
    assert 'w:firstLine="0"' in paragraph
    assert 'w:left="0"' in paragraph


def test_njust_empty_keywords_produce_no_paragraph() -> None:
    assert build_keyword_paragraph("", english=False) is None
    assert build_keyword_paragraph("   ", english=True) is None
