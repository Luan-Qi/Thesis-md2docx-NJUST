from __future__ import annotations

from pathlib import Path

from thesis_md2docx.media import MediaImage, MediaManager
from thesis_md2docx.ooxml.paragraphs import paragraph_with_inline_math_xml
from thesis_md2docx.styles.properties import (
    bold_complex,
    indent,
    justification,
    run_fonts,
    run_size,
    spacing,
    style_props,
    tab,
    tabs,
    widow_control,
)
from thesis_md2docx.ooxml.text import text_runs
from thesis_md2docx.profiles.njust_master_thesis.body import figure_image_paragraph_xml
from thesis_md2docx.profiles.njust_master_thesis.styles import (
    njust_font_table,
    njust_font_table_xml,
    njust_numbering_catalog,
    njust_numbering_xml,
    njust_styles_xml,
)


def test_style_property_helpers_render_ooxml_fragments() -> None:
    assert style_props(
        run_fonts(ascii="Times New Roman", hansi="Times New Roman", eastasia="宋体"),
        run_size(24),
    ) == (
        '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/>',
        '<w:sz w:val="24"/><w:szCs w:val="24"/>',
    )

    assert style_props(
        widow_control(False),
        justification("both"),
        spacing(after=0, line=360),
        indent(first_line_chars=200, first_line=480),
    ) == (
        '<w:widowControl w:val="0"/>',
        '<w:jc w:val="both"/>',
        '<w:spacing w:after="0" w:line="360" w:lineRule="auto"/>',
        '<w:ind w:firstLineChars="200" w:firstLine="480"/>',
    )


def test_style_property_helpers_preserve_word_specific_details() -> None:
    assert style_props(
        bold_complex(False),
        '<w:sz w:val="30"/>',
        tabs(tab("right", 8313, leader="dot")),
    ) == (
        '<w:bCs w:val="0"/>',
        '<w:sz w:val="30"/>',
        '<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="8313"/></w:tabs>',
    )


def test_text_runs_support_word_symbol_tokens() -> None:
    runs = text_runs(
        "0{{sym:Times New Roman:0000}}截面 *V{{sub:max}}*/m{{sup:-3}}",
        run_kwargs={"bold_cs": False},
    )

    assert runs == [
        "<w:r><w:t>0</w:t></w:r>",
        '<w:r><w:sym w:font="Times New Roman" w:char="0000"/></w:r>',
        '<w:r><w:t xml:space="preserve">截面 </w:t></w:r>',
        '<w:r><w:rPr><w:i/><w:iCs/></w:rPr><w:t>V</w:t></w:r>',
        '<w:r><w:rPr><w:i/><w:iCs/><w:vertAlign w:val="subscript"/></w:rPr><w:t>max</w:t></w:r>',
        "<w:r><w:t>/m</w:t></w:r>",
        '<w:r><w:rPr><w:vertAlign w:val="superscript"/></w:rPr><w:t>-3</w:t></w:r>',
    ]


def test_inline_bold_markup_can_span_inline_math() -> None:
    xml = paragraph_with_inline_math_xml(
        "**$q/p/c$ 分量分布。** 图4.5 给出 $q/p/c$ 三个分量。",
        run_kwargs={"size": 24},
    )

    assert "**" not in xml
    assert "$q/p/c$" in xml
    bold_rpr = '<w:rPr><w:b/><w:bCs/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr>'
    assert f"{bold_rpr}<w:t>$q/p/c$</w:t>" in xml
    assert f'{bold_rpr}<w:t xml:space="preserve"> 分量分布。</w:t>' in xml


def test_njust_numbering_and_font_table_are_structured_specs() -> None:
    """规范 4.3：标题编号为 1 / 1.1 / 1.1.1 / 1.1.1.1。"""

    numbering = njust_numbering_catalog()
    font_table = njust_font_table()

    levels = numbering.abstract_numbers[0].levels
    assert [level.text for level in levels] == ["%1", "%1.%2", "%1.%2.%3", "%1.%2.%3.%4"]
    assert numbering.instances[0].num_id == 1
    assert font_table.fonts[1].name == "宋体"
    assert font_table.fonts[1].alt_name == "SimSun"
    assert '<w:lvlText w:val="%1.%2.%3"/>' in njust_numbering_xml()
    assert '<w:font w:name="等线"><w:altName w:val="DengXian"/></w:font>' in njust_font_table_xml()


def test_njust_styles_carry_the_declared_style_ids() -> None:
    styles = njust_styles_xml()

    for style_id in (
        "Normal",
        "NjustBody",
        "NjustHeading1",
        "NjustHeading4",
        "NjustFrontHeading",
        "NjustCaption",
        "NjustReference",
        "NjustEquation",
        "NjustFigureImage",
        "NjustTableText",
        "NjustHeader",
        "NjustFooter",
        "TOC1",
        "TOC2",
        "TOC3",
    ):
        assert f'w:styleId="{style_id}"' in styles, style_id
    assert '<w:name w:val="NJUST Body"/>' in styles


def test_njust_figure_image_paragraph_options_are_explicit() -> None:
    item = MediaImage(
        source_path=Path("figure.jpeg"),
        filename="image1.jpeg",
        part_name="media/image1.jpeg",
        rel_id="rId11",
        content_type="image/jpeg",
        width_emu=100,
        height_emu=100,
    )
    xml = figure_image_paragraph_xml(
        item,
        MediaManager(),
        options={"p_style": "NjustCaption", "align": "none", "line": "400", "before": "0", "after": "0", "keep_next": "false"},
    )

    assert '<w:pStyle w:val="NjustCaption"/>' in xml
    assert '<w:jc ' not in xml
    assert "<w:keepNext/>" not in xml
    assert "w:line=" in xml
