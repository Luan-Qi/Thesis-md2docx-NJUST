from __future__ import annotations

from pathlib import Path

from thesis_md2docx.layout import DocxPackageParts, mm, validate_front_matter_plan
from thesis_md2docx.profiles.njust_master_thesis import NjustMasterThesisProfile
from thesis_md2docx.profiles.njust_master_thesis.styles import (
    njust_style_bundle,
    njust_style_catalog,
    njust_style_roles,
)
from thesis_md2docx.styles import (
    COMMON_THESIS_STYLE_ROLES,
    BodyRenderProfile,
    StyleRole,
    validate_body_render_profile,
    validate_style_catalog,
)


def test_njust_profile_exposes_front_matter_and_layout_specs() -> None:
    profile = NjustMasterThesisProfile()
    front = profile.front_matter_spec()
    plan = profile.front_matter_plan()
    layout = profile.document_layout()

    assert profile.name == "njust-master-thesis"
    assert front.cover_info_key == "封面信息"
    assert front.declaration_key == "声明"
    # 规范 3.1：南理工硕士论文没有任务书。
    assert front.taskbook_key is None
    assert front.cn_abstract_key == "摘要"
    assert front.en_abstract_key == "ABSTRACT"
    assert front.toc_title == "目  录"

    assert [page.kind for page in plan.pages] == [
        "cover",
        "declaration",
        "abstract",
        "abstract",
        "toc",
    ]
    assert plan.pages[1].page_break_after is True
    assert plan.pages[2].title == "摘  要"
    assert plan.pages[2].keyword_prefix == "关键词："
    assert plan.pages[3].title == "Abstract"
    assert plan.pages[3].english is True
    assert validate_front_matter_plan(front, plan) == ()

    # 规范 2.1：A4，上 30mm、下 24mm、左右 25mm，页眉页脚各 20mm。
    geometry = profile.section_from_spec(layout.cover)
    assert 'w:w="11906"' in geometry
    assert 'w:top="1701"' in geometry
    assert 'w:bottom="1361"' in geometry
    assert 'w:left="1418"' in geometry and 'w:right="1418"' in geometry
    assert 'w:header="1134"' in geometry and 'w:footer="1134"' in geometry
    # 正文可用宽度 160mm。
    assert layout.body_start.page_number_format == "decimal"
    assert layout.body_start.page_number_start == 1
    assert layout.front_matter.page_number_format == "upperRoman"
    assert layout.front_matter.page_number_start == 1


def test_njust_cover_and_declaration_sections_hide_header_and_footer() -> None:
    profile = NjustMasterThesisProfile()
    layout = profile.document_layout()

    cover = profile.section_from_spec(layout.cover)
    assert 'w:headerReference w:type="default" r:id="rId8"' in cover
    assert 'w:footerReference w:type="default" r:id="rId5"' in cover
    assert "w:pgNumType" not in cover

    front = profile.section_from_spec(layout.front_matter)
    assert 'w:headerReference w:type="even" r:id="rId9"' in front
    assert 'w:footerReference w:type="even" r:id="rId10"' in front
    assert 'w:pgNumType w:fmt="upperRoman" w:start="1"' in front


def test_njust_odd_even_header_and_footer_parts() -> None:
    bundle = NjustMasterThesisProfile().style_bundle()

    assert "硕士学位论文" in bundle.header_xml
    assert "STYLEREF" in bundle.header_even_xml
    assert bundle.empty_header_xml.count("<w:p>") == 1
    assert "PAGE" in bundle.page_footer_xml
    assert 'w:jc w:val="right"' in bundle.page_footer_xml
    assert "PAGE" in bundle.footer_even_xml
    assert 'w:jc w:val="left"' in bundle.footer_even_xml
    assert "<w:evenAndOddHeaders/>" in bundle.settings_xml
    assert "<w:mirrorMargins/>" in bundle.settings_xml


def test_njust_image_relationship_ids_avoid_the_header_footer_ids() -> None:
    profile = NjustMasterThesisProfile()
    assert profile.image_starting_rid() == 11
    parts = profile.package_parts()
    assert parts.header_even == "word/header3.xml"
    assert parts.footer_even == "word/footer3.xml"
    assert parts == DocxPackageParts(header_even="word/header3.xml", footer_even="word/footer3.xml")


def test_njust_style_roles_point_to_declared_word_styles() -> None:
    profile = NjustMasterThesisProfile()
    catalog = profile.style_catalog()
    roles = profile.style_roles()

    assert roles.require(StyleRole.BODY_NORMAL) == "NjustBody"
    assert roles.require(StyleRole.BODY_HEADING_LEVEL1) == "NjustHeading1"
    assert roles.require(StyleRole.BODY_HEADING_LEVEL4) == "NjustHeading4"
    assert roles.require(StyleRole.REFERENCE_ITEM) == "NjustReference"
    assert roles.require(StyleRole.TOC_LEVEL1) == "TOC1"
    assert roles.missing_roles(profile.required_style_roles()) == ()
    assert roles.missing_styles(catalog) == ()
    assert njust_style_catalog() == catalog
    assert njust_style_roles() == roles
    assert validate_style_catalog(catalog, roles) == ()
    assert profile.required_style_roles() == COMMON_THESIS_STYLE_ROLES
    assert "NjustFrontHeading" in [style.style_id for style in catalog.styles]
    assert njust_style_bundle().styles_xml == profile.style_bundle().styles_xml


def test_njust_body_render_profile_is_typed_and_validated() -> None:
    profile = NjustMasterThesisProfile()
    body_profile = profile.body_style_profile()

    assert isinstance(body_profile, BodyRenderProfile)
    assert body_profile.styles.normal == "NjustBody"
    assert body_profile.styles.heading1 == "NjustHeading1"
    assert body_profile.styles.table_cell == "NjustTableText"
    assert body_profile.styles.front_heading == "NjustFrontHeading"
    assert body_profile.normal_paragraph.first_line_chars == 200
    assert body_profile.normal_run is not None
    assert body_profile.normal_run.to_kwargs()["font_eastasia"] == "宋体"
    assert body_profile.missing_hooks() == ()
    assert validate_body_render_profile(body_profile, profile.style_catalog()) == ()


def test_njust_normal_style_uses_fixed_20pt_line_spacing() -> None:
    """规范 4.2：正文行距固定值 20 磅（400 twips），段前段后 0。"""

    catalog = NjustMasterThesisProfile().style_catalog()
    by_id = {style.style_id: style for style in catalog.styles}
    normal = by_id["Normal"]
    joined = "".join(normal.paragraph_props)

    assert 'w:line="400"' in joined
    assert 'w:lineRule="exact"' in joined
    assert 'w:before="0"' in joined or "w:before=" not in joined
    assert 'w:sz w:val="24"' in "".join(normal.run_props)


def test_njust_heading_sizes_follow_the_specification() -> None:
    """规范 4.3：一级 小三(15pt)、二级 四号(14pt)、三级 小四(12pt)。"""

    catalog = NjustMasterThesisProfile().style_catalog()
    by_id = {style.style_id: style for style in catalog.styles}

    assert 'w:sz w:val="30"' in "".join(by_id["NjustHeading1"].run_props)
    assert 'w:sz w:val="28"' in "".join(by_id["NjustHeading2"].run_props)
    assert 'w:sz w:val="24"' in "".join(by_id["NjustHeading3"].run_props)
    # 段前段后：18pt / 12pt / 6pt
    assert 'w:before="360"' in "".join(by_id["NjustHeading1"].paragraph_props)
    assert 'w:before="240"' in "".join(by_id["NjustHeading2"].paragraph_props)
    assert 'w:before="120"' in "".join(by_id["NjustHeading3"].paragraph_props)


def test_njust_toc_styles_match_the_specification() -> None:
    """规范 6.2：一级/致谢/参考文献/附录 四号加粗；其余小四不加粗。"""

    catalog = NjustMasterThesisProfile().style_catalog()
    by_id = {style.style_id: style for style in catalog.styles}

    toc1_run = "".join(by_id["TOC1"].run_props)
    assert "<w:b/>" in toc1_run and 'w:sz w:val="28"' in toc1_run
    toc2_run = "".join(by_id["TOC2"].run_props)
    assert "<w:b/>" not in toc2_run and 'w:sz w:val="24"' in toc2_run
    toc3_run = "".join(by_id["TOC3"].run_props)
    assert "<w:b/>" not in toc3_run and 'w:sz w:val="24"' in toc3_run


def test_njust_page_geometry_helpers() -> None:
    assert mm(30) == 1701
    assert mm(24) == 1361
    assert mm(20) == 1134
    assert mm(18) == 1020


def test_njust_cover_assets_resolve_next_to_the_markdown(tmp_path: Path) -> None:
    profile = NjustMasterThesisProfile()
    assets = tmp_path / "img" / "cover-assets"
    assets.mkdir(parents=True)
    (assets / "njust-logo.png").write_bytes(b"png")
    markdown = tmp_path / "thesis.md"
    markdown.write_text("# t\n", encoding="utf-8")

    assert profile.resolve_cover_assets_dir(markdown, None, use_cover_assets=True) == assets
    assert profile.resolve_cover_assets_dir(markdown, None, use_cover_assets=False) is None


def test_njust_default_cover_assets_are_shipped() -> None:
    profile = NjustMasterThesisProfile()
    directory = profile.default_cover_assets_dir
    assert directory is not None and directory.is_dir()
    for name in profile.cover_asset_names():
        assert (directory / name).is_file(), name
