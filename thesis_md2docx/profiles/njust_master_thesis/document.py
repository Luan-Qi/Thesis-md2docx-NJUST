"""Document assembly for the NJUST master's thesis profile.

Section plan (规范 3.1 / 3.2). 前置部分**逐页分节**，共 5 节：

    section A   封面 + 声明 / 学位论文使用授权声明    no header, no page number
    section B1  中文摘要                              header shown, Roman from I
    section B2  英文摘要                              header shown, Roman continues
    section B3  目录                                  header shown, Roman continues
    section C   正文 … 附录                           header shown, Arabic from 1

逐页分节是刻意的：Word 会丢掉**手动分页符**之后第一段的「段前距」，但**分节符**不会。
之前把整个前置部分做成单节时，摘要 / Abstract / 目录 三个标题的段前距全部失效。
副作用是前置部分更容易凑成偶数页，从而避开 Word 在页码重启处插入的空白页。

In OOXML a section's properties live in the `w:sectPr` of the paragraph that ends it, so
`cover_sect` 关闭 A 节、`front_sect` 关闭 B1 节、`front_continue_sect` 关闭 B2/B3 节
（与 `front_sect` 相同，只是不重启页码），最后一节 C 的属性放在 body 末尾的 `sectPr`。

Chapters do **not** start a new page -- 规范 3.2 only requires that for
结论 / 致谢 / 参考文献 / 附录, which `BodyParseRules.level1_break_mode =
"explicit"` implements.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from ...builders.document import build_document_elements, collect_toc_entries
from ...layout import FrontMatterPageSpec
from ...markdown import extract_abstract_keyword_blocks, parse_cover_info, parse_markdown_document
from ...math.converter import MathConverter
from ...media import MediaManager
from ...ooxml.paragraphs import (
    add_section_to_paragraph_xml,
    page_break_xml,
    paragraph_xml,
    toc_cache_entry_paragraph_xml,
    toc_field_paragraph_xml,
)
from ...ooxml.xml import indent_xml, spacing_xml
from ...styles import StyleRole
from ...toc import TocEntry
from ..base import ThesisProfile
from .constants import (
    CN_KEYWORD_PREFIX,
    LINE_FIXED_20PT,
    TOC2_LEFT,
    TOC3_LEFT,
    TOC_TAB_POS,
)
from .frontmatter import (
    build_abstract_body_paragraph,
    build_blank_paragraph,
    build_cover_elements,
    build_declaration_elements,
    build_front_heading,
    build_keyword_paragraph,
    parse_cover_info as _parse_cover_info,
)
from .frontmatter import build_toc_heading
from .header_footer import set_document_title

#: 关键词前的空白段落数（规范 6.1：中英文摘要末段与关键词段之间保留 2 个空白段落）
KEYWORD_BLANK_PARAGRAPHS = 2


def section_break_paragraph_xml(sect_pr: str) -> str:
    """A section-closing paragraph that costs one point of height.

    Word needs a paragraph to carry the section break. A plain empty paragraph
    inherits the 12pt body font, and when the preceding content ends close to the
    bottom margin -- which the table of contents routinely does -- that paragraph
    spills onto a fresh page and leaves a blank page behind. Giving the paragraph
    mark a 1pt run keeps the break on the page it belongs to.
    """

    return (
        "<w:p><w:pPr>"
        + spacing_xml(before=0, after=0, line=1, line_rule="exact")
        + '<w:rPr><w:sz w:val="2"/><w:szCs w:val="2"/></w:rPr>'
        + sect_pr
        + "</w:pPr>"
        '<w:r><w:rPr><w:sz w:val="2"/><w:szCs w:val="2"/></w:rPr>'
        '<w:t xml:space="preserve"> </w:t></w:r>'
        "</w:p>"
    )


def _front_text(front_sections: dict[str, str], page: FrontMatterPageSpec) -> str:
    if page.source_key is None:
        return ""
    return front_sections.get(page.source_key, "").strip()


def _append_cover(
    elements: list[str],
    *,
    thesis_title: str,
    cover_info: dict[str, str],
    cover_assets_dir: Path | None,
    media_manager: MediaManager | None,
) -> None:
    elements.extend(
        build_cover_elements(
            thesis_title,
            cover_info,
            cover_assets_dir=cover_assets_dir,
            media_manager=media_manager,
        )
    )
    # 封面与声明之间的分页；声明页与封面同属一个「无页眉页码」的节。
    elements.append(page_break_xml())


def _append_declaration(
    elements: list[str],
    *,
    text: str,
    math_converter: MathConverter | None,
    reference_anchors: dict[str, str] | None,
) -> None:
    elements.extend(
        build_declaration_elements(
            text,
            math_converter=math_converter,
            reference_anchors=reference_anchors,
        )
    )


def _append_abstract(
    elements: list[str],
    *,
    page: FrontMatterPageSpec,
    text: str,
    math_converter: MathConverter | None,
    reference_anchors: dict[str, str] | None,
    section_sect: str | None = None,
) -> None:
    before, keywords, after = extract_abstract_keyword_blocks(text, page.keyword_prefix)
    if not before and not keywords and not after:
        return
    elements.append(
        build_front_heading(
            page.title,
            english=page.english,
            page_break_before=page.page_break_before,
        )
    )
    for paragraph in before:
        elements.append(
            build_abstract_body_paragraph(
                paragraph,
                english=page.english,
                math_converter=math_converter,
                reference_anchors=reference_anchors,
            )
        )
    keyword_paragraph = build_keyword_paragraph(keywords, english=page.english)
    if keyword_paragraph:
        for _ in range(KEYWORD_BLANK_PARAGRAPHS):
            elements.append(build_blank_paragraph(line=LINE_FIXED_20PT))
        elements.append(keyword_paragraph)
    for paragraph in after:
        elements.append(
            build_abstract_body_paragraph(
                paragraph,
                english=page.english,
                math_converter=math_converter,
                reference_anchors=reference_anchors,
            )
        )
    # 前置部分的每一页各自成节，用分节符而不是手动分页符换页。
    # 手动分页符之后 Word 会丢弃下一段落的「段前距」，摘要/Abstract/目录标题的
    # 段前空白就都不会出现；分节符不会。参考论文正是逐页分节（它有多组 sectPr）。
    if page.page_break_after:
        if section_sect:
            elements.append(section_break_paragraph_xml(section_sect))
        else:
            elements.append(page_break_xml())


def _append_toc(
    elements: list[str],
    *,
    thesis_profile: ThesisProfile,
    page: FrontMatterPageSpec,
    toc_entries: list[TocEntry],
    section_sect: str | None = None,
) -> None:
    """目录标题 + Word 目录域（含缓存条目、PAGEREF 与书签）。

    The section that closes the front matter is emitted as its own 1pt-high
    paragraph (see `section_break_paragraph_xml`) so that a TOC which happens to
    end near the bottom margin does not push the break onto a blank page.
    """

    elements.append(build_toc_heading(page.title))
    roles = thesis_profile.style_roles()
    toc_field_style = roles.require(StyleRole.TOC_FIELD)
    toc_level_styles = {
        1: roles.require(StyleRole.TOC_LEVEL1),
        2: roles.require(StyleRole.TOC_LEVEL2),
        3: roles.require(StyleRole.TOC_LEVEL3),
    }
    if not toc_entries:
        elements.append(
            toc_field_paragraph_xml(style=toc_field_style, line=LINE_FIXED_20PT, line_rule="exact")
        )
    else:
        for index, entry in enumerate(toc_entries):
            elements.append(
                toc_cache_entry_paragraph_xml(
                    entry,
                    first=index == 0,
                    close_field=index == len(toc_entries) - 1,
                    toc_field_style=toc_field_style,
                    toc_level_styles=toc_level_styles,
                    tab_pos=TOC_TAB_POS,
                    line=LINE_FIXED_20PT,
                    line_rule="exact",
                    level_indents={2: TOC2_LEFT, 3: TOC3_LEFT},
                )
            )
    if section_sect:
        elements.append(section_break_paragraph_xml(section_sect))


def build_document(
    text: str,
    *,
    thesis_profile: ThesisProfile,
    math_converter: MathConverter | None = None,
    reference_anchors: dict[str, str] | None = None,
    markdown_dir: Path | None = None,
    cover_assets_dir: Path | None = None,
    media_manager: MediaManager | None = None,
) -> tuple[list[str], str, str]:
    markdown_title, front_sections, body_text = parse_markdown_document(text)
    front_spec = thesis_profile.front_matter_spec()
    cover_info = parse_cover_info(front_sections.get(front_spec.cover_info_key, ""))
    thesis_title = cover_info.get("论文题目") or markdown_title or front_spec.default_title
    # The odd-page header prints the thesis title; the style bundle is built after
    # this function returns, so record it here.
    set_document_title(thesis_title)

    profile = thesis_profile.body_style_profile()
    layout = thesis_profile.document_layout()

    cover_sect = thesis_profile.section_from_spec(layout.cover)
    front_sect = thesis_profile.section_from_spec(layout.front_matter)
    # 前置部分逐页分节：只有第一页（摘要）重启罗马页码，后续页续排。
    front_continue_sect = thesis_profile.section_from_spec(
        replace(layout.front_matter, page_number_start=None)
    )
    body_sect = thesis_profile.section_from_spec(layout.body_start)

    body_rules = thesis_profile.body_parse_rules()
    toc_entries = collect_toc_entries(
        body_text,
        rules=body_rules,
        appendix_heading_normalizer=profile.appendix_heading_normalizer,
    )

    elements: list[str] = []
    front_started = False
    for page in thesis_profile.front_matter_plan().pages:
        if page.kind == "cover":
            _append_cover(
                elements,
                thesis_title=thesis_title,
                cover_info=cover_info,
                cover_assets_dir=cover_assets_dir,
                media_manager=media_manager,
            )
            continue
        if page.kind == "declaration":
            _append_declaration(
                elements,
                text=_front_text(front_sections, page),
                math_converter=math_converter,
                reference_anchors=reference_anchors,
            )
            # 关闭 A 节：封面与声明都不显示页眉与页码。
            elements.append(section_break_paragraph_xml(cover_sect))
            continue
        if page.kind == "taskbook":
            continue
        if page.kind == "abstract":
            _append_abstract(
                elements,
                page=page,
                text=_front_text(front_sections, page),
                math_converter=math_converter,
                reference_anchors=reference_anchors,
                section_sect=front_continue_sect if front_started else front_sect,
            )
            front_started = True
            continue
        if page.kind == "toc":
            _append_toc(
                elements,
                thesis_profile=thesis_profile,
                page=page,
                toc_entries=toc_entries,
                # 关闭最后一节前置页：目录页，罗马页码续排。
                section_sect=front_continue_sect,
            )
            continue

    body_elements, _has_section_breaks, _ = build_document_elements(
        body_text,
        profile=profile,
        rules=body_rules,
        treat_first_heading_as_title=False,
        math_converter=math_converter,
        reference_anchors=reference_anchors,
        markdown_dir=markdown_dir,
        media_manager=media_manager,
    )
    elements.extend(body_elements)
    return elements, body_sect, thesis_title


__all__ = ["build_document"]
