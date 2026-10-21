from __future__ import annotations

import datetime as dt
from xml.sax.saxutils import escape

from ..constants import *
from ..layout import PageGeometry
from ..media import MediaManager


def native_sect_pr_xml(
    *,
    with_header: bool = False,
    footer_kind: str | None = None,
    section_type: str | None = None,
    page_number_format: str | None = None,
    page_number_start: int | None = None,
    header_ref: str | None = None,
    header_ref_even: str | None = None,
    footer_ref: str | None = None,
    footer_ref_even: str | None = None,
    title_page: bool = False,
    geometry: PageGeometry | None = None,
) -> str:
    """Build a section's `w:sectPr`.

    `with_header` / `footer_kind` are the short forms for the common case of a
    single header and a single footer. Profiles with distinct odd/even headers
    pass explicit relationship ids through `header_ref` / `header_ref_even` /
    `footer_ref` / `footer_ref_even` instead. Page size and margins come from
    `geometry`, so no school's numbers are baked into the common layer.
    """

    geom = geometry or PageGeometry()
    # Children are emitted in the order CT_SectPr declares them:
    # headerReference*, footerReference*, type, pgSz, pgMar, pgNumType, cols,
    # titlePg, docGrid. Word tolerates other orders, but the declared one keeps
    # pagination behaviour predictable.
    parts = ["<w:sectPr>"]
    default_header = header_ref if header_ref is not None else (REL_ID_HEADER if with_header else None)
    if default_header:
        parts.append(f'<w:headerReference w:type="default" r:id="{default_header}"/>')
    if header_ref_even:
        parts.append(f'<w:headerReference w:type="even" r:id="{header_ref_even}"/>')
    if footer_ref is None:
        if footer_kind == "empty":
            footer_ref = REL_ID_EMPTY_FOOTER
        elif footer_kind == "page":
            footer_ref = REL_ID_PAGE_FOOTER
    if footer_ref:
        parts.append(f'<w:footerReference w:type="default" r:id="{footer_ref}"/>')
    if footer_ref_even:
        parts.append(f'<w:footerReference w:type="even" r:id="{footer_ref_even}"/>')
    if section_type:
        parts.append(f'<w:type w:val="{section_type}"/>')
    if page_number_format or page_number_start is not None:
        attrs: list[str] = []
        if page_number_format:
            attrs.append(f'w:fmt="{page_number_format}"')
        if page_number_start is not None:
            attrs.append(f'w:start="{page_number_start}"')
        page_number_xml = f"<w:pgNumType {' '.join(attrs)}/>"
    else:
        page_number_xml = ""
    parts.append(f'<w:pgSz w:w="{geom.width}" w:h="{geom.height}"/>')
    parts.append(
        f'<w:pgMar w:top="{geom.top}" w:right="{geom.right}" w:bottom="{geom.bottom}" '
        f'w:left="{geom.left}" w:header="{geom.header}" w:footer="{geom.footer}" w:gutter="{geom.gutter}"/>'
    )
    parts.append(page_number_xml)
    parts.append(f'<w:cols w:space="{geom.cols_space}"/>')
    if title_page:
        parts.append("<w:titlePg/>")
    parts.append(f'<w:docGrid w:type="{geom.doc_grid_type}" w:linePitch="{geom.doc_grid_line_pitch}"/>')
    parts.append("</w:sectPr>")
    return "".join(parts)


def default_sect_pr_xml() -> str:
    return native_sect_pr_xml(with_header=True, footer_kind="page", page_number_format="decimal", page_number_start=1)


def document_xml(elements: list[str], sect_pr: str | None = None) -> str:
    sect_pr = sect_pr or default_sect_pr_xml()
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W_NS}" xmlns:r="{R_NS}" xmlns:m="{M_NS}" xmlns:wp="{WP_NS}" '
        'xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" '
        f'xmlns:a="{A_NS}" xmlns:pic="{PIC_NS}" '
        'xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" '
        'xmlns:a14="http://schemas.microsoft.com/office/drawing/2010/main">'
        f"<w:body>{''.join(elements)}{sect_pr}</w:body>"
        "</w:document>"
    )


def content_types_xml(
    image_extensions: set[str] | None = None,
    *,
    extra_headers: tuple[str, ...] = (),
    extra_footers: tuple[str, ...] = (),
) -> str:
    defaults = [
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
    ]
    for ext in sorted(image_extensions or set()):
        content_type = IMAGE_CONTENT_TYPES.get(ext)
        if content_type:
            defaults.append(f'<Default Extension="{ext}" ContentType="{content_type}"/>')
    header_parts = ["word/header1.xml", "word/header2.xml", *extra_headers]
    footer_parts = ["word/footer1.xml", "word/footer2.xml", *extra_footers]
    overrides = [
        "".join(
            f'<Override PartName="/{part}" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>'
            for part in header_parts
        ),
        "".join(
            f'<Override PartName="/{part}" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
            for part in footer_parts
        ),
    ]
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        f'{"".join(defaults)}'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
        '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
        '<Override PartName="/word/fontTable.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml"/>'
        f'{overrides[0]}{overrides[1]}'
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
        "</Types>"
    )


def rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
        "</Relationships>"
    )


def document_rels_xml(
    media_manager: MediaManager | None = None,
    *,
    even_header_part: str | None = None,
    even_footer_part: str | None = None,
) -> str:
    relationships = [
        f'<Relationship Id="{REL_ID_STYLES}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>',
        f'<Relationship Id="{REL_ID_NUMBERING}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>',
        f'<Relationship Id="{REL_ID_SETTINGS}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>',
        f'<Relationship Id="{REL_ID_FONT_TABLE}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable" Target="fontTable.xml"/>',
        f'<Relationship Id="{REL_ID_HEADER}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>',
        f'<Relationship Id="{REL_ID_EMPTY_FOOTER}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>',
        f'<Relationship Id="{REL_ID_PAGE_FOOTER}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer2.xml"/>',
        f'<Relationship Id="{REL_ID_EMPTY_HEADER}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header2.xml"/>',
    ]
    if even_header_part:
        relationships.append(
            f'<Relationship Id="{REL_ID_HEADER_EVEN}" '
            f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" '
            f'Target="{even_header_part.split("/")[-1]}"/>'
        )
    if even_footer_part:
        relationships.append(
            f'<Relationship Id="{REL_ID_FOOTER_EVEN}" '
            f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" '
            f'Target="{even_footer_part.split("/")[-1]}"/>'
        )
    if media_manager:
        for item in media_manager.images:
            relationships.append(
                f'<Relationship Id="{item.rel_id}" Type="{IMAGE_REL_TYPE}" Target="{item.part_name}"/>'
            )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f'{"".join(relationships)}'
        "</Relationships>"
    )


def settings_xml(
    *,
    even_and_odd_headers: bool = False,
    mirror_margins: bool = False,
    update_fields: bool = True,
) -> str:
    """Build `word/settings.xml`.

    `update_fields` writes `<w:updateFields w:val="true"/>`, which makes Word
    offer to update every field as soon as the document is opened. Word phrases
    that offer as「该文件包含的域可能引用了其他文件」and shows it even for a
    document whose only fields are TOC and PAGEREF, so profiles that mark their
    TOC field `w:dirty` (which Word refreshes on its own) turn this off.
    """

    toggles = ""
    if even_and_odd_headers:
        toggles += "<w:evenAndOddHeaders/>"
    if mirror_margins:
        toggles += "<w:mirrorMargins/>"
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:settings xmlns:w="{W_NS}">'
        f'{"<w:updateFields w:val=\"true\"/>" if update_fields else ""}'
        '<w:zoom w:percent="100"/>'
        "<w:bordersDoNotSurroundHeader/>"
        "<w:bordersDoNotSurroundFooter/>"
        f"{toggles}"
        '<w:defaultTabStop w:val="420"/>'
        '<w:drawingGridHorizontalSpacing w:val="105"/>'
        '<w:drawingGridVerticalSpacing w:val="156"/>'
        '<w:displayHorizontalDrawingGridEvery w:val="0"/>'
        '<w:displayVerticalDrawingGridEvery w:val="2"/>'
        '<w:characterSpacingControl w:val="compressPunctuation"/>'
        '<w:themeFontLang w:val="en-US" w:eastAsia="zh-CN"/>'
        "<w:compat>"
        "<w:spaceForUL/>"
        "<w:balanceSingleByteDoubleByteWidth/>"
        "<w:doNotLeaveBackslashAlone/>"
        "<w:ulTrailSpace/>"
        "<w:doNotExpandShiftReturn/>"
        "<w:adjustLineHeightInTable/>"
        "<w:useFELayout/>"
        '<w:compatSetting w:name="compatibilityMode" '
        'w:uri="http://schemas.microsoft.com/office/word" w:val="15"/>'
        '<w:compatSetting w:name="overrideTableStyleFontSizeAndJustification" '
        'w:uri="http://schemas.microsoft.com/office/word" w:val="1"/>'
        '<w:compatSetting w:name="enableOpenTypeFeatures" '
        'w:uri="http://schemas.microsoft.com/office/word" w:val="1"/>'
        '<w:compatSetting w:name="doNotFlipMirrorIndents" '
        'w:uri="http://schemas.microsoft.com/office/word" w:val="1"/>'
        '<w:compatSetting w:name="differentiateMultirowTableHeaders" '
        'w:uri="http://schemas.microsoft.com/office/word" w:val="1"/>'
        "</w:compat>"
        "</w:settings>"
    )


def core_xml(title: str) -> str:
    created = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<cp:coreProperties xmlns:cp="{CP_NS}" xmlns:dc="{DC_NS}" xmlns:dcterms="{DCTERMS_NS}" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="{XSI_NS}">'
        f"<dc:title>{escape(title)}</dc:title>"
        "<dc:creator>Codex</dc:creator>"
        "<cp:lastModifiedBy>Codex</cp:lastModifiedBy>"
        f'<dcterms:created xsi:type="dcterms:W3CDTF">{created}</dcterms:created>'
        f'<dcterms:modified xsi:type="dcterms:W3CDTF">{created}</dcterms:modified>'
        "</cp:coreProperties>"
    )


def app_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="{VT_NS}">'
        "<Application>Codex</Application>"
        "</Properties>"
    )
