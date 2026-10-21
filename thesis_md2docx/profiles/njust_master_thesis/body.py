"""Body parsing rules and render hooks for the NJUST master's thesis profile.

Rules come from 规范 3 / 4 / 6.2 / 7 / 8 / 9 / 11.3 / 11.4:

* formula numbers use `（章.序）`, e.g. `（2.3）` (规范 9);
* chapters do **not** force a page break -- only 结论/致谢/参考文献/附录 do
  (规范 3.2);
* 图题/表题 use `图2.1` / `表2.1` (规范 7 / 8);
* headings keep going to a fourth level (规范 4.3).
"""

from __future__ import annotations

import re
from typing import Mapping
from xml.sax.saxutils import escape

from ...body_rules import BodyParseRules
from ...ooxml.parts import native_sect_pr_xml
from ...ooxml.render import (
    paragraph_with_inline_math_xml,
    paragraph_xml,
    reference_bookmark_id,
    reference_bookmark_name,
    text_runs,
)
from ...ooxml.tables import table_xml
from ...ooxml.xml import indent_xml, run_text_xml, spacing_xml
from ...styles import BodyRenderProfile, BodyStyleRefs, ParagraphFormatSpec, RunFormatSpec, StyleRole
from ...table_utils import parse_bool_option, parse_int_option
from .constants import (
    BODY_FIRST_LINE,
    BODY_FIRST_LINE_CHARS,
    FONT_CN,
    FONT_EN,
    LINE_FIXED_20PT,
    LINE_KAI_HALF,
    PAGE_BREAK_HEADINGS,
    PAGE_GEOMETRY,
    SIZE_SI,
    SIZE_WU,
    SIZE_XIAO_SI,
    UNNUMBERED_HEADINGS,
)
from .styles import STYLE_HEADING_1, njust_style_roles

FIGURE_ROW_START_PATTERN = re.compile(r"^:::\s*figure-row\s*$")
FIGURE_ROW_END_PATTERN = re.compile(r"^:::\s*$")
TABLE_SPLIT_COMMENT_PATTERN = re.compile(
    r"^<!--\s*thesis-table-split\s*:\s*(?P<spec>\d+(?:\s*,\s*\d+)*)\s*-->\s*$"
)

#: 规范 7 / 8：图号、表号按章编排，形如 `图2.1`、`表2.1`；附录为 `图B1`、`表B1`。
CAPTION_PATTERN = re.compile(r"^[图表]\s*(?:\d+(?:[.\-]\d+)*|[A-Z]\d*)(?:\([a-zA-Z]\))?\s+\S")
CHAPTER_NUMBER_PATTERN = re.compile(r"^(\d+)\b")
REFERENCE_ENTRY_PATTERN = re.compile(r"^\[\d+\]")

#: 规范 9：正文引用写作 `式（2.3）`；参考文献引用允许 `文献[4]` 或上标 `[4]`。
FORMULA_NUMBER_TEMPLATE = "（{scope}.{number}）"


class NjustBodyParseRules(BodyParseRules):
    """规范 9 用点号分隔章号与序号，上游默认用连字符。"""

    def format_formula_number(self, scope: str, number: int) -> str:
        return FORMULA_NUMBER_TEMPLATE.format(scope=scope, number=number)

    def formula_scope(
        self,
        *,
        in_appendix: bool,
        current_appendix_index: int,
        current_chapter_number: str,
    ) -> str | None:
        """规范 11.4 用字母标识附录，因此附录公式编号写作 （A.1）、（B.3）。"""

        if in_appendix and current_appendix_index > 0:
            return _appendix_letter(current_appendix_index)
        return current_chapter_number or None


def body_parse_rules() -> BodyParseRules:
    return NjustBodyParseRules(
        reference_heading="参考文献",
        acknowledgement_heading="致谢",
        acknowledgement_display_text="致  谢",
        appendix_heading="附录",
        appendix_display_text="附  录",
        appendix_formula_scope_prefix="附录",
        appendix_item_level=2,
        appendix_child_headings_unnumbered=True,
        unnumbered_headings=UNNUMBERED_HEADINGS,
        toc_excluded_headings=frozenset(),
        toc_exclude_appendix_children=False,
        level1_break_mode="explicit",
        explicit_page_break_headings=PAGE_BREAK_HEADINGS,
        reference_entry_pattern=REFERENCE_ENTRY_PATTERN,
        caption_pattern=CAPTION_PATTERN,
        table_caption_prefixes=("表",),
        table_split_pattern=TABLE_SPLIT_COMMENT_PATTERN,
        figure_row_start_pattern=FIGURE_ROW_START_PATTERN,
        figure_row_end_pattern=FIGURE_ROW_END_PATTERN,
        chapter_number_pattern=CHAPTER_NUMBER_PATTERN,
    )


# ---------------------------------------------------------------------------
# Appendix normalisation -- 规范 11.4：附录A / 附录B，图表为 图B1 / 表B1
# ---------------------------------------------------------------------------


def normalize_appendix_heading(text: str, appendix_index: int) -> str:
    """规范 11.4：附录序号编排为 附录A、附录B…。"""

    cleaned = re.sub(r"^附\s*录\s*[A-Z0-9]*[\s、.．]*", "", text).strip()
    if cleaned:
        return f"附录{_appendix_letter(appendix_index)} {cleaned}"
    return f"附录{_appendix_letter(appendix_index)}"


def _appendix_letter(index: int) -> str:
    if 1 <= index <= 26:
        return chr(ord("A") + index - 1)
    return str(index)


def normalize_appendix_references(text: str, appendix_index: int) -> str:
    """规范 11.4：附录图表编号为 图B1 / 表B1，不带点号。"""

    letter = _appendix_letter(appendix_index)
    return re.sub(r"([图表])\s*[A-Z]-(\d+)", lambda m: f"{m.group(1)}{letter}{m.group(2)}", text)


def strip_heading_prefix(text: str) -> str:
    stripped = re.sub(r"^\d+(?:\.\d+)*\s+", "", text).strip()
    return stripped or text.strip()


# ---------------------------------------------------------------------------
# Body render hooks
# ---------------------------------------------------------------------------


def heading_paragraph_xml(
    text: str,
    level: int,
    profile: BodyRenderProfile,
    *,
    numbered: bool = True,
    keep_with_next: bool = True,
) -> str:
    """规范 4.3：一至三级标题加粗宋体、居左，段前段后分别 18/12/6 磅。"""

    styles = profile.styles
    style = {
        1: styles.heading1,
        2: styles.heading2,
        3: styles.heading3,
        4: styles.heading4 or styles.heading3,
    }.get(level, styles.heading3)

    if numbered:
        heading_text = strip_heading_prefix(text) if profile.strip_heading_numbers else text.strip()
        return paragraph_xml(
            heading_text,
            style=style,
            align="left",
            ppr_extra=indent_xml(left=0, first_line_chars=0, first_line=0),
        )

    # 不编号：显式把编号清掉，标题本身仍用一级标题样式。
    ppr_extra = (
        '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="0"/></w:numPr>'
        + indent_xml(left=0, first_line_chars=0, first_line=0)
    )
    return paragraph_xml(text.strip(), style=style, align="left", ppr_extra=ppr_extra)


def acknowledgement_heading_paragraph_xml(text: str, profile: BodyRenderProfile) -> str:
    """致谢标题：规范 4.4 要求不编号的一级标题、三号加粗、居中。"""

    ppr_extra = (
        '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="0"/></w:numPr>'
        '<w:snapToGrid w:val="0"/>'
        + spacing_xml(before=360, after=360, line=LINE_FIXED_20PT, line_rule="exact")
        + indent_xml(left=0, first_line_chars=0, first_line=0)
    )
    return paragraph_xml(text.strip(), style=profile.styles.front_heading, align="center", ppr_extra=ppr_extra)


def caption_paragraph_xml(
    text: str,
    *,
    style: str | None = None,
    english: bool = False,
    math_converter=None,
    reference_anchors: dict[str, str] | None = None,
    keep_next: bool = False,
) -> str:
    """规范 7 / 8：图题在图下、表题在表上，五号宋体，西文 Times New Roman。"""

    run_kwargs = {
        "font_ascii": FONT_EN,
        "font_hansi": FONT_EN,
        "font_eastasia": FONT_EN if english else FONT_CN,
        "size": SIZE_WU,
    }
    ppr_extra = (
        spacing_xml(before=0, after=0, line=LINE_FIXED_20PT, line_rule="exact")
        + indent_xml(left=0, first_line_chars=0, first_line=0)
    )
    if keep_next:
        ppr_extra += "<w:keepNext/>"
    return paragraph_with_inline_math_xml(
        text,
        style=style,
        align="center",
        ppr_extra=ppr_extra,
        run_kwargs=run_kwargs,
        math_converter=math_converter,
        reference_anchors=reference_anchors,
    )


def chapter_section_break_paragraph_xml(sect_pr: str) -> str:
    return paragraph_xml(
        style=STYLE_HEADING_1,
        ppr_extra=spacing_xml(line=LINE_FIXED_20PT, line_rule="exact")
        + indent_xml(left=0, first_line_chars=0, first_line=0)
        + sect_pr,
    )


def reference_paragraph_xml(text: str, reference_anchors: dict[str, str] | None = None) -> str:
    """规范 11.3：小四号宋体、固定值 20 磅；`[n]` 加书签便于正文跳转。"""

    run_kwargs = {
        "font_ascii": FONT_EN,
        "font_hansi": FONT_EN,
        "font_eastasia": FONT_CN,
        "size": SIZE_XIAO_SI,
    }
    ppr_extra = (
        spacing_xml(after=0, line=LINE_FIXED_20PT, line_rule="exact")
        + indent_xml(left=0, first_line_chars=0, first_line=0)
    )
    match = re.match(r"^\[(\d+)\]\s*(.*)$", text)
    if not match:
        return paragraph_with_inline_math_xml(
            text,
            style=reference_style(),
            ppr_extra=ppr_extra,
            run_kwargs=run_kwargs,
            reference_anchors=reference_anchors,
        )
    ref_id, rest = match.groups()
    anchor = (
        reference_anchors.get(ref_id, reference_bookmark_name(ref_id))
        if reference_anchors
        else reference_bookmark_name(ref_id)
    )
    bookmark_id = reference_bookmark_id(ref_id)
    runs = [
        f'<w:bookmarkStart w:id="{bookmark_id}" w:name="{escape(anchor)}"/>',
        run_text_xml(f"[{ref_id}] ", **run_kwargs),
        f'<w:bookmarkEnd w:id="{bookmark_id}"/>',
    ]
    if rest:
        runs.extend(text_runs(rest, run_kwargs=run_kwargs))
    return paragraph_xml(style=reference_style(), runs=runs, ppr_extra=ppr_extra)


def reference_style() -> str:
    from .styles import STYLE_REFERENCE

    return STYLE_REFERENCE


def figure_image_paragraph_xml(
    item,
    media_manager,
    *,
    alt_text: str = "",
    width_emu: int | None = None,
    height_emu: int | None = None,
    crop_top: int | None = None,
    crop_right: int | None = None,
    crop_bottom: int | None = None,
    crop_left: int | None = None,
    options: Mapping[str, str] | None = None,
) -> str:
    """规范未规定图片默认宽度/环绕；沿用「居中、段前后 0、单倍行距」。

    行距必须是单倍（`line=240 lineRule=auto`）。固定值行距会把图片按行高裁剪，
    整幅图显示不全；参考论文的图片段落实测为单倍行距。
    """

    from ...ooxml.render import image_paragraph_xml

    style = None
    align: str | None = "center"
    ppr_extra = (
        spacing_xml(before=0, after=0, line=LINE_KAI_HALF, line_rule="auto")
        + indent_xml(left=0, first_line_chars=0, first_line=0)
    )
    keep_next = True

    if options:
        style_text = options.get("p_style", options.get("paragraph_style", "")).strip()
        if style_text and style_text.lower() not in {"none", "omit"}:
            style = style_text
        align_text = options.get("align", options.get("jc", "")).strip().lower()
        if align_text in {"none", "omit"}:
            align = None
        elif align_text:
            align = align_text
        spacing_parts = spacing_xml(
            line=parse_int_option(options, "line"),
            before=parse_int_option(options, "before"),
            after=parse_int_option(options, "after"),
            before_lines=parse_int_option(options, "before_lines"),
            after_lines=parse_int_option(options, "after_lines"),
            line_rule=options.get("line_rule", "auto"),
        )
        if spacing_parts:
            ppr_extra = spacing_parts
        if "keep_next" in options:
            keep_next = parse_bool_option(options, "keep_next", default=True)

    return image_paragraph_xml(
        item,
        media_manager,
        alt_text=alt_text,
        width_emu=width_emu,
        height_emu=height_emu,
        crop_top=crop_top,
        crop_right=crop_right,
        crop_bottom=crop_bottom,
        crop_left=crop_left,
        style=style,
        align=align,
        ppr_extra=ppr_extra,
        keep_next=keep_next,
        local_dpi=True,
        no_change_arrows=True,
    )


def section_pr_builder(**kwargs) -> str:
    return native_sect_pr_xml(geometry=PAGE_GEOMETRY, **kwargs)


def body_style_profile() -> BodyRenderProfile:
    styles = njust_style_roles()
    return BodyRenderProfile(
        styles=BodyStyleRefs(
            title=styles.require(StyleRole.BODY_HEADING_LEVEL1),
            heading1=styles.require(StyleRole.BODY_HEADING_LEVEL1),
            heading2=styles.require(StyleRole.BODY_HEADING_LEVEL2),
            heading3=styles.require(StyleRole.BODY_HEADING_LEVEL3),
            heading4=styles.require(StyleRole.BODY_HEADING_LEVEL4),
            normal=styles.require(StyleRole.BODY_NORMAL),
            quote=styles.require(StyleRole.QUOTE_BLOCK),
            code=styles.require(StyleRole.CODE_BLOCK),
            math=styles.require(StyleRole.MATH_BLOCK),
            image=styles.require(StyleRole.BODY_IMAGE),
            table_cell=styles.require(StyleRole.TABLE_CELL),
            caption=styles.require(StyleRole.CAPTION_DEFAULT),
            front_heading=styles.require(StyleRole.FRONT_HEADING),
        ),
        normal_paragraph=ParagraphFormatSpec(
            ppr_extra=spacing_xml(after=0, line=LINE_FIXED_20PT, line_rule="exact"),
            first_line_chars=BODY_FIRST_LINE_CHARS,
            first_line=BODY_FIRST_LINE,
        ),
        normal_run=RunFormatSpec(
            font_ascii=FONT_EN,
            font_hansi=FONT_EN,
            font_eastasia=FONT_CN,
            size=SIZE_XIAO_SI,
        ),
        code_paragraph=ParagraphFormatSpec(),
        strip_heading_numbers=True,
        heading_builder=heading_paragraph_xml,
        acknowledgement_heading_builder=acknowledgement_heading_paragraph_xml,
        caption_builder=caption_paragraph_xml,
        reference_builder=reference_paragraph_xml,
        image_builder=figure_image_paragraph_xml,
        table_builder=table_xml,
        appendix_heading_normalizer=normalize_appendix_heading,
        appendix_reference_normalizer=normalize_appendix_references,
        section_pr_builder=section_pr_builder,
        chapter_section_break_builder=chapter_section_break_paragraph_xml,
    )


__all__ = [
    "NjustBodyParseRules",
    "body_parse_rules",
    "body_style_profile",
    "normalize_appendix_heading",
    "normalize_appendix_references",
]
