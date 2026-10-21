from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SectionSpec:
    with_header: bool = False
    footer_kind: str | None = None
    section_type: str | None = None
    page_number_format: str | None = None
    page_number_start: int | None = None
    # Profiles that need distinct odd/even headers set these. `header_ref` and
    # `footer_ref` override the legacy `with_header` / `footer_kind` shortcuts.
    header_ref: str | None = None
    header_ref_even: str | None = None
    footer_ref: str | None = None
    footer_ref_even: str | None = None
    title_page: bool = False


@dataclass(frozen=True)
class PageGeometry:
    """Page size and margins, in twips.

    The defaults are a plain A4 page with 2.54 cm margins, used only when a
    profile does not supply its own geometry. `njust-master-thesis` always
    passes its own instance (A4, 30/24/25/25 mm, header and footer 20 mm) so
    the common layer never hard-codes one school's numbers.
    """

    width: int = 11906
    height: int = 16838
    top: int = 1440
    right: int = 1440
    bottom: int = 1440
    left: int = 1440
    header: int = 851
    footer: int = 992
    gutter: int = 0
    cols_space: int = 720
    doc_grid_line_pitch: int = 312
    #: `w:docGrid/@w:type`；只有 `lines` / `linesAndChars` 才会真正生成行网格，
    #: 段落的 `w:snapToGrid` 才有意义（默认的 `default` 等于没有网格）。
    doc_grid_type: str = "default"
    mirror_margins: bool = False

    @property
    def text_width(self) -> int:
        return self.width - self.left - self.right


# Millimetres -> twips (1 mm = 1440 / 25.4 twips).
MM_TO_TWIPS = 1440.0 / 25.4


def mm(value: float) -> int:
    """Convert millimetres to twips, rounded to the nearest twip."""

    return int(round(value * MM_TO_TWIPS))


def pt(value: float) -> int:
    """Convert points to half-points (the unit used by `w:sz`)."""

    return int(round(value * 2))


@dataclass(frozen=True)
class DocumentLayout:
    cover: SectionSpec
    front_matter: SectionSpec
    body_start: SectionSpec
    body_continue: SectionSpec


@dataclass(frozen=True)
class DocxPackageParts:
    content_types: str = "[Content_Types].xml"
    package_rels: str = "_rels/.rels"
    core_props: str = "docProps/core.xml"
    app_props: str = "docProps/app.xml"
    document: str = "word/document.xml"
    styles: str = "word/styles.xml"
    numbering: str = "word/numbering.xml"
    settings: str = "word/settings.xml"
    font_table: str = "word/fontTable.xml"
    header: str = "word/header1.xml"
    empty_header: str = "word/header2.xml"
    empty_footer: str = "word/footer1.xml"
    page_footer: str = "word/footer2.xml"
    # Only emitted by profiles that use distinct odd/even headers.
    header_even: str = "word/header3.xml"
    footer_even: str = "word/footer3.xml"
    document_rels: str = "word/_rels/document.xml.rels"


@dataclass(frozen=True)
class FrontMatterSpec:
    cover_info_key: str
    declaration_key: str | None = None
    declaration_title: str = ""
    taskbook_key: str | None = None
    cn_abstract_key: str | None = None
    cn_abstract_title: str = ""
    cn_keyword_prefix: str = ""
    en_abstract_key: str | None = None
    en_abstract_title: str = ""
    en_keyword_prefix: str = ""
    toc_title: str = ""
    default_title: str = "Untitled"


@dataclass(frozen=True)
class FrontMatterPageSpec:
    kind: str
    source_key: str | None = None
    title: str = ""
    keyword_prefix: str = ""
    english: bool = False
    page_break_before: bool = False
    page_break_after: bool = False


@dataclass(frozen=True)
class FrontMatterPlan:
    pages: tuple[FrontMatterPageSpec, ...]

    def by_kind(self, kind: str) -> tuple[FrontMatterPageSpec, ...]:
        return tuple(page for page in self.pages if page.kind == kind)


@dataclass(frozen=True)
class FrontMatterPlanIssue:
    message: str


def validate_front_matter_plan(
    spec: FrontMatterSpec,
    plan: FrontMatterPlan,
) -> tuple[FrontMatterPlanIssue, ...]:
    issues: list[FrontMatterPlanIssue] = []
    if not plan.pages:
        return (FrontMatterPlanIssue("front matter plan is empty"),)

    if plan.pages[0].kind != "cover":
        issues.append(FrontMatterPlanIssue("front matter plan should start with a cover page"))

    if not plan.by_kind("toc"):
        issues.append(FrontMatterPlanIssue("front matter plan is missing toc page"))

    expected_keys = [
        spec.cover_info_key,
        spec.declaration_key,
        spec.taskbook_key,
        spec.cn_abstract_key,
        spec.en_abstract_key,
    ]
    planned_keys = {page.source_key for page in plan.pages if page.source_key}
    for source_key in expected_keys:
        if source_key and source_key not in planned_keys:
            issues.append(FrontMatterPlanIssue(f"front matter plan is missing source key: {source_key}"))

    for page in plan.pages:
        if page.kind in {"cover", "declaration", "taskbook", "abstract"} and not page.source_key:
            issues.append(FrontMatterPlanIssue(f"front matter {page.kind} page is missing source key"))
        if page.kind == "abstract" and not page.title:
            issues.append(FrontMatterPlanIssue("front matter abstract page is missing title"))

    return tuple(issues)


@dataclass(frozen=True)
class StyleBundle:
    styles_xml: str
    numbering_xml: str
    settings_xml: str
    font_table_xml: str
    header_xml: str
    empty_header_xml: str
    empty_footer_xml: str
    page_footer_xml: str
    # Empty for profiles that share one header/footer on every page.
    header_even_xml: str = ""
    footer_even_xml: str = ""

    def even_header_footer_parts(self) -> tuple[tuple[str, str], ...]:
        """(attribute name, xml) for the optional even-page parts."""

        parts: list[tuple[str, str]] = []
        if self.header_even_xml:
            parts.append(("header_even_xml", self.header_even_xml))
        if self.footer_even_xml:
            parts.append(("footer_even_xml", self.footer_even_xml))
        return tuple(parts)
