"""Nanjing University of Science and Technology master's thesis constants.

Every number here traces back to one of two sources:

* 《南理工硕士论文格式.doc》 正文条款 + 附件 2.1-2.13 的文字说明与批注
  (referred to below as "规范"), as distilled in the project's `format.md`;
* the university's own already-typeset thesis (`_anno.docx`), used only for
  layout values the written specification deliberately leaves open
  (cover field coordinates, TOC indents, table rules).

Items the specification explicitly marks as "原文未明确" are listed in the
project README together with the value used here, so they can be overridden.
"""

from __future__ import annotations

from ...layout import PageGeometry, mm

# ---------------------------------------------------------------------------
# Page geometry -- 规范 2.1
#   A4, 上 30mm, 下 24mm, 左/右 25mm, 页眉 20mm, 页脚 20mm, 对称页边距.
# Left/right are written as 1418 twips rather than mm(25)=1417 so that the
# usable text width is exactly 160mm (11906 - 1418 - 1418 = 9070 twips), which
# is the figure the 规范 itself uses for header tab stops.
# ---------------------------------------------------------------------------
PAGE_WIDTH = 11906
PAGE_LEFT = 1418
PAGE_RIGHT = 1418
TEXT_WIDTH = PAGE_WIDTH - PAGE_LEFT - PAGE_RIGHT  # 9070 twips == 160mm
TEXT_CENTER = TEXT_WIDTH // 2  # 4535

PAGE_GEOMETRY = PageGeometry(
    width=PAGE_WIDTH,
    height=mm(297),
    top=mm(30),
    right=PAGE_RIGHT,
    bottom=mm(24),
    left=PAGE_LEFT,
    header=mm(20),
    footer=mm(20),
    gutter=0,
    cols_space=720,
    # 范例的节是 `docGrid type="linesAndChars" linePitch="326"`（=16.3pt 一行）。
    # 声明页那些 `snapToGrid` 段落正是靠它把 14pt 正文吸附成 2 格 = 32.6pt，
    # 所以那一页才铺得满；linePitch 若写成 384 或 type=default，吸附就失效。
    doc_grid_line_pitch=326,
    doc_grid_type="linesAndChars",
    mirror_margins=True,
)

# ---------------------------------------------------------------------------
# Fonts -- 规范 1 / 4 / 附件批注
# ---------------------------------------------------------------------------
FONT_CN = "宋体"
FONT_CN_HEI = "黑体"
FONT_CN_KAI = "楷体"
#: UDC 行「注1」的中文字体：范例 `参考封面.docx` 该 run 写死了 `w:eastAsia="华文中宋"`。
FONT_CN_HWZS = "华文中宋"
FONT_EN = "Times New Roman"

# ---------------------------------------------------------------------------
# Font sizes, in half-points (`w:sz`)
#   小一 24pt | 二号 22pt | 小二 18pt | 三号 16pt | 小三 15pt
#   四号 14pt | 小四 12pt | 五号 10.5pt | 小五 9pt
# ---------------------------------------------------------------------------
SIZE_XIAO_YI = 48  # 24pt  -- 封面试题名 小一号黑体加粗
SIZE_XIAO_ER = 36  # 18pt  -- 封面作者姓名 小二号楷体加粗
SIZE_SAN = 32  # 16pt  -- 前置页标题, 封面导师姓名
SIZE_XIAO_SAN = 30  # 15pt  -- 一级标题
SIZE_SI = 28  # 14pt  -- 二级标题, 关键词标签, 封面导师职称
SIZE_XIAO_SI = 24  # 12pt  -- 正文
SIZE_WU = 21  # 10.5pt -- 图表题与表内文字
SIZE_XIAO_WU = 18  # 9pt   -- 页眉页脚

# 封面「硕 士 学 位 论 文」批注写的是 "32号楷体"，规范未给出磅值。
# 学校自己的排版件用 sz=64（=32pt），此处沿用，并在 README 中标注。
SIZE_COVER_DEGREE = 64  # 32pt

# ---------------------------------------------------------------------------
# Paragraph spacing -- 规范 4.2 / 4.3 / 4.4 (twips; 1pt = 20 twips)
# ---------------------------------------------------------------------------
LINE_FIXED_20PT = 400  # 固定值 20 磅
LINE_KAI_28PT = 560  # 封面字段固定行距 28 磅（范例反推）
LINE_KAI_HALF = 240  # 单倍行距（范例反推：声明页、表格）
LINE_SAN_SI = 340  # 封面"(作者姓名)"提示行（范例反推）

BEFORE_H1 = 360  # 18pt
BEFORE_H2 = 240  # 12pt
BEFORE_H3 = 120  # 6pt
BEFORE_H4 = 120  # 6pt

# 目录标题的段前/段后：**规范只规定了字体**（「目录」二字 3 号宋体加粗），没有给段距；
# 学校排版件（`_anno.docx`）的「目    录」用的是 **一级标题样式**（before/after = 360
# twips = 18pt），与摘要 / Abstract 标题一致。早期误按「上空 18mm」实现（=51pt），
# 比范例大了近 3 倍，目录页顶部会空出很大一块——已修正。
BEFORE_TOC_TITLE = 360  # 18pt，同一级标题
AFTER_TOC_TITLE = 360  # 18pt

# ---------------------------------------------------------------------------
# Body indents -- 规范 13 未明确首行缩进；范例为 2 字符
# ---------------------------------------------------------------------------
BODY_FIRST_LINE_CHARS = 200
BODY_FIRST_LINE = 480  # 2 chars @ 小四

# ---------------------------------------------------------------------------
# Table of contents -- 规范 6.2 只规定字体与加粗；缩进与制表位为范例反推
# ---------------------------------------------------------------------------
TOC_TAB_POS = TEXT_WIDTH  # 右对齐制表位落在正文右边界
TOC1_LEFT = 0
TOC2_LEFT = 420
TOC3_LEFT = 839
TOC_FIRST_STOP = 283

# ---------------------------------------------------------------------------
# Cover -- coordinates reverse-engineered from the university's own thesis
# (`_anno.docx`), approved by the project owner. See README "封面布局".
# ---------------------------------------------------------------------------
COVER_LOGO_WIDTH_EMU = 4509770  # 4.932in == 1085px @220dpi
COVER_LOGO_HEIGHT_EMU = 1059815  # 1.159in ==  255px @220dpi
COVER_TOP_TAB_CENTER = 4536
COVER_TOP_TAB_RIGHT = 9072
COVER_TOP_FIRST_LINE = 420
# 范例：分类号/密级行 before=163 twips (beforeLines=50)；UDC 行只有缩进。
# Word 在两者同时存在时**优先取 beforeLines**，因此实际段前是 0.5 行 = 10pt，
# 而不是 163 twips (8.15pt)。两个值照范例都写，差值约 1.9pt。
COVER_TOP_BEFORE = 163
COVER_TOP_BEFORE_LINES = 50
# 范例逐 run 还原：分类号 + 下划线空格 + 普通空格 + 密级 + 下划线空格。
# 密级是靠普通空格推到右侧的——是**位置**铺到页面两端，不是下划线铺满整行。
COVER_TOP_UNDERLINE_PT = 105.0  # 分类号后下划线宽度（点）
COVER_TOP_GAP_PT = 142.0  # 分类号与密级之间的普通空格宽度（点）
# 密级后的下划线比分类号那条短：像素实测参考封面 37.0mm vs 31.5mm。
COVER_TOP_UNDERLINE_RIGHT_PT = 89.0  # 密级后下划线宽度（点）
# UDC 行：「UDC」+ 下划线「注1」+ 下划线空格。
COVER_UDC_LABEL = "UDC"
COVER_UDC_NOTE = "注1"
COVER_UDC_UNDERLINE_PT = 100.0
# 封面模板保留的两行括号提示（范例 line=360 / line=340，均 exact）。
COVER_TITLE_HINT = "(题名和副题名)"
COVER_AUTHOR_HINT = "(作者姓名)"
COVER_TITLE_HINT_LINE = 360
COVER_AUTHOR_HINT_LINE = 340
COVER_DEGREE_FIRST_LINE_CHARS = 31
COVER_DEGREE_FIRST_LINE = 199
COVER_TITLE_LINE_RULE = "auto"
COVER_TITLE_LINE = 240
COVER_FIELD_FIRST_LINE_CHARS = 300
COVER_FIELD_FIRST_LINE = 843
COVER_FIELD_FIRST_LINE_SHORT = 783
# 范例中封面字段值靠空格对齐；其 8280 的制表位一旦真正被 Tab 触发，值会落到
# 右边界之外并折行。这里把值列改到正文约 46% 处：与范例视觉一致且不会折行。
COVER_FIELD_TAB = 4200
COVER_FIELD_TAB_PT = 210.0  # 同上，点为单位
COVER_FIELD_GAP_SPACES = 12  # 标签与值之间的下划线空格个数（照范例）
# 字段填空位的总宽（点）。范例六行的下划线**等宽**：像素实测都从 69.6mm 起、
# 到 156.4mm 止，即 86.8mm ≈ 246pt。
COVER_FIELD_FILL_PT = 246.0
# 值的**水平中心**（相对填空位左端，点）。范例里各行的值不是左对齐，而是居中在
# 这条中心线附近：工学硕士 / 通信与信息系统 / 交通智能感知 的中心都在 109.5mm
# （页面坐标），减去填空位起点 69.6mm 得 39.9mm ≈ 113.1pt。
# 这正是「***」「教授」比下面几行靠右、而「通信与信息系统」比它们靠左的原因。
COVER_FIELD_VALUE_CENTER_PT = 113.1
COVER_FIELD_LABEL_UNITS = 6  # 「指导教师姓名」的全角字个数
COVER_AUTHOR_BLANK_LINE = 600  # (作者姓名) 之下的空行：30 磅
# 填写项下划线的总宽度（点）。每行都补齐到这个宽度，保证等长且左端对齐。
COVER_FIELD_UNDERLINE_PT = 160.0
# 标签与值之间用下划线空格填充（附件2.1 该段同样带下划线）。
COVER_FIELD_GAP_PT = 210.0
# 范例：导师姓名行是该字段块的第一行，段前 before=326 twips 且 beforeLines=100。
# Word 同时存在两者时取 beforeLines=100 → 段前 1 行 = 28pt（该行 line=560 exact）。
# 注意：规范附件 2.1 同一处写的是 before=312（范例是 326），差 0.7pt；因两处都写
# beforeLines=100，实际渲染无差别。这里取范例值以便与 `参考封面.docx` 逐值对齐。
# 其余字段行（导师职称、学位类别、学科名称、研究方向、论文提交时间）都没有段前。
COVER_FIELD_BEFORE = 326
COVER_FIELD_BEFORE_LINES = 100
COVER_SIGNATURE_RIGHT = 62

# 封面两条独立横线（附件 2.1）。范例里它们是 wps 浮动直线（`mc:AlternateContent`）：
#   题名下方   5057775 EMU = 7965 twips = 140.4mm，居中
#   作者姓名下方 1824990 EMU = 2874 twips =  50.7mm，居中
# 本项目用「段落下框线 + 左右等距缩进」复现（不引入 VML/形状），线宽 = 正文宽
# 9070 − 左右缩进之和，所以这里存的是**线宽**，缩进在 frontmatter 里均分。
# 两条线粗细均为 0.75pt（范例 `a:ln w=9525`），与 `_cover_rule()` 的 sz=6 一致。
COVER_RULE_TITLE_WIDTH = 7965
COVER_RULE_AUTHOR_WIDTH = 2874
# 题名区**每一行下方都有一条横线**（规范附件 2.1），因此两行题名 = 两条线；
# 题名只有一行时，第二行留空但横线照画——用户明确要求"两行下划线"。
COVER_TITLE_MIN_LINES = 2
# 范例：论文提交时间行的所有 run 都带字符间距 -10（-0.5pt），把这一行压窄。
# 这是该行与相邻行长度差 1.1mm 的来源，实测对齐后加上。
COVER_SUBMIT_CHAR_SPACING = -10

# ---------------------------------------------------------------------------
# Declaration page -- 规范 5.2 + 附件 2.5
#   声明与学位论文使用授权声明同页，上、下两部分，正文内容不得改动。
# ---------------------------------------------------------------------------
DECLARATION_TITLE = "声  明"
AUTHORISATION_TITLE = "学位论文使用授权声明"
DECLARATION_BODY = (
    "本学位论文是我在导师的指导下取得的研究成果，尽我所知，在本学位论文中，"
    "除了加以标注和致谢的部分外，不包含其他人已经发表或公布过的研究成果，"
    "也不包含我为获得任何教育机构的学位或学历而使用过的材料。"
    "与我一同工作的同事对本学位论文做出的贡献均已在论文中作了明确的说明。"
)
AUTHORISATION_BODY = (
    "南京理工大学有权保存本学位论文的电子和纸质文档，可以借阅或上网公布本学位论文的"
    "部分或全部内容，可以向有关部门或机构送交并授权其保存、借阅或上网公布本学位论文的"
    "部分或全部内容。对于保密论文，按保密的有关规定和程序处理。"
)
SIGNATURE_LABEL = "研究生签名："
SIGNATURE_DATE = "年  月  日"
# 范例：签名行的下划线空格数在上下两份声明里不同（12 / 13），下划线之后还有
# 13 个**普通**空格才到「年 月 日」。改动这几个数会直接改变下划线长度。
DECLARATION_SIGNATURE_UNDERLINE = 12
AUTHORISATION_SIGNATURE_UNDERLINE = 13
SIGNATURE_DATE_GAP = 13
DECLARATION_FIRST_LINE = 560
DECLARATION_TITLE_FIRST_LINE_CHARS = 62
DECLARATION_TITLE_FIRST_LINE = 199
# 范例：声明页标题「声  明」的段落不带 spacing 覆盖，继承 Normal 的**固定值 20 磅**；
# 而「学位论文使用授权声明」标题显式写了单倍行距（line=240 auto）。两者不同。
DECLARATION_TITLE_LINE = LINE_FIXED_20PT

# ---------------------------------------------------------------------------
# Abstract -- 规范 6.1
# ---------------------------------------------------------------------------
CN_KEYWORD_PREFIX = "关键词："
EN_KEYWORD_PREFIX = "Key word: "
# 关键词之间统一用逗号（用户要求）：中文「，」、英文「, 」。
CN_KEYWORD_SEPARATOR = "，"
EN_KEYWORD_SEPARATOR = ", "
KEYWORD_BLANK_PARAGRAPHS = 2

# ---------------------------------------------------------------------------
# Layout values the specification leaves open but that the generator must fix.
# Recorded here so the README can list them next to the value in use.
# ---------------------------------------------------------------------------
# 规范 13：「封面未被批注覆盖的字段位置和字体」未明确 -> 采用与已批注的
# 「学位类别」标签一致的四号宋体加粗。
COVER_UNSPECIFIED_FIELD_SIZE = SIZE_SI
# 规范 13：「表格三线表、边框粗细」未明确 -> 正文表格默认三线表（上下框线
# 1.5 磅、无内线），与学校实际排版件一致；可用富表格语法逐表覆盖。
TABLE_TOP_BOTTOM_BORDER_SIZE = 12  # eighths of a point -> 1.5pt


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------
COVER_ASSET_NAME = "njust-logo.png"
COVER_ASSET_LOCAL_REL = "img/cover-assets"

# ---------------------------------------------------------------------------
# Chapter structure -- 规范 3.1 / 3.2
# ---------------------------------------------------------------------------
# 另页开始的标题（规范 3.2 明确列举；正文每章不强制另页）
PAGE_BREAK_HEADINGS = frozenset({"结论", "致谢", "参考文献", "附录"})
UNNUMBERED_HEADINGS = frozenset({"结论", "致谢", "参考文献", "附录"})
