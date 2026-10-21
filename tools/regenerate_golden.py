#!/usr/bin/env python3
"""Regenerate the DOCX golden hashes in `tests/test_docx_golden.py`.

Run this only after an intentional layout change, and confirm the Word/PDF
result first:

    python tools/regenerate_golden.py
"""

from __future__ import annotations

import hashlib
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from thesis_md2docx.exporter import write_docx  # noqa: E402

MARKDOWN = ROOT / "example" / "thesis-demo.md"
PROFILE = "njust-master-thesis"
CONSTANT = "GOLDEN_DOCX_PART_HASHES"

TEST_FILE = ROOT / "tests" / "test_docx_golden.py"

PART_NAMES = [
    "[Content_Types].xml",
    "_rels/.rels",
    "docProps/app.xml",
    "word/_rels/document.xml.rels",
    "word/document.xml",
    "word/styles.xml",
    "word/numbering.xml",
    "word/settings.xml",
    "word/fontTable.xml",
    "word/header1.xml",
    "word/header2.xml",
    "word/header3.xml",
    "word/footer1.xml",
    "word/footer2.xml",
    "word/footer3.xml",
]


def build() -> dict[str, str]:
    # Write the scratch document inside the repository rather than the system
    # temp directory: restricted environments sometimes deny writes there.
    scratch = ROOT / ".golden-tmp"
    scratch.mkdir(parents=True, exist_ok=True)
    try:
        output = scratch / "golden.docx"
        write_docx(MARKDOWN, output, enable_formula_conversion=False, profile=PROFILE)
        with zipfile.ZipFile(output) as zf:
            return {name: hashlib.sha256(zf.read(name)).hexdigest() for name in PART_NAMES}
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def render(hashes: dict[str, str]) -> str:
    lines = [f"{CONSTANT} = {{"]
    for name, digest in hashes.items():
        lines.append(f'    "{name}": "{digest}",')
    lines.append("}")
    return "\n".join(lines)


def main() -> int:
    source = TEST_FILE.read_text(encoding="utf-8")
    pattern = re.compile(rf"^{CONSTANT} = \{{.*?^\}}$", re.S | re.M)
    if not pattern.search(source):
        print(f"{CONSTANT} not found in {TEST_FILE}")
        return 2

    hashes = build()
    source = pattern.sub(lambda _: render(hashes), source, count=1)
    TEST_FILE.write_text(source, encoding="utf-8")
    print(f"regenerated {CONSTANT} ({len(hashes)} parts)")
    print(f"updated {TEST_FILE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
