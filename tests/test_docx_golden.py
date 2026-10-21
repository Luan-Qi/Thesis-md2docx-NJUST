from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

from thesis_md2docx.exporter import write_docx

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

#: Hashes of the stable OOXML parts produced from `example/thesis-demo.md`.
#: Regenerate with `python tools/regenerate_golden.py` after an intentional
#: layout change -- and confirm the Word/PDF result first.
GOLDEN_DOCX_PART_HASHES = {
    "[Content_Types].xml": "e9847e7242955ed42703ddb62d73cd660faa3c035228eb1eb64fceff39853584",
    "_rels/.rels": "f2ee5d069d316d080de4513502475fc76cbd64a7c536cf2420faad30a053aaae",
    "docProps/app.xml": "fce1d0ca26f687eabbc9465481916002bebe2b7e31cfc53c83967485475b98fc",
    "word/_rels/document.xml.rels": "c2aa9aa1b2bd0f931bd0c94a36dd2fd0e05b944bbaf56c9d2fe3c9b74520200e",
    "word/document.xml": "3aaf2f296f9ae86e8d269bf6294ce7de39b47bc5faf52a3479d2765b882d6415",
    "word/styles.xml": "c875b84e33c74e867ee62b5927d1a6f9ee832267eb360a04cb6e7983cc7f23d8",
    "word/numbering.xml": "4f3c66e06770b052504c874dc38a0f297b52369daed0fad1b31721b9c47def9e",
    "word/settings.xml": "76838f5c3ff5c6bdbd19f9d7cd33abc5a1185aeb34531c7e3be9eeefbdbb0971",
    "word/fontTable.xml": "bc8932e4f16b2d81637b141a3d523a0e527f77a43bbfb1cabe735210ca225db5",
    "word/header1.xml": "287eacc9eca97742c48ff86a0b8d8b66953f1590713870c9f22ffd6d3c365009",
    "word/header2.xml": "619c6194a3415515b3c5145badfe7e35d75cd3de154631632a9bec1fb7ecc48d",
    "word/header3.xml": "d4a25dda5d7868b647b49e2d2d0453f21540b755832f050e001ba37460d89ea2",
    "word/footer1.xml": "7f427bed6b467a6447b86eaa8e77b65b2a4a682f2a157226384758992e8038a2",
    "word/footer2.xml": "3aed0984bdffc41980a32ac74d6064165d1b411041734d9acb2cd974513cb51b",
    "word/footer3.xml": "ce06ea3382729a1055337a6948920e4006d30f0b1c8fe2a48f2a280314170aaa",
}

EXAMPLE_MARKDOWN = Path("example/thesis-demo.md")


def _part_hash(docx_path: Path, part_name: str) -> str:
    with ZipFile(docx_path) as zf:
        return sha256(zf.read(part_name)).hexdigest()


def _write_example(tmp_path: Path) -> Path:
    output_path = tmp_path / "thesis-demo.docx"
    write_docx(EXAMPLE_MARKDOWN, output_path, enable_formula_conversion=False)
    return output_path


def test_example_docx_matches_golden_ooxml_parts(tmp_path: Path) -> None:
    output_path = _write_example(tmp_path)

    with ZipFile(output_path) as zf:
        names = set(zf.namelist())

    for part_name, expected in GOLDEN_DOCX_PART_HASHES.items():
        assert part_name in names, part_name
        assert _part_hash(output_path, part_name) == expected, part_name


# ---------------------------------------------------------------------------
# Structural regression checks
# ---------------------------------------------------------------------------


def _load_body(docx_path: Path) -> ET.Element:
    with ZipFile(docx_path) as zf:
        return ET.fromstring(zf.read("word/document.xml"))


def _text_of(paragraph: ET.Element) -> str:
    return "".join(text.text or "" for text in paragraph.findall(".//w:t", NS))


def _style_of(paragraph: ET.Element) -> str | None:
    node = paragraph.find("w:pPr/w:pStyle", NS)
    return node.get(f"{{{NS['w']}}}val") if node is not None else None


def test_toc_section_break_sits_on_its_own_small_paragraph(tmp_path: Path) -> None:
    root = _load_body(_write_example(tmp_path))
    paragraphs = root.find("w:body", NS).findall("w:p", NS)

    toc_indices = [i for i, p in enumerate(paragraphs) if _style_of(p) in ("TOC1", "TOC2", "TOC3")]
    assert toc_indices, "no TOC entries were generated"

    section_break = toc_indices[-1] + 1
    assert paragraphs[section_break].find("w:pPr/w:sectPr", NS) is not None
    # The section-break paragraph is the 1pt carrier, not a full body paragraph.
    assert 'w:line="1"' in ET.tostring(paragraphs[section_break], encoding="unicode")
    # The body starts on the very next paragraph, with no filler in between.
    assert "绪论" in _text_of(paragraphs[section_break + 1])


def test_chapters_do_not_force_page_breaks(tmp_path: Path) -> None:
    """规范 3.2：正文每一章不强制另页；只有 结论/致谢/参考文献/附录 另页。"""

    root = _load_body(_write_example(tmp_path))
    paragraphs = root.find("w:body", NS).findall("w:p", NS)
    texts = [_text_of(p) for p in paragraphs]

    def has_page_break(paragraph: ET.Element) -> bool:
        for br in paragraph.iter(f"{{{NS['w']}}}br"):
            if br.get(f"{{{NS['w']}}}type") in (None, "page"):
                return True
        return False

    ack = texts.index("致  谢")
    assert has_page_break(paragraphs[ack - 1])

    chapter = texts.index("绪论")
    assert not has_page_break(paragraphs[chapter])
    assert not has_page_break(paragraphs[chapter - 1])

    # 正文内不出现分节符
    assert all(p.find("w:pPr/w:sectPr", NS) is None for p in paragraphs[chapter:])


def test_even_page_header_and_outer_page_numbers(tmp_path: Path) -> None:
    output_path = _write_example(tmp_path)
    with ZipFile(output_path) as zf:
        names = set(zf.namelist())
        header_odd = zf.read("word/header1.xml").decode("utf-8")
        header_even = zf.read("word/header3.xml").decode("utf-8")
        settings = zf.read("word/settings.xml").decode("utf-8")
        footer_odd = zf.read("word/footer2.xml").decode("utf-8")
        footer_even = zf.read("word/footer3.xml").decode("utf-8")

    assert {"word/header3.xml", "word/footer3.xml"} <= names
    assert "STYLEREF" in header_even and "硕士学位论文" in header_even
    assert "STYLEREF" not in header_odd and "硕士学位论文" in header_odd
    assert "<w:evenAndOddHeaders/>" in settings
    assert 'w:jc w:val="right"' in footer_odd
    assert 'w:jc w:val="left"' in footer_even


def test_settings_do_not_ask_word_to_update_fields(tmp_path: Path) -> None:
    """生成的 DOCX 打开时不得弹出「该文档包含的域可能引用了其他文件」。

    触发这个提示的是两件事，两个都不能写：

    * `<w:updateFields w:val="true"/>`；
    * 任何带 `w:dirty="true"` 的域 —— 目录域尤其容易踩到，而 Word 对「有待更新
      的域」一律使用上述措辞，哪怕目录域只引用文档自身。

    页码由 `md2docx refresh-fields`（或用户在 Word 里更新一次目录）填入。
    """

    output_path = _write_example(tmp_path)
    with ZipFile(output_path) as zf:
        settings = zf.read("word/settings.xml").decode("utf-8")
        document = zf.read("word/document.xml").decode("utf-8")

    assert "<w:updateFields" not in settings
    assert 'w:dirty="true"' not in document
    assert 'TOC \\o "1-3"' in document


def test_refresh_fields_assets_are_shipped() -> None:
    from pathlib import Path as _Path

    from thesis_md2docx.main import build_parser

    vbs = _Path("thesis_md2docx/pdf/backends/word/word_update_fields.vbs")
    assert vbs.is_file()
    assert "Fields.Update" in vbs.read_text(encoding="utf-8")

    parser = build_parser()
    subparsers = next(
        action for action in parser._actions if action.dest == "command" and hasattr(action, "choices")
    )
    assert "refresh-fields" in subparsers.choices


def test_document_has_no_external_references(tmp_path: Path) -> None:
    output_path = _write_example(tmp_path)
    with ZipFile(output_path) as zf:
        for name in zf.namelist():
            if not name.endswith(".rels"):
                continue
            text = zf.read(name).decode("utf-8")
            assert 'TargetMode="External"' not in text, name
        document = zf.read("word/document.xml").decode("utf-8")

    for forbidden in ("INCLUDETEXT", "INCLUDEPICTURE", "RD ", "DDE", "AUTOTEXT"):
        assert forbidden not in document, forbidden
