"""NJUST headers and footers -- 规范 11.1 / 11.2.

Odd pages   : 「硕士学位论文」 TAB 「本论文题目」
Even pages  : 「章节号和章节名」 TAB 「硕士学位论文」
Footers     : page number on the outer edge -- odd pages right, even pages left.
Cover/声明  : header and page number hidden (用户要求).

The odd-page header contains the thesis title, which is only known once the
Markdown has been parsed. The exporter builds the document body first and the
style bundle second, so `document.py` records the resolved title here before
`style_bundle()` is called.
"""

from __future__ import annotations

from xml.sax.saxutils import escape

from ...constants import R_NS, W_NS
from ...ooxml.paragraphs import paragraph_xml
from ...ooxml.xml import field_char_run_xml, instr_text_run_xml, run_text_xml, tab_run_xml
from .constants import FONT_CN, FONT_EN, SIZE_XIAO_WU
from .styles import STYLE_FOOTER, STYLE_HEADER

#: 规范 11.1 -- 章节名取自一级标题样式。
HEADING_STYLE_NAME = "NJUST Heading 1"

DEGREE_LABEL = "硕士学位论文"

_document_title = {"value": ""}


def set_document_title(title: str) -> None:
    """Remember the thesis title for the odd-page header.

    A cover title may contain explicit line breaks for layout; the header must
    stay on one line, so the breaks are merged here.
    """

    text = (title or "").strip()
    parts = [part.strip() for part in text.splitlines() if part.strip()]
    if any("\u4e00" <= ch <= "\u9fff" for ch in text):
        _document_title["value"] = "".join(parts)
    else:
        _document_title["value"] = " ".join(parts)


def document_title() -> str:
    return _document_title["value"]


def _run_kwargs() -> dict[str, object]:
    return {
        "font_ascii": FONT_EN,
        "font_hansi": FONT_EN,
        "font_eastasia": FONT_CN,
        "size": SIZE_XIAO_WU,
    }


def _wrap(part_tag: str, paragraph: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:{part_tag} xmlns:w="{W_NS}" xmlns:r="{R_NS}">{paragraph}</w:{part_tag}>'
    )


def _header_paragraph(left_runs: list[str], right_text: str) -> str:
    runs = list(left_runs)
    runs.append(tab_run_xml())
    if right_text:
        runs.append(run_text_xml(right_text, **_run_kwargs()))
    return paragraph_xml(runs=runs, style=STYLE_HEADER, first_line_chars=0, first_line=0)


def odd_header_xml() -> str:
    """奇数页：左「硕士学位论文」，右论文题目。"""

    left = [run_text_xml(DEGREE_LABEL, **_run_kwargs())]
    return _wrap("hdr", _header_paragraph(left, document_title()))


def even_header_xml() -> str:
    """偶数页：左章节号与章节名（STYLEREF 域），右「硕士学位论文」。"""

    left = [
        field_char_run_xml("begin"),
        instr_text_run_xml(f' STYLEREF "{HEADING_STYLE_NAME}" \\* MERGEFORMAT '),
        field_char_run_xml("separate"),
        field_char_run_xml("end"),
    ]
    return _wrap("hdr", _header_paragraph(left, DEGREE_LABEL))


def empty_header_xml() -> str:
    return _wrap("hdr", paragraph_xml("", first_line_chars=0, first_line=0))


def _page_number_paragraph(*, align: str) -> str:
    runs = [
        field_char_run_xml("begin"),
        instr_text_run_xml("PAGE   \\* MERGEFORMAT "),
        field_char_run_xml("separate"),
        run_text_xml("1", **_run_kwargs()),
        field_char_run_xml("end"),
    ]
    return paragraph_xml(
        runs=runs,
        style=STYLE_FOOTER,
        align=align,
        first_line_chars=0,
        first_line=0,
    )


def odd_footer_xml() -> str:
    """奇数页页码靠右（页面外侧）。"""

    return _wrap("ftr", _page_number_paragraph(align="right"))


def even_footer_xml() -> str:
    """偶数页页码靠左（页面外侧）。"""

    return _wrap("ftr", _page_number_paragraph(align="left"))


def empty_footer_xml() -> str:
    return _wrap("ftr", paragraph_xml("", style=STYLE_FOOTER, first_line_chars=0, first_line=0))


# `escape` is imported for symmetry with the other profile modules and used by
# callers that embed the title in field results.
__all__ = [
    "DEGREE_LABEL",
    "HEADING_STYLE_NAME",
    "document_title",
    "empty_footer_xml",
    "empty_header_xml",
    "even_footer_xml",
    "even_header_xml",
    "odd_footer_xml",
    "odd_header_xml",
    "set_document_title",
    "escape",
]
