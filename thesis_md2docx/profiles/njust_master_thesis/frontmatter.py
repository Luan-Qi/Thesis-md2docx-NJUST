"""Front matter rendering for the NJUST master's thesis profile.

Cover layout coordinates are reverse-engineered from the university's own
already-typeset thesis (`_anno.docx`), which the project owner approved as the
source for layout values the written specification deliberately leaves open.
Fonts, sizes and paragraph spacing come from the specification and its 附件批注.

The two declarations are reproduced verbatim from 附件 2.5, because 规范 2.3
requires their wording to be used without any change.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ...constants import DEFAULT_LOCAL_COVER_ASSETS_REL
from ...frontmatter import parse_inline_image_value
from ...markdown import parse_cover_info, split_cover_title_lines
from ...math.converter import MathConverter
from ...media import MediaImage, MediaManager
from ...ooxml.images import image_paragraph_xml
from ...ooxml.paragraphs import paragraph_with_inline_math_xml, paragraph_xml
from ...ooxml.xml import indent_xml, run_text_xml, spacing_xml
from .constants import (
    AFTER_TOC_TITLE,
    AUTHORISATION_BODY,
    AUTHORISATION_SIGNATURE_UNDERLINE,
    AUTHORISATION_TITLE,
    BEFORE_H1,
    BEFORE_TOC_TITLE,
    CN_KEYWORD_PREFIX,
    CN_KEYWORD_SEPARATOR,
    COVER_ASSET_NAME,
    COVER_ASSET_LOCAL_REL,
    COVER_AUTHOR_HINT,
    COVER_AUTHOR_HINT_LINE,
    COVER_DEGREE_FIRST_LINE,
    COVER_DEGREE_FIRST_LINE_CHARS,
    COVER_FIELD_BEFORE,
    COVER_FIELD_BEFORE_LINES,
    COVER_FIELD_FIRST_LINE,
    COVER_FIELD_FIRST_LINE_CHARS,
    COVER_FIELD_FIRST_LINE_SHORT,
    COVER_FIELD_TAB_PT,
    COVER_AUTHOR_BLANK_LINE,
    COVER_FIELD_GAP_SPACES,
    COVER_FIELD_FILL_PT,
    COVER_FIELD_LABEL_UNITS,
    COVER_FIELD_UNDERLINE_PT,
    COVER_FIELD_VALUE_CENTER_PT,
    COVER_LOGO_HEIGHT_EMU,
    COVER_LOGO_WIDTH_EMU,
    COVER_RULE_AUTHOR_WIDTH,
    COVER_RULE_TITLE_WIDTH,
    COVER_SIGNATURE_RIGHT,
    COVER_SUBMIT_CHAR_SPACING,
    COVER_TITLE_HINT,
    COVER_TITLE_HINT_LINE,
    COVER_TITLE_MIN_LINES,
    COVER_TOP_BEFORE,
    COVER_TOP_BEFORE_LINES,
    COVER_TOP_FIRST_LINE,
    COVER_TOP_GAP_PT,
    COVER_TOP_TAB_CENTER,
    COVER_TOP_TAB_RIGHT,
    COVER_TOP_UNDERLINE_PT,
    COVER_TOP_UNDERLINE_RIGHT_PT,
    COVER_UDC_LABEL,
    COVER_UDC_NOTE,
    COVER_UDC_UNDERLINE_PT,
    COVER_UNSPECIFIED_FIELD_SIZE,
    DECLARATION_BODY,
    DECLARATION_FIRST_LINE,
    DECLARATION_SIGNATURE_UNDERLINE,
    DECLARATION_TITLE,
    DECLARATION_TITLE_FIRST_LINE,
    DECLARATION_TITLE_FIRST_LINE_CHARS,
    DECLARATION_TITLE_LINE,
    EN_KEYWORD_PREFIX,
    EN_KEYWORD_SEPARATOR,
    FONT_CN,
    FONT_CN_HEI,
    FONT_CN_HWZS,
    FONT_CN_KAI,
    FONT_EN,
    KEYWORD_BLANK_PARAGRAPHS,
    LINE_FIXED_20PT,
    LINE_KAI_HALF,
    LINE_KAI_28PT,
    SIGNATURE_DATE,
    SIGNATURE_DATE_GAP,
    SIGNATURE_LABEL,
    SIZE_COVER_DEGREE,
    SIZE_SAN,
    SIZE_SI,
    SIZE_WU,
    SIZE_XIAO_ER,
    SIZE_XIAO_SI,
    SIZE_XIAO_YI,
    TEXT_WIDTH,
)
from .styles import STYLE_BODY, STYLE_FRONT_HEADING

# ---------------------------------------------------------------------------
# Cover field specification
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CoverFieldSpec:
    """One labelled fill-in row on the cover."""

    source_key: str
    label: str
    value_size: int = COVER_UNSPECIFIED_FIELD_SIZE
    #: 填写内容的中文字体。封面填写项一律中文楷体 + 西文 Times New Roman。
    value_font: str = FONT_CN_KAI
    value_bold: bool = True
    label_bold: bool = True
    #: 标签字号。范例标签为四号，不随填写内容放大。
    label_size: int = SIZE_SI
    first_line: int = COVER_FIELD_FIRST_LINE
    #: 段前。范例只给字段块的第一行（导师姓名）写了段前，且同时写了 beforeLines
    #: 与 before —— Word 取 beforeLines，故实际段前是 1 行（28pt）。
    before: int = 0
    before_lines: int | None = None
    #: 字符间距（`w:spacing`，单位 twips/20）。范例只有「论文提交时间」行是 -10。
    char_spacing: int | None = None


#: 学术硕士学位论文封面字段 -- 规范 5.1 + 附件 2.1。
#: 批注明确给出的：学位类别标签 四号宋体加粗、导师姓名 三号楷体加粗、
#: 导师职称 四号楷体、作者姓名 小二号楷体加粗、题名 小一号黑体加粗。
NJUST_COVER_FIELD_ORDER: tuple[CoverFieldSpec, ...] = (
    CoverFieldSpec(
        "导师姓名",
        "指导教师姓名",
        value_size=SIZE_SAN,
        value_font=FONT_CN_KAI,
        before=COVER_FIELD_BEFORE,
        before_lines=COVER_FIELD_BEFORE_LINES,
    ),
    CoverFieldSpec("导师职称", "", value_size=SIZE_SI, value_font=FONT_CN_KAI, value_bold=False,
                   label_bold=False, first_line=281),
    CoverFieldSpec("学位类别", "学 位 类 别"),
    CoverFieldSpec("学科名称", "学 科 名 称"),
    CoverFieldSpec("研究方向", "研 究 方 向"),
    CoverFieldSpec(
        "论文提交时间",
        "论文提交时间",
        first_line=COVER_FIELD_FIRST_LINE_SHORT,
        char_spacing=COVER_SUBMIT_CHAR_SPACING,
    ),
)

#: 封面顶部的「分类号 / 密级」与「UDC」行。
COVER_TOP_KEYS: tuple[str, ...] = ("分类号", "密级", "UDC", "论文类别")
COVER_TITLE_KEY = "论文题目"
COVER_AUTHOR_KEY = "作者姓名"

COVER_NOTE = "注1：注明《国际十进分类法UDC》的类号。"


def resolve_cover_assets_dir(
    markdown_path: Path,
    assets_dir: Path | None,
    *,
    use_cover_assets: bool,
) -> Path | None:
    """Find the cover logo next to the Markdown first, then the given directory."""

    if not use_cover_assets:
        return None
    candidates: list[Path] = []
    local = markdown_path.parent / COVER_ASSET_LOCAL_REL
    candidates.append(local)
    candidates.append(markdown_path.parent)
    if assets_dir is not None:
        candidates.append(assets_dir)
    for directory in candidates:
        if directory.is_dir() and (directory / COVER_ASSET_NAME).is_file():
            return directory
    return None


# ---------------------------------------------------------------------------
# Low level run helpers
# ---------------------------------------------------------------------------


def _underlined_spaces(count: int, **run_kwargs: object) -> str:
    return run_text_xml(" " * count, underline=True, **run_kwargs)


def _spaces_for_pt(target_pt: float, size_half_points: int) -> int:
    """返回铺满 `target_pt` 点所需的半角空格个数（全角字 = 字号，空格 = 半字号）。"""

    return max(int(round(target_pt / (size_half_points / 2.0 / 2.0))), 1)


def _underlined_value(value: str, target_pt: float, size_half_points: int, **run_kwargs: object) -> str:
    """封面的填空位：空格占位 + **字体下划线**，并补齐到 `target_pt` 点的总宽度。

    参考封面用的是字体下划线（`w:u val="single"`）铺在空格上，不是制表位前导符——
    前导符画的是下划线字符，位置与粗细都和字体下划线不同。

    补空格数按宽度推算：全角字宽 = 字号，半角（含空格）= 字号的一半。
    这样即使某行字号不同（导师行三号、其余四号），所有行的下划线也等长。
    """

    size_pt = size_half_points / 2.0
    space_pt = size_pt / 2.0
    used = sum(size_pt if ord(ch) > 0x2000 else space_pt for ch in value)
    padding = max(int(round((target_pt - used) / space_pt)), 1)
    return run_text_xml(value + " " * padding, underline=True, **run_kwargs)


def _blank_line(
    *,
    line: int | None = LINE_KAI_HALF,
    size: int | None = None,
    snap_to_grid: bool = False,
) -> str:
    """空行；`line=None` 表示不写行距、交由所在样式决定。

    `snap_to_grid=True` 会写 `<w:snapToGrid/>`——声明页那些空行在范例里是**吸附
    网格**的，一行占 2 格（32.6pt），不是单倍行距的 18pt。少了这个开关，整页会
    比范例短一大截。

    注意 `pPr` 的子元素顺序是 ECMA 规定的硬约束，`w:snapToGrid` 必须排在
    `w:spacing` **之前**；写反了 Word 会静默忽略（踩过：正文吸附了、空行没吸附，
    整页少一格）。
    """

    ppr = "<w:snapToGrid/>" if snap_to_grid else ""
    if line is not None:
        ppr += spacing_xml(line=line, line_rule="auto" if line == LINE_KAI_HALF else "exact")
    if size is not None:
        # 空段落的高度由**段落标记**的字号决定，而不是空 run 的字号：字号必须写进
        # `pPr/rPr`（范例就是这么写的）。早期只写在空 run 上，Word 直接按 12pt
        # 算行高——声明页因此少了整整一格（16.3pt）。
        ppr += f'<w:rPr><w:sz w:val="{size}"/><w:szCs w:val="{size}"/></w:rPr>'
    return paragraph_xml(runs=[], ppr_extra=ppr)


# ---------------------------------------------------------------------------
# Cover
# ---------------------------------------------------------------------------


def _cover_top_line(cover_info: dict[str, str]) -> str:
    """分类号 / 密级 一行，五号宋体，下划线分列两侧制表位。

    两个值即使已填写也要画下划线——封面是表格化的填空页，范例里填好的
    「工学硕士」「通信与信息系统」同样带下划线。
    """

    kwargs = {"font_ascii": FONT_EN, "font_hansi": FONT_EN, "font_eastasia": FONT_CN, "size": SIZE_WU}
    value = (cover_info.get("分类号") or "").strip()
    secret = (cover_info.get("密级") or "").strip()
    # 范例逐 run 还原：分类号 + 下划线填空 + 普通空格 + 密级 + 下划线填空。
    # 密级靠普通空格推到右侧——是**位置**铺到页面两端，不是下划线铺满整行。
    runs = [
        run_text_xml("分类号", **kwargs),
        _underlined_value(value, COVER_TOP_UNDERLINE_PT, SIZE_WU, **kwargs),
        run_text_xml(" " * _spaces_for_pt(COVER_TOP_GAP_PT, SIZE_WU), **kwargs),
        run_text_xml("密级", **kwargs),
        _underlined_value(secret, COVER_TOP_UNDERLINE_RIGHT_PT, SIZE_WU, **kwargs),
    ]
    ppr = (
        '<w:tabs><w:tab w:val="center" w:pos="%d"/><w:tab w:val="right" w:pos="%d"/></w:tabs>'
        % (COVER_TOP_TAB_CENTER, COVER_TOP_TAB_RIGHT)
    ) + spacing_xml(
        before=COVER_TOP_BEFORE,
        before_lines=COVER_TOP_BEFORE_LINES,
        line=LINE_FIXED_20PT,
        line_rule="exact",
    ) + indent_xml(first_line=COVER_TOP_FIRST_LINE)
    return paragraph_xml(runs=runs, ppr_extra=ppr)


def _cover_udc_line(cover_info: dict[str, str]) -> str:
    kwargs = {"font_ascii": FONT_EN, "font_hansi": FONT_EN, "font_eastasia": FONT_CN, "size": SIZE_WU}
    value = (cover_info.get("UDC") or "").strip()
    # 附件2.1：UDC 行的「注1」是**上标**（vertAlign=superscript）并带下划线。
    # 范例该 run 的中文字体写死为「华文中宋」，与整行其余部分的宋体不同。
    note_kwargs = {**kwargs, "font_eastasia": FONT_CN_HWZS}
    ppr = spacing_xml(line=LINE_FIXED_20PT, line_rule="exact") + indent_xml(first_line=COVER_TOP_FIRST_LINE)
    return paragraph_xml(
        runs=[
            run_text_xml(COVER_UDC_LABEL, **kwargs),
            run_text_xml(COVER_UDC_NOTE, underline=True, superscript=True, **note_kwargs),
            _underlined_value(value, COVER_UDC_UNDERLINE_PT, SIZE_WU, **kwargs),
        ],
        ppr_extra=ppr,
    )


def _full_width_units(units: int) -> int:
    """把全角字个数换算成半角空格个数。"""

    return units * 2


def _cover_rule(width_twips: int = COVER_RULE_TITLE_WIDTH) -> str:
    """题名与作者姓名下方的独立横线。

    附件2.1 的封面在这两处各有一条横线；它既不是字体下划线，也不是段的下框线，
    而是独立的一条线（范例里是 wps 浮动直线，可精确到 0.1pt）。这里改用「段落
    下框线 + 左右等距缩进」实现，不引入 VML/形状：线段宽度 = 正文宽 − 左右缩进，
    因此本函数接收**线宽**并按正文宽均分缩进。

    范例实测线宽：题名下 7965 twips (140.4mm)、作者姓名下 2874 twips (50.7mm)，
    粗细都是 0.75pt（`a:ln w=9525`），与这里的 `w:sz="6"` 一致。
    `w:space="0"`：边框与段落边缘的距离取 0，线尽量贴近文字——范例的线是浮动
    形状、能落在文字行内部，段落下框线只能落到段落底部，这一步能补回约 1pt。
    """

    if width_twips >= TEXT_WIDTH:
        raise ValueError(f"cover rule width {width_twips} must be narrower than the text width {TEXT_WIDTH}")
    left = (TEXT_WIDTH - width_twips) // 2
    right = TEXT_WIDTH - width_twips - left
    return paragraph_xml(
        runs=[run_text_xml("")],
        align="center",
        ppr_extra=(
            "<w:pBdr>"
            '<w:bottom w:val="single" w:sz="6" w:space="0" w:color="auto"/>'
            "</w:pBdr>"
            + spacing_xml(before=0, after=0, line=1, line_rule="exact")
            + f'<w:ind w:left="{left}" w:right="{right}" w:firstLine="0" w:firstLineChars="0"/>'
        ),
    )


def _cover_hint(text: str, *, line: int) -> str:
    """封面模板保留的括号提示行，如 `(题名和副题名)` / `(作者姓名)`。

    范例中这两行分别是 line=360 / line=340（exact）、居中、无缩进。按用户要求
    让封面保持模板状态，因此照范例保留。
    """

    return paragraph_xml(
        runs=[run_text_xml(text, font_ascii=FONT_EN, font_hansi=FONT_EN, font_eastasia=FONT_CN)],
        align="center",
        ppr_extra=spacing_xml(line=line, line_rule="exact") + indent_xml(first_line_chars=0, first_line=0),
    )


def _cover_degree_label(cover_info: dict[str, str]) -> str:

    degree_kind = (cover_info.get("论文类别") or "").strip()
    text = degree_kind or "硕 士 学 位 论 文"
    return paragraph_xml(
        runs=[run_text_xml(text, font_ascii=FONT_CN_KAI, font_hansi=FONT_CN_KAI,
                           font_eastasia=FONT_CN_KAI, size=SIZE_COVER_DEGREE,
                           bold=True)],
        align="center",
        ppr_extra=spacing_xml(line=LINE_KAI_HALF, line_rule="auto")
        + indent_xml(first_line_chars=COVER_DEGREE_FIRST_LINE_CHARS, first_line=COVER_DEGREE_FIRST_LINE),
    )


def _cover_title(title: str) -> list[str]:
    """题名：小一号黑体加粗、居中，允许 Markdown 显式换行。

    附件 2.1 的题名区**每一行下方都有一条横线**，因此这里只负责文字行，
    横线由 `_cover_title_block()` 逐行补上。
    """

    lines = split_cover_title_lines(title)
    out: list[str] = []
    for line in lines:
        out.append(
            paragraph_xml(
                runs=[run_text_xml(line, font_ascii=FONT_CN_HEI, font_hansi=FONT_CN_HEI,
                                   font_eastasia=FONT_CN_HEI, size=SIZE_XIAO_YI, bold=True)],
                align="center",
                ppr_extra=spacing_xml(line=LINE_KAI_HALF, line_rule="auto")
                + indent_xml(first_line_chars=0, first_line=0),
            )
        )
    return out


def _cover_title_block(title: str) -> list[str]:
    """题名区：每行文字 + 其正下方的横线；不足两行时补一条空行再补横线。

    规范附件 2.1 的题名位于两条等宽横线之间（范例实测：两条 140.5mm 的线分别
    落在两行题名的正下方，相距 11mm = 一行题名高）。题名只有一行时，第二行留空
    但横线照画——用户明确要求"永远出现两行下划线"。
    """

    lines = _cover_title(title)
    if len(lines) < COVER_TITLE_MIN_LINES:
        lines.extend(
            _blank_line(line=LINE_KAI_HALF, size=SIZE_XIAO_YI)
            for _ in range(COVER_TITLE_MIN_LINES - len(lines))
        )
    out: list[str] = []
    for line in lines:
        out.append(line)
        out.append(_cover_rule(COVER_RULE_TITLE_WIDTH))
    return out


def _cover_author(cover_info: dict[str, str]) -> str:
    """作者姓名：小二号楷体加粗、居中。"""

    name = (cover_info.get(COVER_AUTHOR_KEY) or "").strip()
    kwargs = {
        "font_ascii": FONT_CN_KAI,
        "font_hansi": FONT_CN_KAI,
        "font_eastasia": FONT_CN_KAI,
        "size": SIZE_XIAO_ER,
        "bold": True,
    }
    runs = [run_text_xml(name, **kwargs)] if name else [_underlined_spaces(24, **kwargs)]
    return paragraph_xml(
        runs=runs,
        align="center",
        ppr_extra=spacing_xml(line=600, line_rule="exact") + indent_xml(right=COVER_SIGNATURE_RIGHT),
    )


def _cover_field_row(spec: CoverFieldSpec, cover_info: dict[str, str]) -> str | None:
    value = (cover_info.get(spec.source_key) or "").strip()
    if not value and not spec.label:
        return None
    label_kwargs = {
        "font_ascii": FONT_EN,
        "font_hansi": FONT_EN,
        "font_eastasia": FONT_CN,
        "size": spec.label_size,
        "bold": spec.label_bold,
    }
    value_kwargs = {
        "font_ascii": FONT_EN,
        "font_hansi": FONT_EN,
        "font_eastasia": spec.value_font,
        "size": spec.value_size,
        "bold": spec.value_bold,
    }
    if spec.char_spacing is not None:
        # 字符间距只加在**值**上：加到标签上会让填空位起点左移 1mm（踩过——
        # 「论文提交时间」那一行因此比其它五行短、且左端不齐），加到空格上会让
        # 整条填空位缩短（早前一次只剩 76mm）。空格与标签都保持原样。
        value_kwargs["spacing"] = spec.char_spacing
    label_pt = spec.label_size / 2.0
    label_space_pt = label_pt / 2.0
    spacing_pt = (spec.char_spacing or 0) / 20.0
    # 标签列宽固定为 6 个全角字（范例：「指导教师姓名」= 6 字；
    # 「学 位 类 别」只有 5.5 字宽，范例在该标签后多一个空格补到 6 字）。
    label_col_pt = COVER_FIELD_LABEL_UNITS * label_pt
    label_width_pt = sum(
        (label_pt if ord(ch) > 0x2000 else label_space_pt) for ch in spec.label
    )
    runs: list[str] = []
    if spec.label:
        trailing = max(int(round((label_col_pt - label_width_pt) / label_space_pt)), 0)
        runs.append(run_text_xml(spec.label + " " * trailing, **label_kwargs))
    else:
        # 无标签行（导师职称）：范例用**不带下划线**的空格把填空位推到与上面各行
        # 相同的起点（69.6mm），本身不画线。
        runs.append(
            run_text_xml(" " * _full_width_units(COVER_FIELD_LABEL_UNITS), **label_kwargs)
        )
    # 填空位 = 前导下划线空格 + 值 + 补齐下划线空格。两个约束：
    #   1. 总宽 = COVER_FIELD_FILL_PT（范例各行下划线等宽 86.8mm）；
    #   2. 值**居中**在 COVER_FIELD_VALUE_CENTER_PT 上——范例不是左对齐，
    #      所以「***」「教授」比下面几行靠右、而「通信与信息系统」比它们靠左。
    space_pt = spec.value_size / 4.0
    value_pt = sum(
        (spec.value_size / 2.0) if ord(ch) > 0x2000 else space_pt for ch in value
    )
    # 字符间距按"每字少 spacing_pt"计入值宽（spacing 是负值时值变窄）。
    value_pt = max(value_pt + spacing_pt * len(value), space_pt)
    lead_pt = COVER_FIELD_VALUE_CENTER_PT - value_pt / 2.0
    leading = max(int(round(lead_pt / label_space_pt)), 1)
    lead_pt = leading * label_space_pt
    padding = max(int(round((COVER_FIELD_FILL_PT - lead_pt - value_pt) / space_pt)), 1)
    # 空格 run 不带字符间距，否则下划线几何会跟着缩短。
    fill_kwargs = {k: v for k, v in label_kwargs.items() if k != "spacing"}
    value_space_kwargs = {k: v for k, v in value_kwargs.items() if k != "spacing"}
    runs.append(run_text_xml(" " * leading, underline=True, **fill_kwargs))
    runs.append(run_text_xml(value, underline=True, **value_kwargs))
    runs.append(run_text_xml(" " * padding, underline=True, **value_space_kwargs))
    ppr = (
        spacing_xml(
            before=spec.before or None,
            before_lines=spec.before_lines,
            line=LINE_KAI_28PT,
            line_rule="exact",
        )
        + indent_xml(first_line_chars=COVER_FIELD_FIRST_LINE_CHARS, first_line=spec.first_line)
    )
    return paragraph_xml(runs=runs, ppr_extra=ppr)


def _cover_logo(cover_assets_dir: Path | None, media_manager: MediaManager | None) -> list[str]:
    if cover_assets_dir is None or media_manager is None:
        return []
    logo_path = cover_assets_dir / COVER_ASSET_NAME
    if not logo_path.is_file():
        return []
    item: MediaImage | None = media_manager.register_image(logo_path)
    if item is None:
        return []
    return [
        image_paragraph_xml(
            item,
            media_manager,
            alt_text="南京理工大学校徽与校名",
            width_emu=COVER_LOGO_WIDTH_EMU,
            height_emu=COVER_LOGO_HEIGHT_EMU,
            align="center",
            ppr_extra=spacing_xml(line=LINE_KAI_HALF, line_rule="auto") + indent_xml(first_line=0),
            keep_next=True,
        )
    ]


def build_cover_elements(
    thesis_title: str,
    cover_info: dict[str, str],
    *,
    cover_assets_dir: Path | None = None,
    media_manager: MediaManager | None = None,
) -> list[str]:
    """Render the academic-master cover page (规范 5.1 + 附件 2.1)."""

    elements: list[str] = [_cover_top_line(cover_info), _cover_udc_line(cover_info)]
    # 附件2.1：UDC 与校徽之间是一个「固定值 20 磅」的空行。
    elements.append(_blank_line(line=LINE_FIXED_20PT, size=SIZE_XIAO_SI))
    elements.extend(_cover_logo(cover_assets_dir, media_manager))
    elements.append(_cover_degree_label(cover_info))
    # 附件2.1：「硕 士 学 位 论 文」与题名之间是**两个**空行。
    elements.append(_blank_line(line=LINE_FIXED_20PT))
    elements.append(_blank_line(line=LINE_FIXED_20PT))
    elements.extend(_cover_title_block(thesis_title))
    elements.append(_cover_hint(COVER_TITLE_HINT, line=COVER_TITLE_HINT_LINE))
    elements.append(_blank_line(line=LINE_FIXED_20PT, size=SIZE_XIAO_SI))
    elements.append(_cover_author(cover_info))
    elements.append(_cover_rule(COVER_RULE_AUTHOR_WIDTH))
    elements.append(_cover_hint(COVER_AUTHOR_HINT, line=COVER_AUTHOR_HINT_LINE))
    # 附件2.1：作者姓名提示行之下是一个 30 磅行距的空行。
    elements.append(_blank_line(line=COVER_AUTHOR_BLANK_LINE, size=SIZE_XIAO_SI))
    for spec in NJUST_COVER_FIELD_ORDER:
        row = _cover_field_row(spec, cover_info)
        if row:
            elements.append(row)
    elements.append(_blank_line(line=LINE_KAI_28PT))
    elements.append(
        paragraph_xml(
            runs=[run_text_xml(COVER_NOTE, font_ascii=FONT_EN, font_hansi=FONT_EN,
                               font_eastasia=FONT_CN, size=SIZE_WU)],
            ppr_extra=indent_xml(first_line=COVER_TOP_FIRST_LINE),
        )
    )
    return elements


# ---------------------------------------------------------------------------
# Declaration + authorisation (同页上下两部分)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DeclarationSignatureSpec:
    label: str = SIGNATURE_LABEL
    date_text: str = SIGNATURE_DATE
    #: 声明页（上半页）签名线的下划线空格数；授权声明页用 13，见 constants。
    underline_width: int = DECLARATION_SIGNATURE_UNDERLINE
    #: 下划线之后、日期之前的普通空格数（范例为 13）。
    date_gap: int = SIGNATURE_DATE_GAP


DECLARATION_SIGNATURE = DeclarationSignatureSpec()


def parse_declaration_values(text: str) -> tuple[str, str]:
    """Read the optional 研究生签名 / 签字日期 values out of the Markdown."""

    signature = ""
    date_value = ""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith(SIGNATURE_LABEL):
            signature = line.split("：", 1)[1].strip() if "：" in line else ""
        elif line.startswith("签字日期"):
            date_value = line.split("：", 1)[1].strip() if "：" in line else ""
    return signature, date_value


def _signature_line(
    signature: str,
    date_value: str,
    *,
    first_line: int,
    underline_width: int = DECLARATION_SIGNATURE_UNDERLINE,
    date_gap: int = SIGNATURE_DATE_GAP,
) -> str:
    kwargs = {"font_ascii": FONT_EN, "font_hansi": FONT_EN, "font_eastasia": FONT_CN,
              "size": SIZE_SI}
    runs = [run_text_xml(SIGNATURE_LABEL, **kwargs)]
    if signature:
        runs.append(run_text_xml(signature, underline=True, **kwargs))
    else:
        runs.append(_underlined_spaces(underline_width, **kwargs))
    # 范例：下划线之后是一段**普通**空格（不带下划线），然后才是「年  月  日」。
    runs.append(run_text_xml(" " * date_gap, **kwargs))
    if date_value:
        runs.append(run_text_xml(date_value, underline=True, **kwargs))
    else:
        runs.append(run_text_xml("年  月  日", **kwargs))
    # 声明页：单倍行距 **+ 吸附行网格**（范例该页每个段落都是 `<w:snapToGrid/>`）。
    # 14pt 正文在 16.3pt 的行网格上向上吸附到 2 格 = 32.6pt，这一页才会铺满。
    return paragraph_xml(
        runs=runs,
        ppr_extra="<w:snapToGrid/>"
        + spacing_xml(line=LINE_KAI_HALF, line_rule="auto")
        + indent_xml(first_line=first_line),
    )


def _declaration_heading(
    text: str,
    *,
    first_line: int,
    first_line_chars: int = 0,
    line: int = LINE_KAI_HALF,
    line_rule: str = "auto",
    snap_to_grid: bool = False,
) -> str:
    return paragraph_xml(
        runs=[run_text_xml(text, font_ascii=FONT_CN, font_hansi=FONT_CN, font_eastasia=FONT_CN,
                           size=SIZE_SAN, bold=True, bold_cs=True)],
        align="center",
        ppr_extra=("<w:snapToGrid/>" if snap_to_grid else "")
        + spacing_xml(line=line, line_rule=line_rule)
        + indent_xml(first_line_chars=first_line_chars, first_line=first_line),
    )


def _declaration_body_paragraph(text: str, *, math_converter=None, reference_anchors=None) -> str:
    return paragraph_with_inline_math_xml(
        text,
        style=STYLE_BODY,
        ppr_extra="<w:snapToGrid/>"
        + spacing_xml(line=LINE_KAI_HALF, line_rule="auto")
        + indent_xml(first_line=DECLARATION_FIRST_LINE),
        run_kwargs={
            "font_ascii": FONT_EN,
            "font_hansi": FONT_EN,
            "font_eastasia": FONT_CN,
            "size": SIZE_SI,
        },
        math_converter=math_converter,
        reference_anchors=reference_anchors,
    )


def build_declaration_elements(
    declaration_text: str,
    *,
    math_converter: MathConverter | None = None,
    reference_anchors: dict[str, str] | None = None,
) -> list[str]:
    """声明 + 学位论文使用授权声明，同页上、下两部分（规范 5.2）。

    The wording comes from 附件 2.5 and is inserted by the profile so it can
    never be edited by accident; the Markdown only supplies the signatures.
    """

    signature, date_value = parse_declaration_values(declaration_text)
    elements: list[str] = [
        _declaration_heading(
            DECLARATION_TITLE,
            first_line=DECLARATION_TITLE_FIRST_LINE,
            first_line_chars=DECLARATION_TITLE_FIRST_LINE_CHARS,
            # 范例：「声  明」标题继承 Normal 的固定值 20 磅，不是单倍。
            line=DECLARATION_TITLE_LINE,
            line_rule="exact",
        ),
        _declaration_body_paragraph(
            DECLARATION_BODY,
            math_converter=math_converter,
            reference_anchors=reference_anchors,
        ),
        _blank_line(line=LINE_KAI_HALF, size=SIZE_SI, snap_to_grid=True),
        _signature_line(
            signature,
            date_value,
            first_line=DECLARATION_FIRST_LINE,
            underline_width=DECLARATION_SIGNATURE_UNDERLINE,
        ),
        _blank_line(line=LINE_KAI_HALF, size=SIZE_SI, snap_to_grid=True),
        _blank_line(line=LINE_KAI_HALF, size=SIZE_SI, snap_to_grid=True),
        _blank_line(line=LINE_KAI_HALF, size=SIZE_SI, snap_to_grid=True),
        # 范例：「学位论文使用授权声明」标题是单倍行距 + 吸附网格（32.6pt），
        # 而上面的「声  明」是不吸附的固定值 20 磅。
        _declaration_heading(AUTHORISATION_TITLE, first_line=0, snap_to_grid=True),
        # 这一条空行跟在 16pt 标题后面，范例给它的段落标记字号是 16pt（sz=32）。
        _blank_line(line=LINE_KAI_HALF, size=SIZE_SAN, snap_to_grid=True),
        _declaration_body_paragraph(
            AUTHORISATION_BODY,
            math_converter=math_converter,
            reference_anchors=reference_anchors,
        ),
        _blank_line(line=LINE_KAI_HALF, size=SIZE_SI, snap_to_grid=True),
        _blank_line(line=LINE_KAI_HALF, size=SIZE_SI, snap_to_grid=True),
        _signature_line(
            signature,
            date_value,
            first_line=0,
            underline_width=AUTHORISATION_SIGNATURE_UNDERLINE,
        ),
        _blank_line(line=LINE_KAI_HALF, size=SIZE_SI, snap_to_grid=True),
    ]
    return elements


# ---------------------------------------------------------------------------
# Front-matter headings, abstract bodies and keywords
# ---------------------------------------------------------------------------


def build_front_heading(
    title: str,
    *,
    english: bool = False,
    toc: bool = False,
    page_break_before: bool = False,
    before_twips: int | None = None,
    after_twips: int | None = None,
) -> str:
    """摘要 / Abstract / 目录 / 致谢 / 参考文献 / 附录 标题（规范 4.4）。

    目录标题的段前段后按批注为 18mm/18mm；段后收到 15mm 以免目录页排满时挤出
    一张只有页眉页码的空页，原因见 `constants.AFTER_TOC_TITLE`。
    """

    font = FONT_EN if english else FONT_CN
    before = BEFORE_TOC_TITLE if toc else BEFORE_H1
    after = AFTER_TOC_TITLE if toc else before
    if before_twips is not None:
        before = before_twips
    if after_twips is not None:
        after = after_twips
    ppr = (
        spacing_xml(before=before, after=after, line=LINE_FIXED_20PT, line_rule="exact")
        + indent_xml(left=0, first_line_chars=0, first_line=0)
    )
    if page_break_before:
        ppr = "<w:pageBreakBefore/>" + ppr
    return paragraph_xml(
        runs=[run_text_xml(title, font_ascii=font, font_hansi=font, font_eastasia=font,
                           size=SIZE_SAN, bold=True, bold_cs=True)],
        style=STYLE_FRONT_HEADING,
        align="center",
        ppr_extra=ppr,
    )


def build_abstract_body_paragraph(
    text: str,
    *,
    english: bool = False,
    math_converter: MathConverter | None = None,
    reference_anchors: dict[str, str] | None = None,
) -> str:
    """规范 6.1：小四号，行距固定值 20 磅，两端对齐。"""

    return paragraph_with_inline_math_xml(
        text,
        style=STYLE_BODY,
        ppr_extra=spacing_xml(after=0, line=LINE_FIXED_20PT, line_rule="exact"),
        first_line_chars=200 if not english else 0,
        first_line=480 if not english else 0,
        run_kwargs={
            "font_ascii": FONT_EN,
            "font_hansi": FONT_EN,
            "font_eastasia": FONT_EN if english else FONT_CN,
            "size": SIZE_XIAO_SI,
        },
        math_converter=math_converter,
        reference_anchors=reference_anchors,
    )


def build_keyword_paragraph(keywords: str, *, english: bool = False) -> str | None:
    """关键词行（规范 6.1）。

    标签四号加粗、词项小四号；分隔符统一为逗号；左右缩进与首行缩进均为 0。
    """

    keywords = (keywords or "").strip()
    if not keywords:
        return None
    if english:
        normalized = _normalize_keyword_separators(keywords, EN_KEYWORD_SEPARATOR)
    else:
        normalized = _normalize_keyword_separators(keywords, CN_KEYWORD_SEPARATOR)

    label_kwargs = {
        "font_ascii": FONT_EN,
        "font_hansi": FONT_EN,
        "font_eastasia": FONT_EN if english else FONT_CN,
        "size": SIZE_SI,
        "bold": True,
    }
    value_kwargs = {
        "font_ascii": FONT_EN,
        "font_hansi": FONT_EN,
        "font_eastasia": FONT_EN if english else FONT_CN,
        "size": SIZE_XIAO_SI,
    }
    label = EN_KEYWORD_PREFIX.strip() if english else CN_KEYWORD_PREFIX.strip()
    body = normalized
    if body.startswith(label):
        body = body[len(label):].lstrip("：: ").strip()
    runs = [
        run_text_xml(label, **label_kwargs),
        run_text_xml((" " if english else "") + body, **value_kwargs),
    ]
    return paragraph_xml(
        runs=runs,
        ppr_extra=spacing_xml(before=0, line=LINE_FIXED_20PT, line_rule="exact")
        + indent_xml(left=0, first_line_chars=0, first_line=0),
    )


def _normalize_keyword_separators(text: str, separator: str) -> str:
    normalized = text
    for old in ("；", ";", "，", ","):
        normalized = normalized.replace(old, separator)
    parts = [part.strip() for part in normalized.split(separator)]
    return separator.join(part for part in parts if part)


def build_blank_paragraph(*, line: int = LINE_FIXED_20PT) -> str:
    return paragraph_xml(
        runs=[],
        ppr_extra=spacing_xml(before=0, after=0, line=line, line_rule="exact")
        + indent_xml(left=0, first_line_chars=0, first_line=0),
    )


def build_toc_heading(title: str, *, before_twips: int | None = None) -> str:
    return build_front_heading(title, toc=True, before_twips=before_twips)


__all__ = [
    "COVER_TITLE_KEY",
    "CoverFieldSpec",
    "DECLARATION_SIGNATURE",
    "DeclarationSignatureSpec",
    "KEYWORD_BLANK_PARAGRAPHS",
    "NJUST_COVER_FIELD_ORDER",
    "build_abstract_body_paragraph",
    "build_blank_paragraph",
    "build_cover_elements",
    "build_declaration_elements",
    "build_front_heading",
    "build_keyword_paragraph",
    "build_toc_heading",
    "parse_cover_info",
    "parse_declaration_values",
    "parse_inline_image_value",
    "resolve_cover_assets_dir",
]
