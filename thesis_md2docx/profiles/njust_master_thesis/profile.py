"""The `njust-master-thesis` profile: Nanjing University of Science and
Technology academic master's thesis.

Specification: 《南理工硕士论文格式.doc》(正文条款 + 附件 2.1-2.13 文字说明与批注),
distilled into `format.md` at the repository root. Layout values the written
specification leaves open are taken from the university's own already-typeset
thesis; every such value is listed in the project README.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ...body_rules import BodyParseRules
from ...constants import (
    REL_ID_EMPTY_FOOTER,
    REL_ID_EMPTY_HEADER,
    REL_ID_FOOTER_EVEN,
    REL_ID_HEADER,
    REL_ID_HEADER_EVEN,
    REL_ID_PAGE_FOOTER,
)
from ...layout import DocumentLayout, FrontMatterSpec, SectionSpec, StyleBundle
from ...math.converter import MathConverter
from ...media import MediaManager
from ...ooxml.parts import native_sect_pr_xml
from ...styles import BodyRenderProfile, StyleCatalog, StyleRoleMap
from ..base import ThesisProfile
from .body import body_parse_rules, body_style_profile
from .constants import (
    CN_KEYWORD_PREFIX,
    EN_KEYWORD_PREFIX,
    PAGE_GEOMETRY,
)
from .document import build_document as build_profile_document
from .frontmatter import resolve_cover_assets_dir
from .styles import njust_style_bundle, njust_style_catalog, njust_style_roles

#: 封面校徽/校名图片随 profile 一起分发。
ASSETS_DIR = Path(__file__).resolve().parent / "assets"

#: 前置页页眉页脚引用（奇偶两套）。
_HEADER_REFS = {
    "header_ref": REL_ID_HEADER,
    "header_ref_even": REL_ID_HEADER_EVEN,
    "footer_ref": REL_ID_PAGE_FOOTER,
    "footer_ref_even": REL_ID_FOOTER_EVEN,
}
_HIDDEN_REFS = {
    "header_ref": REL_ID_EMPTY_HEADER,
    "footer_ref": REL_ID_EMPTY_FOOTER,
}


@dataclass(frozen=True)
class NjustMasterThesisProfile(ThesisProfile):
    name: str = "njust-master-thesis"
    display_name: str = "Nanjing University of Science and Technology master's thesis"
    default_cover_assets_dir: Path | None = ASSETS_DIR

    def resolve_cover_assets_dir(
        self,
        markdown_path: Path,
        assets_dir: Path | None,
        *,
        use_cover_assets: bool,
    ) -> Path | None:
        return resolve_cover_assets_dir(
            markdown_path,
            assets_dir or self.default_cover_assets_dir,
            use_cover_assets=use_cover_assets,
        )

    def body_style_profile(self) -> BodyRenderProfile:
        return body_style_profile()

    def body_parse_rules(self) -> BodyParseRules:
        return body_parse_rules()

    def document_layout(self) -> DocumentLayout:
        return DocumentLayout(
            # A 节：封面 + 声明，隐藏页眉与页码。
            cover=SectionSpec(section_type="nextPage", **_HIDDEN_REFS),
            # B 节：摘要/英文摘要/目录，罗马数字页码。
            front_matter=SectionSpec(
                section_type="nextPage",
                page_number_format="upperRoman",
                page_number_start=1,
                **_HEADER_REFS,
            ),
            # C 节：正文至附录，阿拉伯数字页码。
            body_start=SectionSpec(
                section_type="nextPage",
                page_number_format="decimal",
                page_number_start=1,
                **_HEADER_REFS,
            ),
            body_continue=SectionSpec(**_HEADER_REFS),
        )

    def front_matter_spec(self) -> FrontMatterSpec:
        return FrontMatterSpec(
            cover_info_key="封面信息",
            declaration_key="声明",
            # 声明页内有两个标题（声明 / 学位论文使用授权声明），由 profile 自行渲染。
            declaration_title="",
            taskbook_key=None,
            cn_abstract_key="摘要",
            cn_abstract_title="摘  要",
            cn_keyword_prefix=CN_KEYWORD_PREFIX,
            en_abstract_key="ABSTRACT",
            en_abstract_title="Abstract",
            en_keyword_prefix=EN_KEYWORD_PREFIX,
            toc_title="目  录",
            default_title="硕士学位论文",
        )

    def image_starting_rid(self) -> int:
        # rId9 / rId10 are the even-page header and footer relationships.
        return 11

    def cover_asset_names(self) -> tuple[str, ...]:
        from .constants import COVER_ASSET_NAME

        return (COVER_ASSET_NAME,)

    def section_from_spec(self, spec: SectionSpec) -> str:
        return native_sect_pr_xml(
            geometry=PAGE_GEOMETRY,
            with_header=spec.with_header,
            footer_kind=spec.footer_kind,
            section_type=spec.section_type,
            page_number_format=spec.page_number_format,
            page_number_start=spec.page_number_start,
            header_ref=spec.header_ref,
            header_ref_even=spec.header_ref_even,
            footer_ref=spec.footer_ref,
            footer_ref_even=spec.footer_ref_even,
            title_page=spec.title_page,
        )

    def style_catalog(self) -> StyleCatalog:
        return njust_style_catalog()

    def style_roles(self) -> StyleRoleMap:
        return njust_style_roles()

    def style_bundle(self) -> StyleBundle:
        return njust_style_bundle()

    def build_document(
        self,
        text: str,
        *,
        math_converter: MathConverter | None = None,
        reference_anchors: dict[str, str] | None = None,
        markdown_dir: Path | None = None,
        cover_assets_dir: Path | None = None,
        media_manager: MediaManager | None = None,
    ) -> tuple[list[str], str, str]:
        return build_profile_document(
            text,
            thesis_profile=self,
            math_converter=math_converter,
            reference_anchors=reference_anchors,
            markdown_dir=markdown_dir,
            cover_assets_dir=cover_assets_dir,
            media_manager=media_manager,
        )
