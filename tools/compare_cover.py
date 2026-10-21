#!/usr/bin/env python3
"""一键回归：把生成的封面与学校参考封面做**像素级**对版。

做法与 AGENT.md 第 6 节的方法论一致——不靠推理，靠量：

1. 参考件（`format_requirements/参考封面.docx`）与候选件（默认 `example/thesis-demo.md`）
   各自经 Word 后端导出 PDF；
2. 用 `pdftoppm` 以同一 DPI 渲染第 1 页（封面）；
3. 扫描每一条**横线**（分类号/密级下划线、两道题名线、作者线、六条填空位下划线），
   得到它们的起点 x、终点 x、长度与 y；同时给出六个字段行里"值"的墨迹范围，
   用来确认值是否按范例**居中**在填空位里；
4. 逐条与参考件比较，超出容差即退出码 1，可挂进 CI 或提交前检查。

用法：

    python tools/compare_cover.py                          # 默认：demo 封面 vs 参考封面
    python tools/compare_cover.py thesis.md                # 指定自己的 Markdown
    python tools/compare_cover.py --out output/cover.md     # 指定报告路径
    python tools/compare_cover.py --tolerance-mm 1.5        # 收紧容差
    python tools/compare_cover.py --no-export               # 复用已导出的 PDF，快速迭代

注意：需要 Microsoft Word（与 `md2docx pdf --backend word` 相同的前置条件）；
`pdftoppm` 来自 poppler / MiKTeX。两者缺失时会给出明确报错而不是静默跳过。
"""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from thesis_md2docx.pdf_compare import render_pdf_to_images  # noqa: E402

DEFAULT_REFERENCE = ROOT / "format_requirements" / "参考封面.docx"
DEFAULT_CANDIDATE = ROOT / "example" / "thesis-demo.md"
DEFAULT_OUT = ROOT / "example" / "output" / "cover-audit.md"
DEFAULT_WORK = ROOT / ".cover-compare"

#: 封面上每条横线的名字，顺序与页面从上到下一致。
RULE_NAMES = (
    "分类号下划线",
    "密级下划线",
    "UDC下划线",
    "题名第1行横线",
    "题名第2行横线",
    "作者姓名横线",
    "指导教师姓名",
    "导师职称",
    "学位类别",
    "学科名称",
    "研究方向",
    "论文提交时间",
)


# ---------------------------------------------------------------------------
# 渲染
# ---------------------------------------------------------------------------


def ensure_pdf(
    source: Path,
    *,
    work_dir: Path,
    backend: str,
    export: bool,
    keep_existing: bool = False,
) -> Path:
    """把 .md / .docx 变成 PDF；`export=False` 时要求 PDF 已存在。"""

    if source.suffix.lower() == ".pdf":
        return source

    pdf_path = work_dir / f"{source.stem}.pdf"
    if not export and pdf_path.is_file():
        return pdf_path
    if keep_existing and pdf_path.is_file():
        return pdf_path

    docx_path = source
    if source.suffix.lower() == ".md":
        from thesis_md2docx.exporter import write_docx

        docx_path = work_dir / f"{source.stem}.docx"
        write_docx(source, docx_path)
    elif source.suffix.lower() != ".docx":
        raise SystemExit(f"unsupported input: {source} (expected .md, .docx or .pdf)")

    work_dir.mkdir(parents=True, exist_ok=True)
    if backend == "word":
        from thesis_md2docx.pdf.backends.word import backend as word_backend

        word_backend.convert(docx_path, pdf_path)
    else:
        from thesis_md2docx.pdf.registry import get_backend

        import argparse as _argparse

        args = _argparse.Namespace(
            input=str(docx_path),
            output=str(pdf_path),
            tmp_root=None,
            vbs_template=None,
            keep_tmp=False,
            skip_word_check=False,
            no_update_fields=None,
            soffice=None,
        )
        get_backend(backend).convert(args)
    return pdf_path


# ---------------------------------------------------------------------------
# 测量
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Rule:
    """一条横线（下划线/段落下框线），单位 mm，原点是页面左上角。"""

    y: float
    start: float
    end: float

    @property
    def length(self) -> float:
        return self.end - self.start


@dataclass(frozen=True)
class Measured:
    width_mm: float
    height_mm: float
    dpi: int
    rules: tuple[Rule, ...]
    image: Path


def _load_gray(image: Path):
    from PIL import Image

    im = Image.open(image).convert("L")
    return im, im.size, im.load()


def measure_rules(
    image: Path,
    *,
    dpi: int,
    min_length_mm: float = 18.0,
    max_thickness_px: int = 4,
    min_coverage: float = 0.80,
) -> Measured:
    """扫描"细长横线"（下划线 / 段落下框线）。

    判据三条，缺一不可——校徽图片与加粗文字的长笔迹都会被前两条排除：

    1. 一行里存在 ≥ `min_length_mm` 的**连续**墨迹（文字的字间空隙会打断它）；
    2. 该行的墨迹**覆盖率**（最长连续段 / 全行墨迹数）≥ `min_coverage`，
       文字行因为还有其他笔画而远低于此；
    3. 相邻行里 **起止 x 都接近**（±6px）的才合并成同一条线，厚度 ≤ 4 行为一条。
       只按 y 相邻合并会把"分类号"和"密级"两条同高度但相距很远的线连成一条。
    """

    im, (width, height), px = _load_gray(image)
    px_per_mm = dpi / 25.4
    min_px = min_length_mm * px_per_mm

    candidates: list[tuple[int, int, int]] = []
    for y in range(height):
        runs: list[tuple[int, int]] = []
        run_start = None
        for x in range(width):
            dark = px[x, y] < 200
            if dark and run_start is None:
                run_start = x
            elif not dark and run_start is not None:
                runs.append((run_start, x))
                run_start = None
        if run_start is not None:
            runs.append((run_start, width))
        if not runs:
            continue
        long_runs = [(a, b) for a, b in runs if b - a >= min_px]
        if not long_runs:
            continue
        # 覆盖率按"所有长段之和 / 全行墨迹"算：分类号与密级两条线在同一行，
        # 各占一段，都算长段，所以这一行的覆盖率仍是 1.0；文字行则远低于 0.85。
        total = sum(b - a for a, b in runs)
        covered = sum(b - a for a, b in long_runs)
        if covered / total < min_coverage:
            continue
        for a, b in long_runs:
            candidates.append((y, a, b))

    groups: list[dict[str, int]] = []
    for y, a, b in candidates:
        for group in groups:
            if y - group["y_last"] <= 2 and abs(a - group["start"]) <= 6 and abs(b - group["end"]) <= 6:
                group["y_last"] = y
                group["rows"] += 1
                break
        else:
            groups.append({"y_last": y, "y": y, "start": a, "end": b, "rows": 1})

    rules: list[Rule] = []
    for group in groups:
        if group["rows"] > max_thickness_px:
            continue
        if group["end"] - group["start"] < min_px:
            continue
        rules.append(
            Rule(
                y=round(group["y"] / px_per_mm, 2),
                start=round(group["start"] / px_per_mm, 2),
                end=round(group["end"] / px_per_mm, 2),
            )
        )
    return Measured(
        width_mm=round(width / px_per_mm, 2),
        height_mm=round(height / px_per_mm, 2),
        dpi=dpi,
        rules=tuple(rules),
        image=image,
    )


def measure_value_spans(measured: Measured, *, band: tuple[int, int] = (34, 6)) -> dict[str, tuple[float, float]]:
    """每个填充行"值"的墨迹横向范围（mm）。

    值在范例里是**居中**的，位置比长度更能说明对齐是否正确，所以单独量一份。
    判据：取该行横线起点之后的所有墨迹（标签在横线起点之前），合并成一个区间。
    """

    _, (_, _), px = _load_gray(measured.image)
    px_per_mm = measured.dpi / 25.4
    out: dict[str, tuple[float, float]] = {}
    for index, rule in enumerate(measured.rules):
        if index >= len(RULE_NAMES) or RULE_NAMES[index] not in RULE_NAMES[6:]:
            continue
        y_rule = int(rule.y * px_per_mm)
        cutoff = int((rule.start + 0.5) * px_per_mm)
        columns: list[bool] = []
        for x in range(int(measured.width_mm * px_per_mm)):
            hit = False
            for y in range(max(0, y_rule - band[0]), max(0, y_rule - band[1])):
                if px[x, y] < 200:
                    hit = True
                    break
            columns.append(hit)
        spans = [x for x in range(cutoff, len(columns)) if columns[x]]
        if spans:
            out[RULE_NAMES[index]] = (
                round(spans[0] / px_per_mm, 2),
                round((spans[-1] + 1) / px_per_mm, 2),
            )
    return out


# ---------------------------------------------------------------------------
# 比较与报告
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Diff:
    name: str
    reference: Rule
    candidate: Rule
    length_delta: float
    start_delta: float
    y_delta: float


def compare(reference: Measured, candidate: Measured) -> list[Diff]:
    diffs: list[Diff] = []
    for index, (ref_rule, cand_rule) in enumerate(zip(reference.rules, candidate.rules)):
        name = RULE_NAMES[index] if index < len(RULE_NAMES) else f"第{index + 1}条"
        diffs.append(
            Diff(
                name=name,
                reference=ref_rule,
                candidate=cand_rule,
                length_delta=round(cand_rule.length - ref_rule.length, 2),
                start_delta=round(cand_rule.start - ref_rule.start, 2),
                y_delta=round(cand_rule.y - ref_rule.y, 2),
            )
        )
    return diffs


def build_report(
    *,
    reference_path: Path,
    candidate_path: Path,
    reference: Measured,
    candidate: Measured,
    diffs: list[Diff],
    tolerance_mm: float,
    value_spans: dict[str, tuple[tuple[float, float], tuple[float, float]]],
) -> str:
    failures = [
        d
        for d in diffs
        if abs(d.length_delta) > tolerance_mm
        or abs(d.start_delta) > tolerance_mm
        or abs(d.y_delta) > tolerance_mm
    ]
    lines: list[str] = []
    lines.append("# 封面对版报告")
    lines.append("")
    lines.append(f"- 参考件：`{reference_path}`")
    lines.append(f"- 候选件：`{candidate_path}`")
    lines.append(f"- 渲染：{candidate.dpi} dpi，页面 {candidate.width_mm}×{candidate.height_mm} mm")
    lines.append(f"- 容差：{tolerance_mm} mm；结论：**{'通过' if not failures else '不通过'}**")
    lines.append("")
    lines.append("## 横线（起点 / 终点 / 长度 / y，单位 mm）")
    lines.append("")
    lines.append("| 元素 | 参考 起..止(长) | 生成 起..止(长) | 长差 | 起点差 | y 差 | 判定 |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for diff in diffs:
        ok = (
            abs(diff.length_delta) <= tolerance_mm
            and abs(diff.start_delta) <= tolerance_mm
            and abs(diff.y_delta) <= tolerance_mm
        )
        lines.append(
            "| {name} | {r.start:.1f}..{r.end:.1f} ({r_len:.1f}) | {c.start:.1f}..{c.end:.1f} ({c_len:.1f}) "
            "| {ld:+.1f} | {sd:+.1f} | {yd:+.1f} | {verdict} |".format(
                name=diff.name,
                r=diff.reference,
                c=diff.candidate,
                r_len=diff.reference.length,
                c_len=diff.candidate.length,
                ld=diff.length_delta,
                sd=diff.start_delta,
                yd=diff.y_delta,
                verdict="✅" if ok else "❌",
            )
        )
    lines.append("")
    lines.append("## 字段行「值」的横向范围（范例中值是居中的）")
    lines.append("")
    lines.append("| 行 | 参考 | 生成 | 中心差 |")
    lines.append("| --- | --- | --- | --- |")
    for name, (ref_span, cand_span) in value_spans.items():
        ref_center = (ref_span[0] + ref_span[1]) / 2
        cand_center = (cand_span[0] + cand_span[1]) / 2
        lines.append(
            f"| {name} | {ref_span[0]:.1f}..{ref_span[1]:.1f} | {cand_span[0]:.1f}..{cand_span[1]:.1f} "
            f"| {cand_center - ref_center:+.1f} |"
        )
    lines.append("")
    if failures:
        lines.append("## 超差项")
        lines.append("")
        for diff in failures:
            lines.append(
                f"- **{diff.name}**：长差 {diff.length_delta:+.1f} mm、起点差 {diff.start_delta:+.1f} mm、"
                f"y 差 {diff.y_delta:+.1f} mm"
            )
        lines.append("")
    lines.append("> 横线由 `pdftoppm` 渲染后按像素扫描得到；`+` 表示生成件更大/更靠右/更靠下。")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python tools/compare_cover.py",
        description="Compare the generated cover page against the school reference cover, pixel by pixel.",
    )
    parser.add_argument("candidate", nargs="?", type=Path, default=DEFAULT_CANDIDATE,
                        help="Candidate thesis (.md or .docx). Defaults to example/thesis-demo.md.")
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE,
                        help="Reference cover (.docx or .pdf). Defaults to format_requirements/参考封面.docx.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Markdown report path.")
    parser.add_argument("--work-dir", type=Path, default=DEFAULT_WORK,
                        help="Scratch directory for PDFs and PNGs. Defaults to .cover-compare/.")
    parser.add_argument("--dpi", type=int, default=120, help="Rasterization DPI. Defaults to 120.")
    parser.add_argument("--tolerance-mm", type=float, default=2.5,
                        help="Allowed deviation per rule, in mm. Defaults to 2.5 (see AGENT.md "
                             "'封面已知残差').")
    parser.add_argument("--backend", default="word", help="DOCX to PDF backend. Defaults to word.")
    parser.add_argument("--no-export", action="store_true",
                        help="Reuse PDFs already produced in --work-dir.")
    parser.add_argument("--quiet", action="store_true", help="Do not print the table.")
    args = parser.parse_args(argv)

    if not args.reference.is_file():
        raise SystemExit(f"reference not found: {args.reference}")
    if not shutil.which("pdftoppm"):
        raise SystemExit(
            "pdftoppm not found; install poppler-utils (or use the MiKTeX bin dir) and retry"
        )

    work_dir: Path = args.work_dir
    work_dir.mkdir(parents=True, exist_ok=True)
    render_dir = work_dir / "pages"

    reference_pdf = ensure_pdf(
        args.reference, work_dir=work_dir, backend=args.backend, export=not args.no_export
    )
    candidate_pdf = ensure_pdf(
        args.candidate, work_dir=work_dir, backend=args.backend, export=not args.no_export
    )

    ref_images = render_pdf_to_images(reference_pdf, render_dir, dpi=args.dpi, prefix="ref")
    cand_images = render_pdf_to_images(candidate_pdf, render_dir, dpi=args.dpi, prefix="cand")
    if not ref_images or not cand_images:
        raise SystemExit("pdftoppm produced no pages")

    reference = measure_rules(ref_images[0], dpi=args.dpi)
    candidate = measure_rules(cand_images[0], dpi=args.dpi)

    if len(reference.rules) != len(candidate.rules):
        print(
            f"横线数量不一致：参考 {len(reference.rules)} 条，候选 {len(candidate.rules)} 条",
            file=sys.stderr,
        )
        for measured, label in ((reference, "参考"), (candidate, "候选")):
            print(f"  {label}: " + ", ".join(f"{r.start:.1f}..{r.end:.1f}@{r.y:.1f}" for r in measured.rules))
        return 2

    diffs = compare(reference, candidate)
    ref_spans = measure_value_spans(reference)
    cand_spans = measure_value_spans(candidate)
    value_spans = {
        name: (ref_spans[name], cand_spans[name])
        for name in ref_spans
        if name in cand_spans
    }

    report = build_report(
        reference_path=args.reference,
        candidate_path=args.candidate,
        reference=reference,
        candidate=candidate,
        diffs=diffs,
        tolerance_mm=args.tolerance_mm,
        value_spans=value_spans,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")

    if not args.quiet:
        print(report)
        print(f"报告已写入 {args.out}")

    failures = [
        d
        for d in diffs
        if abs(d.length_delta) > args.tolerance_mm
        or abs(d.start_delta) > args.tolerance_mm
        or abs(d.y_delta) > args.tolerance_mm
    ]
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
