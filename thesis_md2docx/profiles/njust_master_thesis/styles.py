"""Word style catalogue for the NJUST master's thesis profile.

Sources for every value:

* 规范 4.2 / 4.3 / 4.4 / 6.2 / 7 / 8 / 11.1 / 11.2 / 11.3 -- fonts, sizes,
  boldness, alignment and paragraph spacing;
* 附件批注 -- the per-item annotations in 《南理工硕士论文格式.doc》;
* `_anno.docx` -- the university's own typeset thesis, used only where the
  written specification leaves a value open (TOC indents and tab stops).

Styles deliberately keep a `Njust` prefix so the common layer never has to know
about this school; the semantic roles in `njust_style_roles()` are what the
body renderer actually consumes.
"""

from __future__ import annotations

from ...layout import StyleBundle
from ...ooxml.parts import settings_xml
from ...styles import DocumentDefaultsSpec, StyleCatalog, StyleRole, StyleRoleMap, StyleSpec
from ...styles.fonts import FontSpec, FontTableSpec, font_table_xml
from ...styles.numbering import (
    AbstractNumberingSpec,
    NumberingCatalog,
    NumberingInstanceSpec,
    NumberingLevelSpec,
    numbering_xml,
)
from ...styles.ooxml import styles_xml as render_styles_xml
from ...styles.properties import (
    bold,
    bold_complex,
    indent,
    italic,
    justification,
    kern,
    numbering,
    outline_level,
    paragraph_bottom_border,
    run_fonts,
    run_size,
    shading,
    snap_to_grid,
    spacing,
    style_props,
    tab,
    tabs,
    text_alignment,
    widow_control,
)
from .constants import (
    BEFORE_H1,
    BEFORE_H2,
    BEFORE_H3,
    BEFORE_H4,
    BODY_FIRST_LINE,
    BODY_FIRST_LINE_CHARS,
    FONT_CN,
    FONT_CN_HEI,
    FONT_CN_KAI,
    FONT_EN,
    LINE_FIXED_20PT,
    LINE_KAI_HALF,
    SIZE_SAN,
    SIZE_SI,
    SIZE_WU,
    SIZE_XIAO_SAN,
    SIZE_XIAO_SI,
    SIZE_XIAO_WU,
    TOC_FIRST_STOP,
    TOC_TAB_POS,
    TOC1_LEFT,
    TOC2_LEFT,
    TOC3_LEFT,
)

STYLE_BODY = "NjustBody"
STYLE_HEADING_1 = "NjustHeading1"
STYLE_HEADING_2 = "NjustHeading2"
STYLE_HEADING_3 = "NjustHeading3"
STYLE_HEADING_4 = "NjustHeading4"
STYLE_FRONT_HEADING = "NjustFrontHeading"
STYLE_TOC_FIELD = "NjustTocField"
STYLE_TOC_1 = "TOC1"
STYLE_TOC_2 = "TOC2"
STYLE_TOC_3 = "TOC3"
STYLE_CAPTION = "NjustCaption"
STYLE_REFERENCE = "NjustReference"
STYLE_QUOTE = "NjustQuote"
STYLE_CODE = "NjustCode"
STYLE_MATH = "NjustEquation"
STYLE_FIGURE_IMAGE = "NjustFigureImage"
STYLE_TABLE_TEXT = "NjustTableText"
STYLE_HEADER = "NjustHeader"
STYLE_FOOTER = "NjustFooter"

NUMBERING_ID = 1


def njust_numbering_catalog() -> NumberingCatalog:
    """Multi-level heading numbering -- 规范 4.3（1 / 1.1 / 1.1.1 / 1.1.1.1）。"""

    return NumberingCatalog(
        abstract_numbers=(
            AbstractNumberingSpec(
                abstract_num_id=0,
                levels=(
                    NumberingLevelSpec(level=0, text="%1", paragraph_style=STYLE_HEADING_1),
                    NumberingLevelSpec(level=1, text="%1.%2", paragraph_style=STYLE_HEADING_2),
                    NumberingLevelSpec(level=2, text="%1.%2.%3", paragraph_style=STYLE_HEADING_3),
                    NumberingLevelSpec(level=3, text="%1.%2.%3.%4", paragraph_style=STYLE_HEADING_4),
                ),
            ),
        ),
        instances=(NumberingInstanceSpec(num_id=NUMBERING_ID, abstract_num_id=0),),
    )


def njust_numbering_xml() -> str:
    return numbering_xml(njust_numbering_catalog())


def njust_font_table() -> FontTableSpec:
    return FontTableSpec(
        fonts=(
            FontSpec(FONT_EN),
            FontSpec(FONT_CN, alt_name="SimSun", charset="86", family="auto", pitch="variable"),
            FontSpec(FONT_CN_HEI, alt_name="SimHei", charset="86", family="modern", pitch="fixed"),
            FontSpec(FONT_CN_KAI, alt_name="KaiTi", charset="86", family="modern", pitch="fixed"),
            FontSpec("楷体_GB2312", alt_name="楷体", charset="86", family="modern", pitch="default"),
            FontSpec("华文中宋", alt_name="STZhongsong", charset="86", family="auto", pitch="variable"),
            FontSpec("Cambria Math"),
            FontSpec("Courier New"),
            FontSpec("等线", alt_name="DengXian"),
        ),
    )


def njust_font_table_xml() -> str:
    return font_table_xml(njust_font_table())


def njust_style_roles() -> StyleRoleMap:
    return StyleRoleMap(
        {
            StyleRole.BASE_NORMAL: "Normal",
            StyleRole.BODY_TITLE: STYLE_HEADING_1,
            StyleRole.BODY_NORMAL: STYLE_BODY,
            StyleRole.BODY_HEADING_LEVEL1: STYLE_HEADING_1,
            StyleRole.BODY_HEADING_LEVEL2: STYLE_HEADING_2,
            StyleRole.BODY_HEADING_LEVEL3: STYLE_HEADING_3,
            StyleRole.BODY_HEADING_LEVEL4: STYLE_HEADING_4,
            StyleRole.FRONT_HEADING: STYLE_FRONT_HEADING,
            StyleRole.TOC_FIELD: STYLE_TOC_FIELD,
            StyleRole.TOC_LEVEL1: STYLE_TOC_1,
            StyleRole.TOC_LEVEL2: STYLE_TOC_2,
            StyleRole.TOC_LEVEL3: STYLE_TOC_3,
            StyleRole.CAPTION_DEFAULT: STYLE_CAPTION,
            StyleRole.REFERENCE_ITEM: STYLE_REFERENCE,
            StyleRole.QUOTE_BLOCK: STYLE_QUOTE,
            StyleRole.CODE_BLOCK: STYLE_CODE,
            StyleRole.MATH_BLOCK: STYLE_MATH,
            StyleRole.BODY_IMAGE: STYLE_FIGURE_IMAGE,
            StyleRole.TABLE_CELL: STYLE_TABLE_TEXT,
            StyleRole.HEADER_DEFAULT: STYLE_HEADER,
            StyleRole.FOOTER_DEFAULT: STYLE_FOOTER,
        }
    )


def njust_style_catalog() -> StyleCatalog:
    cn_run = style_props(run_fonts(ascii=FONT_EN, hansi=FONT_EN, eastasia=FONT_CN))
    cn_run_complex = style_props(
        run_fonts(ascii=FONT_EN, hansi=FONT_EN, eastasia=FONT_CN, complex_script=FONT_EN)
    )

    return StyleCatalog(
        defaults=DocumentDefaultsSpec(
            run_props=style_props(
                run_fonts(ascii=FONT_EN, hansi=FONT_EN, eastasia=FONT_CN),
                kern(2),
                run_size(SIZE_WU),
            )
        ),
        styles=(
            # -- Normal ------------------------------------------------------
            # 规范 4.2：正文小四号宋体、固定值 20 磅、段前段后 0、两端对齐。
            StyleSpec(
                style_id="Normal",
                name="Normal",
                default=True,
                q_format=True,
                paragraph_props=style_props(
                    widow_control(False),
                    "<w:adjustRightInd/>",
                    snap_to_grid(False),
                    spacing(after=0, line=LINE_FIXED_20PT, line_rule="exact"),
                    indent(left=0, first_line_chars=0, first_line=0),
                    justification("both"),
                    text_alignment("center"),
                ),
                run_props=style_props(
                    run_fonts(ascii=FONT_EN, hansi=FONT_EN, eastasia=FONT_CN, complex_script=FONT_EN),
                    kern(2),
                    run_size(SIZE_XIAO_SI),
                ),
            ),
            # -- Body --------------------------------------------------------
            StyleSpec(
                style_id=STYLE_BODY,
                name="NJUST Body",
                based_on="Normal",
                q_format=True,
                paragraph_props=style_props(
                    widow_control(False),
                    justification("both"),
                    spacing(after=0, line=LINE_FIXED_20PT, line_rule="exact"),
                    indent(left=0, first_line_chars=BODY_FIRST_LINE_CHARS, first_line=BODY_FIRST_LINE),
                ),
                run_props=style_props(
                    run_fonts(ascii=FONT_EN, hansi=FONT_EN, eastasia=FONT_CN),
                    kern(2),
                    run_size(SIZE_XIAO_SI),
                ),
            ),
            # -- Headings 1-4 ------------------------------------------------
            # 规范 4.3：一级 小三号加粗宋体、居左、段前段后各 18 磅
            StyleSpec(
                style_id=STYLE_HEADING_1,
                name="NJUST Heading 1",
                based_on="Normal",
                next_style="Normal",
                q_format=True,
                paragraph_props=style_props(
                    "<w:keepNext/>",
                    "<w:keepLines/>",
                    numbering(num_id=NUMBERING_ID),
                    spacing(before=BEFORE_H1, after=BEFORE_H1, line=LINE_FIXED_20PT, line_rule="exact"),
                    indent(left=0, first_line_chars=0, first_line=0),
                    justification("left"),
                    outline_level(0),
                ),
                run_props=style_props(
                    run_fonts(ascii=FONT_EN, hansi=FONT_EN, eastasia=FONT_CN),
                    bold(),
                    bold_complex(),
                    kern(44),
                    run_size(SIZE_XIAO_SAN, complex_size=44),
                ),
            ),
            # 二级 四号加粗宋体、居左、段前段后各 12 磅
            StyleSpec(
                style_id=STYLE_HEADING_2,
                name="NJUST Heading 2",
                based_on=STYLE_HEADING_1,
                next_style="Normal",
                q_format=True,
                paragraph_props=style_props(
                    "<w:keepNext/>",
                    "<w:keepLines/>",
                    numbering(level=1),
                    spacing(before=BEFORE_H2, after=BEFORE_H2, line=LINE_FIXED_20PT, line_rule="exact"),
                    indent(left=0, first_line_chars=0, first_line=0),
                    justification("left"),
                    outline_level(1),
                ),
                run_props=style_props(bold(), bold_complex(), run_size(SIZE_SI)),
            ),
            # 三级 小四号加粗宋体、居左、段前段后各 6 磅
            StyleSpec(
                style_id=STYLE_HEADING_3,
                name="NJUST Heading 3",
                based_on=STYLE_HEADING_2,
                next_style="Normal",
                q_format=True,
                paragraph_props=style_props(
                    "<w:keepNext/>",
                    "<w:keepLines/>",
                    numbering(level=2),
                    spacing(before=BEFORE_H3, after=BEFORE_H3, line=LINE_FIXED_20PT, line_rule="exact"),
                    indent(left=0, first_line_chars=0, first_line=0),
                    justification("left"),
                    outline_level(2),
                ),
                run_props=style_props(bold(), bold_complex(), run_size(SIZE_XIAO_SI)),
            ),
            # 四级 规范 4.3 写「同正文用小四号宋体」，未要求加粗
            StyleSpec(
                style_id=STYLE_HEADING_4,
                name="NJUST Heading 4",
                based_on="Normal",
                next_style="Normal",
                q_format=True,
                paragraph_props=style_props(
                    "<w:keepNext/>",
                    "<w:keepLines/>",
                    numbering(level=3),
                    spacing(before=BEFORE_H4, after=BEFORE_H4, line=LINE_FIXED_20PT, line_rule="exact"),
                    indent(left=0, first_line_chars=0, first_line=0),
                    justification("left"),
                    outline_level(3),
                ),
                run_props=style_props(
                    run_fonts(ascii=FONT_EN, hansi=FONT_EN, eastasia=FONT_CN),
                    run_size(SIZE_XIAO_SI),
                ),
            ),
            # -- Front matter headings ---------------------------------------
            # 规范 4.4：摘要 / Abstract / 目录 / 致谢 / 参考文献 / 附录 均为
            # 「不编号的一级标题」，三号加粗、居中，大纲级别 1（因此进目录）。
            # 段前段后默认 18 磅；目录标题单独用 18mm，由渲染层覆写。
            StyleSpec(
                style_id=STYLE_FRONT_HEADING,
                name="NJUST Front Heading",
                based_on="Normal",
                next_style="Normal",
                q_format=True,
                paragraph_props=style_props(
                    "<w:keepNext/>",
                    "<w:keepLines/>",
                    spacing(before=BEFORE_H1, after=BEFORE_H1, line=LINE_FIXED_20PT, line_rule="exact"),
                    indent(left=0, first_line_chars=0, first_line=0),
                    justification("center"),
                    outline_level(0),
                ),
                run_props=style_props(
                    run_fonts(ascii=FONT_CN, hansi=FONT_CN, eastasia=FONT_CN),
                    bold(),
                    bold_complex(),
                    run_size(SIZE_SAN),
                ),
            ),
            # -- Table of contents -------------------------------------------
            StyleSpec(
                style_id=STYLE_TOC_FIELD,
                name="NJUST TOC Field",
                based_on="Normal",
                paragraph_props=style_props(
                    spacing(after=0, line=LINE_FIXED_20PT, line_rule="exact"),
                    indent(left=0, first_line_chars=0, first_line=0),
                ),
                run_props=style_props(run_size(SIZE_XIAO_SI)),
            ),
            # 规范 6.2：一级标题、致谢、参考文献、附录条目 四号加粗；
            # 其余（二、三级）小四号不加粗。缩进与制表位为范例反推。
            StyleSpec(
                style_id=STYLE_TOC_1,
                name="toc 1",
                based_on="Normal",
                paragraph_props=style_props(
                    tabs(tab("left", TOC_FIRST_STOP), tab("right", TOC_TAB_POS, leader="dot")),
                    spacing(after=0, line=LINE_FIXED_20PT, line_rule="exact"),
                    indent(left=TOC1_LEFT, first_line_chars=0, first_line=0),
                ),
                run_props=style_props(
                    run_fonts(ascii=FONT_EN, hansi=FONT_EN, eastasia=FONT_CN),
                    bold(),
                    run_size(SIZE_SI),
                ),
            ),
            StyleSpec(
                style_id=STYLE_TOC_2,
                name="toc 2",
                based_on="Normal",
                paragraph_props=style_props(
                    tabs(tab("right", TOC_TAB_POS, leader="dot")),
                    spacing(after=0, line=LINE_FIXED_20PT, line_rule="exact"),
                    indent(left=TOC2_LEFT, first_line_chars=0, first_line=0),
                ),
                run_props=style_props(
                    run_fonts(ascii=FONT_EN, hansi=FONT_EN, eastasia=FONT_CN),
                    run_size(SIZE_XIAO_SI),
                ),
            ),
            StyleSpec(
                style_id=STYLE_TOC_3,
                name="toc 3",
                based_on="Normal",
                paragraph_props=style_props(
                    tabs(tab("right", TOC_TAB_POS, leader="dot")),
                    spacing(after=0, line=LINE_FIXED_20PT, line_rule="exact"),
                    indent(left=TOC3_LEFT, first_line_chars=0, first_line=0),
                ),
                run_props=style_props(
                    run_fonts(ascii=FONT_EN, hansi=FONT_EN, eastasia=FONT_CN),
                    run_size(SIZE_XIAO_SI),
                ),
            ),
            # -- Figure / table caption --------------------------------------
            # 规范 7 / 8：图题在图下、表题在表上，五号宋体（西文 Times New Roman）。
            # 规范未写对齐与段距；范例为居中、段前后 0、固定值 20 磅。
            StyleSpec(
                style_id=STYLE_CAPTION,
                name="NJUST Caption",
                based_on="Normal",
                next_style="Normal",
                paragraph_props=style_props(
                    justification("center"),
                    spacing(before=0, after=0, line=LINE_FIXED_20PT, line_rule="exact"),
                    indent(left=0, first_line_chars=0, first_line=0),
                ),
                run_props=style_props(
                    run_fonts(ascii=FONT_EN, hansi=FONT_EN, eastasia=FONT_CN),
                    run_size(SIZE_WU),
                ),
            ),
            # -- References --------------------------------------------------
            # 规范 11.3：小四号宋体、固定值 20 磅；西文 Times New Roman。
            # 规范 13 把「悬挂缩进」列为未明确，因此默认不设悬挂缩进。
            StyleSpec(
                style_id=STYLE_REFERENCE,
                name="NJUST Reference",
                based_on="Normal",
                paragraph_props=style_props(
                    '<w:adjustRightInd w:val="0"/>',
                    snap_to_grid(False),
                    spacing(after=0, line=LINE_FIXED_20PT, line_rule="exact"),
                    indent(left=0, first_line_chars=0, first_line=0),
                ),
                run_props=style_props(
                    run_fonts(ascii=FONT_EN, hansi=FONT_EN, eastasia=FONT_CN),
                    run_size(SIZE_XIAO_SI),
                ),
            ),
            StyleSpec(
                style_id=STYLE_QUOTE,
                name="NJUST Quote",
                based_on=STYLE_BODY,
                paragraph_props=style_props(
                    indent(left=480, first_line_chars=0, first_line=0),
                    spacing(after=0, line=LINE_FIXED_20PT, line_rule="exact"),
                ),
                run_props=style_props(italic()),
            ),
            StyleSpec(
                style_id=STYLE_CODE,
                name="NJUST Code",
                based_on="Normal",
                paragraph_props=style_props(
                    spacing(after=0, line=LINE_KAI_HALF, line_rule="auto"),
                    shading("clear", "F5F5F5"),
                ),
                run_props=style_props(
                    run_fonts(ascii="Courier New", hansi="Courier New", eastasia="等线"),
                    run_size(20),
                ),
            ),
            # -- Display equation --------------------------------------------
            # 规范 9 未规定居中方式；范例使用「居中制表位 + 右对齐编号制表位」，
            # 与本项目生成公式段落的方式一致。
            StyleSpec(
                style_id=STYLE_MATH,
                name="NJUST Equation",
                based_on="Normal",
                paragraph_props=style_props(
                    tabs(tab("center", TOC_TAB_POS // 2), tab("right", TOC_TAB_POS)),
                    spacing(before=0, after=0, line=LINE_FIXED_20PT, line_rule="exact"),
                    indent(left=0, first_line_chars=0, first_line=0),
                ),
                run_props=style_props(run_size(SIZE_XIAO_SI)),
            ),
            StyleSpec(
                style_id=STYLE_FIGURE_IMAGE,
                name="NJUST Figure Image",
                based_on="Normal",
                paragraph_props=style_props(
                    justification("center"),
                    # 单倍行距：固定值会把整幅图压进一行，导致图片显示不全。
                    # 范例反推确认参考论文的图片段落为 line=240 lineRule=auto。
                    spacing(before=0, after=0, line=LINE_KAI_HALF, line_rule="auto"),
                    indent(left=0, first_line_chars=0, first_line=0),
                ),
                run_props=style_props(run_size(SIZE_WU)),
            ),
            # 规范 8：表题及表内文字五号宋体。行距未明确，采用单倍行距避免单元格裁切。
            StyleSpec(
                style_id=STYLE_TABLE_TEXT,
                name="NJUST Table Text",
                based_on="Normal",
                paragraph_props=style_props(
                    justification("center"),
                    spacing(before=0, after=0, line=LINE_KAI_HALF, line_rule="auto"),
                    indent(left=0, first_line_chars=0, first_line=0),
                ),
                run_props=style_props(
                    run_fonts(ascii=FONT_EN, hansi=FONT_EN, eastasia=FONT_CN),
                    run_size(SIZE_WU),
                ),
            ),
            # -- Header / footer ---------------------------------------------
            # 规范 11.1：小五号宋体、左对齐、首行与左右缩进均为 0，
            # 一个右对齐制表位落在正文右边界（160mm）。
            StyleSpec(
                style_id=STYLE_HEADER,
                name="NJUST Header",
                based_on="Normal",
                paragraph_props=style_props(
                    paragraph_bottom_border(),
                    tabs(tab("right", TOC_TAB_POS)),
                    snap_to_grid(False),
                    spacing(after=0, line=LINE_KAI_HALF, line_rule="auto"),
                    indent(left=0, first_line_chars=0, first_line=0, right=0),
                    justification("left"),
                ),
                run_props=style_props(
                    run_fonts(ascii=FONT_EN, hansi=FONT_EN, eastasia=FONT_CN),
                    run_size(SIZE_XIAO_WU),
                ),
            ),
            StyleSpec(
                style_id=STYLE_FOOTER,
                name="NJUST Footer",
                based_on="Normal",
                paragraph_props=style_props(
                    tabs(tab("left", 0), tab("right", TOC_TAB_POS)),
                    snap_to_grid(False),
                    spacing(after=0, line=LINE_KAI_HALF, line_rule="auto"),
                    indent(left=0, first_line_chars=0, first_line=0, right=0),
                    justification("left"),
                ),
                run_props=style_props(
                    run_fonts(ascii=FONT_EN, hansi=FONT_EN, eastasia=FONT_CN),
                    run_size(SIZE_XIAO_WU),
                ),
            ),
        ),
    )


def njust_styles_xml() -> str:
    return render_styles_xml(njust_style_catalog())


def njust_settings_xml() -> str:
    """规范 11.1 要求奇偶页页眉不同，规范 2.1 要求对称页边距。

    `update_fields=False`：文档里只有目录域与 PAGEREF 域，没有任何外部引用，
    但 Word 对「打开时更新所有域」一律弹出「该文件包含的域可能引用了其他文件」。
    目录域本身带 `w:dirty`，Word 打开时会自行刷新它，因此关掉全局开关即可
    在保持目录正确的同时消除该提示。
    """

    return settings_xml(even_and_odd_headers=True, mirror_margins=True, update_fields=False)


def njust_style_bundle() -> StyleBundle:
    from .header_footer import empty_footer_xml, empty_header_xml, even_footer_xml, even_header_xml, odd_footer_xml, odd_header_xml

    return StyleBundle(
        styles_xml=njust_styles_xml(),
        numbering_xml=njust_numbering_xml(),
        settings_xml=njust_settings_xml(),
        font_table_xml=njust_font_table_xml(),
        header_xml=odd_header_xml(),
        empty_header_xml=empty_header_xml(),
        empty_footer_xml=empty_footer_xml(),
        page_footer_xml=odd_footer_xml(),
        header_even_xml=even_header_xml(),
        footer_even_xml=even_footer_xml(),
    )
