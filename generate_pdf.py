#!/usr/bin/env python3
"""Generate a clean PDF from the presentation content with CJK font support."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    KeepTogether, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# ── Font Registration ──────────────────────────────────────────────────────────
FONT_NAME = "WQYZenHei"
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

try:
    pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH, subfontIndex=0))
    pdfmetrics.registerFont(TTFont(FONT_NAME + "B", FONT_PATH, subfontIndex=0))  # same file, no bold variant
    print(f"Registered font: {FONT_NAME} from {FONT_PATH}")
except Exception as e:
    print(f"Font registration failed: {e}")
    FONT_NAME = "Helvetica"
    FONT_NAME_B = "Helvetica-Bold"

FONT_B = FONT_NAME  # WQY has no separate bold file; rely on weight styling

# ── Color Palette ──────────────────────────────────────────────────────────────
C_NAVY      = HexColor("#1a2744")   # deep navy – chapter headers
C_BLUE      = HexColor("#2563eb")   # accent blue – slide titles
C_TEAL      = HexColor("#0891b2")   # teal – sub-headers
C_ORANGE    = HexColor("#ea580c")   # orange – callout / labels
C_LIGHT     = HexColor("#f0f4ff")   # light blue – shaded rows
C_GRAY      = HexColor("#6b7280")   # body-text gray
C_RULE      = HexColor("#cbd5e1")   # rule lines

# ── Page Setup ────────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4
MARGIN_L = 2.2 * cm
MARGIN_R = 2.2 * cm
MARGIN_T = 2.0 * cm
MARGIN_B = 2.0 * cm

# ── Styles ────────────────────────────────────────────────────────────────────
def make_styles():
    s = {}

    def ps(name, **kw):
        kw.setdefault("fontName", FONT_NAME)
        return ParagraphStyle(name, **kw)

    s["cover_title"] = ps("cover_title",
        fontSize=28, leading=36, textColor=C_NAVY,
        spaceAfter=8, alignment=TA_CENTER, fontName=FONT_NAME)

    s["cover_sub"] = ps("cover_sub",
        fontSize=14, leading=20, textColor=C_BLUE,
        spaceAfter=6, alignment=TA_CENTER)

    s["cover_tagline"] = ps("cover_tagline",
        fontSize=11, leading=16, textColor=C_GRAY,
        spaceAfter=4, alignment=TA_CENTER)

    s["chapter_label"] = ps("chapter_label",
        fontSize=9, leading=12, textColor=white,
        spaceBefore=18, spaceAfter=4, alignment=TA_LEFT)

    s["chapter_title"] = ps("chapter_title",
        fontSize=18, leading=24, textColor=white,
        spaceAfter=6, alignment=TA_LEFT)

    s["chapter_sub"] = ps("chapter_sub",
        fontSize=10, leading=14, textColor=HexColor("#bfdbfe"),
        spaceAfter=0, alignment=TA_LEFT)

    s["slide_title"] = ps("slide_title",
        fontSize=16, leading=22, textColor=C_NAVY,
        spaceBefore=20, spaceAfter=6)

    s["slide_num"] = ps("slide_num",
        fontSize=9, leading=12, textColor=C_ORANGE,
        spaceBefore=0, spaceAfter=2)

    s["section_header"] = ps("section_header",
        fontSize=12, leading=16, textColor=C_TEAL,
        spaceBefore=10, spaceAfter=4)

    s["route_label"] = ps("route_label",
        fontSize=9, leading=12, textColor=white,
        spaceBefore=0, spaceAfter=0)

    s["route_title"] = ps("route_title",
        fontSize=11, leading=15, textColor=C_NAVY,
        spaceBefore=6, spaceAfter=2)

    s["body"] = ps("body",
        fontSize=10, leading=15, textColor=C_GRAY,
        spaceAfter=4)

    s["bullet"] = ps("bullet",
        fontSize=10, leading=15, textColor=C_GRAY,
        leftIndent=14, spaceAfter=3,
        bulletIndent=0, bulletFontName=FONT_NAME, bulletFontSize=10)

    s["sub_bullet"] = ps("sub_bullet",
        fontSize=9, leading=13, textColor=C_GRAY,
        leftIndent=28, spaceAfter=2)

    s["label_tag"] = ps("label_tag",
        fontSize=9, leading=12, textColor=C_ORANGE,
        spaceBefore=4, spaceAfter=1)

    s["callout"] = ps("callout",
        fontSize=10, leading=15, textColor=C_NAVY,
        spaceBefore=8, spaceAfter=4,
        borderPadding=(6, 8, 6, 8))

    s["conclusion"] = ps("conclusion",
        fontSize=10, leading=15, textColor=C_ORANGE,
        spaceBefore=8, spaceAfter=4)

    s["toc_item"] = ps("toc_item",
        fontSize=12, leading=18, textColor=C_NAVY,
        spaceAfter=6, leftIndent=10)

    s["toc_desc"] = ps("toc_desc",
        fontSize=10, leading=14, textColor=C_GRAY,
        spaceAfter=8, leftIndent=10)

    s["summary_box"] = ps("summary_box",
        fontSize=10, leading=15, textColor=C_NAVY,
        spaceAfter=4, leftIndent=8)

    return s


# ── Helper Flowable Builders ──────────────────────────────────────────────────
def rule(color=C_RULE, thickness=0.5, spaceBefore=4, spaceAfter=6):
    return HRFlowable(width="100%", thickness=thickness,
                      color=color, spaceAfter=spaceAfter, spaceBefore=spaceBefore)


def chapter_block(s, num, title, subtitle):
    """A colored banner for chapter dividers."""
    data = [[
        Paragraph(f"CHAPTER {num}", s["chapter_label"]),
    ], [
        Paragraph(title, s["chapter_title"]),
    ], [
        Paragraph(subtitle, s["chapter_sub"]),
    ]]
    tbl = Table(data, colWidths=[PAGE_W - MARGIN_L - MARGIN_R])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 16),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_NAVY]),
    ]))
    return [Spacer(1, 0.3 * cm), tbl, Spacer(1, 0.4 * cm)]


def slide_header(s, num, title):
    """Slide number tag + title line."""
    return [
        Paragraph(f"SLIDE {num}", s["slide_num"]),
        Paragraph(title, s["slide_title"]),
        rule(C_BLUE, thickness=1.5, spaceBefore=2, spaceAfter=8),
    ]


def bullet_item(s, text, indent=0):
    style = s["sub_bullet"] if indent else s["bullet"]
    return Paragraph(f"• {text}", style)


def labeled_item(s, label, title, body_lines):
    """Colored label + title + body paragraphs for route/section items."""
    items = []
    # label badge via table
    badge = Table([[Paragraph(label, s["route_label"])]],
                  colWidths=[None])
    badge.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_TEAL),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ]))
    items.append(badge)
    items.append(Paragraph(title, s["route_title"]))
    for line in body_lines:
        items.append(Paragraph(line, s["body"]))
    items.append(Spacer(1, 0.15 * cm))
    return items


def orange_label(s, text):
    return Paragraph(text, s["label_tag"])


def conclusion_line(s, text):
    return [
        rule(C_ORANGE, thickness=0.8, spaceBefore=10, spaceAfter=4),
        Paragraph(f"结论：{text}", s["conclusion"]),
    ]


def two_col_table(s, left_items, right_items, header_left="", header_right=""):
    """Simple 2-column table."""
    col_w = (PAGE_W - MARGIN_L - MARGIN_R - 0.5 * cm) / 2

    def cell(items):
        return "\n".join(items)

    rows = []
    if header_left or header_right:
        rows.append([
            Paragraph(header_left, s["section_header"]),
            Paragraph(header_right, s["section_header"]),
        ])
    max_len = max(len(left_items), len(right_items))
    for i in range(max_len):
        l = Paragraph(left_items[i], s["body"]) if i < len(left_items) else Paragraph("", s["body"])
        r = Paragraph(right_items[i], s["body"]) if i < len(right_items) else Paragraph("", s["body"])
        rows.append([l, r])

    tbl = Table(rows, colWidths=[col_w, col_w])
    style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    if header_left or header_right:
        style += [
            ("BACKGROUND", (0, 0), (-1, 0), C_LIGHT),
            ("FONTNAME", (0, 0), (-1, 0), FONT_NAME),
        ]
    tbl.setStyle(TableStyle(style))
    return tbl


# ── Content Builder ────────────────────────────────────────────────────────────
def build_story(s):
    story = []

    # ─────────────────────────────────────────────────
    # SLIDE 1 – COVER
    # ─────────────────────────────────────────────────
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph("高德 × 世界模型", s["cover_title"]))
    story.append(Paragraph("空间智能时代的产品思考", s["cover_sub"]))
    story.append(Spacer(1, 0.4 * cm))
    story.append(rule(C_BLUE, thickness=2, spaceBefore=0, spaceAfter=10))
    story.append(Paragraph("行业技术研判 · 高德战略机会 · 用户痛点洞察", s["cover_tagline"]))
    story.append(Spacer(1, 1.5 * cm))

    # ─────────────────────────────────────────────────
    # SLIDE 2 – 目录
    # ─────────────────────────────────────────────────
    story += slide_header(s, 2, "目录")
    toc_rows = [
        ("01  行业发展分析", "技术路线 · 应用痛点 · 竞品格局"),
        ("02  高德 × 世界模型", "痛点机会 · 优势劣势 · 落地节奏"),
        ("03  用户视角", "出行痛点 · 解法对应 · 未来延展"),
    ]
    for num_title, desc in toc_rows:
        story.append(Paragraph(num_title, s["toc_item"]))
        story.append(Paragraph(desc, s["toc_desc"]))
    story.append(Spacer(1, 0.5 * cm))

    # ─────────────────────────────────────────────────
    # CHAPTER 1
    # ─────────────────────────────────────────────────
    story += chapter_block(s, 1, "世界模型行业发展分析",
                           "先判断技术路线与行业格局，再判断高德该如何落地")

    # ─────────────────────────────────────────────────
    # SLIDE 4 – 技术路线
    # ─────────────────────────────────────────────────
    story += slide_header(s, 4, "世界模型当前的技术路线")

    routes = [
        ("01 / 视频生成路线", "(Sora · Veo)",
         ["从海量视频中学习光影、材质、运动和场景连续性，画面高度逼真。",
          "但模型对因果关系理解薄弱，无法真正懂得交通规则与行动后果，",
          "生成内容「看起来真」不等于「可用于决策」。"],
         "高德切入：用于路线预览与解释层，不替代地图事实"),
        ("02 / 3D空间智能", "(World Labs Marble)",
         ["生成可转身、可探索、具备三维一致性的空间模型，支持多视角查看与室内外连续导航。",
          "核心挑战是全国规模的采集和实时更新成本极高，动态人流、车流仍难以稳定建模。"],
         "高德切入：优先做路口、枢纽、停车场局部孪生"),
        ("03 / 交互环境路线", "(Genie · SIMA)",
         ["在可交互环境中训练智能体，通过观察动作带来的后果来学习。",
          "具备强交互性与可评测性，适合验证极端场景策略。",
          "将游戏规则迁移至真实道路仍需地图数据约束。"],
         "高德切入：Scenario Lab 场景生成 + 导航策略仿真评测"),
        ("04 / JEPA抽象状态", "(V-JEPA 2)",
         ["不预测像素，预测高维抽象状态的下一步变化，更接近对世界的真实「理解」。",
          "利于规划、长时序推理与机器人决策。",
          "不直接输出可展示画面，产品表达需要额外转化。"],
         "高德切入：路线风险预测、动态分流与决策内核"),
    ]

    for title, subtitle, body_lines, cutpoint in routes:
        story.append(Paragraph(title, s["section_header"]))
        story.append(Paragraph(subtitle, s["body"]))
        for line in body_lines:
            story.append(bullet_item(s, line))
        story.append(Paragraph(cutpoint, s["callout"]))
        story.append(Spacer(1, 0.2 * cm))

    story += conclusion_line(s, "视频真实感只是表层，地图对齐和行动后果才是高德的核心")

    # ─────────────────────────────────────────────────
    # SLIDE 5 – 切入点
    # ─────────────────────────────────────────────────
    story += slide_header(s, 5, "世界模型应用的切入点")

    opportunities = [
        ("智能交互", "SHORT-TERM",
         "用户的真实目标往往包含多个约束：顺路接人、找停车、避堵、带老人小孩……",
         "当前系统只能一个一个回答，无法给出综合最优方案",
         "小高老师多约束规划 · 路线解释 · 临时改计划"),
        ("数字孪生", "MID-TERM",
         "城市和商圈的三维资产常是静态快照，路况变化、施工封道、天气影响、大型活动人流等动态事件，",
         "难以实时融入空间模型",
         "路口/枢纽/商圈/停车场局部实时孪生"),
        ("仿真模拟", "MID-TERM",
         "导航和调度策略在上线前，极难覆盖恶劣天气、突发事故、临时封道、演唱会散场等长尾场景，",
         "线上才暴露问题代价极高",
         "复杂路口/极端天气仿真 · 车企与机器人场景评测"),
        ("决策支持", "LONG-TERM",
         "ETA预测、绕行推荐、拥堵分流对用户是黑盒——「为什么走这条路」没有解释，",
         "用户不信任、不采纳，业务也无法量化策略收益",
         "可解释分流策略 · 城市级事件推演 · 应急调度"),
    ]

    for title, horizon, pain1, pain2, solution in opportunities:
        badge_color = C_ORANGE if horizon == "SHORT-TERM" else (C_TEAL if horizon == "MID-TERM" else C_NAVY)
        badge = Table([[Paragraph(f"{title}  {horizon}", s["route_label"])]],
                      colWidths=[None])
        badge.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), badge_color),
            ("TOPPADDING",    (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ]))
        story.append(badge)
        story.append(Paragraph(f"痛点：{pain1}{pain2}", s["body"]))
        story.append(Paragraph(f"切口：{solution}", s["callout"]))
        story.append(Spacer(1, 0.2 * cm))

    story += conclusion_line(s, "先做近场高频可量化，再扩城市级生态")

    # ─────────────────────────────────────────────────
    # SLIDE 6 – 竞品分析
    # ─────────────────────────────────────────────────
    story += slide_header(s, 6, "竞品分析")

    competitors = [
        ("Google Maps / 体验层", "视觉沉浸领跑",
         ["Immersive View、Ask Maps、Live View AR",
          "把视觉表达做成下一代地图入口"],
         "优势：3D / 沉浸体验 ★"),
        ("百度 Apollo / 能力层", "车路协同深耕",
         ["高精地图、车道级导航、Apollo + OEM协同",
          "B端能力输出路径清晰"],
         "优势：智驾 / 车路协同 ★"),
        ("高德 / 数据层", "数据最强 · 待建模拟层",
         ["170M DAU + 实时路况 + Qwen + 阿里生态",
          "具备建立模拟/解释层的独特优势"],
         "优势：中国实时交通数据 ★  商业生态（阿里全域）★"),
    ]

    for name, tagline, bullets, strength in competitors:
        story.append(Paragraph(name, s["section_header"]))
        story.append(Paragraph(tagline, s["body"]))
        for b in bullets:
            story.append(bullet_item(s, b))
        story.append(Paragraph(strength, s["callout"]))
        story.append(Spacer(1, 0.15 * cm))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("对比矩阵", s["section_header"]))

    matrix_data = [
        [Paragraph("维度", s["section_header"]),
         Paragraph("Google Maps", s["section_header"]),
         Paragraph("百度Apollo", s["section_header"]),
         Paragraph("高德", s["section_header"])],
        [Paragraph("中国实时交通数据", s["body"]),
         Paragraph("●", s["body"]),
         Paragraph("●●", s["body"]),
         Paragraph("●●●  最强", s["body"])],
        [Paragraph("3D / 沉浸体验", s["body"]),
         Paragraph("●●●  最强", s["body"]),
         Paragraph("●", s["body"]),
         Paragraph("● 缺口", s["body"])],
        [Paragraph("智驾 / 车路协同", s["body"]),
         Paragraph("●", s["body"]),
         Paragraph("●●●  最强", s["body"]),
         Paragraph("● 缺口", s["body"])],
        [Paragraph("商业生态闭环", s["body"]),
         Paragraph("Google Search", s["body"]),
         Paragraph("智驾OEM", s["body"]),
         Paragraph("阿里全域", s["body"])],
    ]
    col_w_4 = (PAGE_W - MARGIN_L - MARGIN_R) / 4
    matrix_tbl = Table(matrix_data, colWidths=[col_w_4] * 4)
    matrix_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_NAVY),
        ("TEXTCOLOR",  (0, 0), (-1, 0), white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, C_LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.3, C_RULE),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(matrix_tbl)

    story += conclusion_line(s, "高德的不对称机会——在数据最密集处率先建立模拟层+解释层")

    # ─────────────────────────────────────────────────
    # CHAPTER 2
    # ─────────────────────────────────────────────────
    story += chapter_block(s, 2, "高德 × 世界模型",
                           "从行业判断，推导高德专属的产品机会与战略节奏")

    # ─────────────────────────────────────────────────
    # SLIDE 8 – 为什么做世界模型
    # ─────────────────────────────────────────────────
    story += slide_header(s, 8, "高德·为什么做世界模型")

    pain_opp = [
        ("痛点", C_ORANGE, [
            ("P/01", "最后100米断层", "到了附近找不到入口与楼层"),
            ("P/02", "路线推荐黑盒", "用户不理解为什么要绕行"),
            ("P/03", "静态地图vs动态世界", "变化只能事后响应"),
            ("P/04", "多端体验割裂", "手机/车机/AR缺统一空间理解"),
        ]),
        ("机会", C_TEAL, [
            ("O/01", "空间智能落地", "AR入口确认 + 室内连续导航"),
            ("O/02", "可解释导航", "把推荐理由「说出来」"),
            ("O/03", "动态路线预判", "提前感知，主动响应"),
            ("O/04", "统一空间状态", "多端共享同一空间模型"),
        ]),
    ]

    for section_name, color, items in pain_opp:
        story.append(Paragraph(section_name, s["section_header"]))
        for code, title, desc in items:
            row_data = [[
                Paragraph(code, s["route_label"]),
                Paragraph(f"<b>{title}</b>  —  {desc}", s["body"]),
            ]]
            row_tbl = Table(row_data, colWidths=[1.5 * cm, PAGE_W - MARGIN_L - MARGIN_R - 1.5 * cm])
            row_tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, 0), color),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING",    (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING",   (0, 0), (-1, -1), 6),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
            ]))
            story.append(row_tbl)
            story.append(Spacer(1, 0.1 * cm))
        story.append(Spacer(1, 0.2 * cm))

    # ─────────────────────────────────────────────────
    # SLIDE 9 – SWOT
    # ─────────────────────────────────────────────────
    story += slide_header(s, 9, "高德×世界模型·优势和劣势")

    story.append(Paragraph("优势（Strengths）", s["section_header"]))
    strengths = [
        ("S/01", "数据飞轮",
         "170M DAU + 实时路况 + 200M+ POI，Google/百度在中国无法复制的训练底座"),
        ("S/02", "Qwen + 阿里生态",
         "大模型内部直连，本地生活与电商完成商业闭环"),
        ("S/03", "本土高频场景",
         "中国出行场景反馈信号丰富，训练数据质量远高于通用模型"),
        ("S/04", "小高老师先发",
         "AI交互链路初步建立，意图理解能力已有积累"),
    ]
    for code, title, desc in strengths:
        story.append(Paragraph(f"<b>{code}  {title}</b>  —  {desc}", s["body"]))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("挑战（Weaknesses）", s["section_header"]))
    weaknesses = [
        ("W/01", "3D数据缺口",
         "全国高精3D地图采集成本极高，短期难对标Google"),
        ("W/02", "智驾生态弱",
         "车端数据与OEM协同深度不及百度Apollo"),
        ("W/03", "算力投入",
         "世界模型训练需极大算力，依赖阿里云资源协同"),
    ]
    for code, title, desc in weaknesses:
        story.append(Paragraph(f"<b>{code}  {title}</b>  —  {desc}", s["body"]))

    story.append(Spacer(1, 0.3 * cm))
    story += conclusion_line(s,
        "不做全球3D，不追赶智驾。做中国出行链路上最懂用户意图的空间智能平台。")

    # ─────────────────────────────────────────────────
    # SLIDE 10 – RoadMap
    # ─────────────────────────────────────────────────
    story += slide_header(s, 10, "未来 RoadMap")

    phases = [
        ("PHASE 01", "0–12个月", "近场可验证（高频痛点，指标可量化）",
         ["复杂路口风险解释", "停车场/室内最后100米", "路线推荐理由卡片"],
         "指标：错过率↓  采纳率↑", C_ORANGE),
        ("PHASE 02", "1–2年", "链路延展（多端打通，主动规划）",
         ["小高老师主动出行规划", "AR/车机统一空间状态", "活动/枢纽散场分流"],
         "指标：ETA误差↓  转化率↑", C_TEAL),
        ("PHASE 03", "2–3年+", "生态化平台（空间智能输出）",
         ["城市级事件推演", "车企/机器人/低空仿真", "空间智能API生态"],
         "指标：B端收入 · API调用", C_NAVY),
    ]

    for phase_label, timeframe, desc, bullets, metric, color in phases:
        header_data = [[
            Paragraph(phase_label, s["route_label"]),
            Paragraph(timeframe, s["route_label"]),
            Paragraph(desc, s["route_label"]),
        ]]
        h_col_w = (PAGE_W - MARGIN_L - MARGIN_R) / 3
        header_tbl = Table(header_data, colWidths=[h_col_w] * 3)
        header_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), color),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(header_tbl)
        for b in bullets:
            story.append(bullet_item(s, b))
        story.append(Paragraph(metric, s["callout"]))
        story.append(Spacer(1, 0.25 * cm))

    story.append(Spacer(1, 0.2 * cm))
    summary_items = [
        "事实层  来自地图",
        "模拟层  负责推演",
        "解释层  面向用户",
        "执行层  必须可确认",
    ]
    summary_w = (PAGE_W - MARGIN_L - MARGIN_R - 0.3 * cm) / 4
    summary_data = [[Paragraph(item, s["summary_box"]) for item in summary_items]]
    summary_tbl = Table(summary_data, colWidths=[summary_w] * 4)
    summary_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_LIGHT),
        ("GRID", (0, 0), (-1, -1), 0.5, C_RULE),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(summary_tbl)

    # ─────────────────────────────────────────────────
    # CHAPTER 3
    # ─────────────────────────────────────────────────
    story += chapter_block(s, 3, "用户视角的优化思路",
                           "从亲身出行体验出发，看高德与世界模型的真实结合点")

    # ─────────────────────────────────────────────────
    # SLIDE 12 – 我的出行痛点
    # ─────────────────────────────────────────────────
    story += slide_header(s, 12, "我的出行痛点")

    pain_layers = [
        ("L/01", "位置层",
         "商场出来定位漂移，找朋友只能靠微信电话互相指引",
         "室内外定位断层，二维坐标无法表达真实三维空间"),
        ("L/02", "路径层",
         "不知道哪个地铁口有电梯、哪个出口排队少",
         "缺少「软信息」，系统不区分用户身体差异与实际约束"),
        ("L/03", "决策层",
         "选错出口后已叫车，只能取消订单重打",
         "信息缺失导致事后后悔，没有预演与因果解释"),
        ("L/04", "协同层",
         "大商场里和朋友互相找不到，各自的地图都说「已到达」",
         "多人空间协同缺失，系统只服务单用户、单时刻"),
    ]

    for code, layer, scene, essence in pain_layers:
        row_data = [[
            Paragraph(f"{code}\n{layer}", s["route_label"]),
            [
                Paragraph(f"场景：{scene}", s["body"]),
                Paragraph(f"本质：{essence}", s["callout"]),
            ],
        ]]
        row_tbl = Table(row_data, colWidths=[1.8 * cm, PAGE_W - MARGIN_L - MARGIN_R - 1.8 * cm])
        row_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), C_NAVY),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ]))
        story.append(row_tbl)
        story.append(Spacer(1, 0.15 * cm))

    story += conclusion_line(s, "当前地图只懂路网，不懂空间；只服务平均人，不服务具体人")

    # ─────────────────────────────────────────────────
    # SLIDE 13 – 四层痛点对应
    # ─────────────────────────────────────────────────
    story += slide_header(s, 13, "世界模型如何接住这四层痛点")

    mapping = [
        ("L/01 位置层", "VLM+视觉定位 → 3D空间智能路线",
         "看懂图像，锚定空间",
         "AR步行入口确认 / 室内外无缝定位"),
        ("L/02 路径层", "具身智能+用户画像 → JEPA抽象状态路线",
         "物理约束建模，理解具体人",
         "个性化路径推荐 / 无障碍/软信息"),
        ("L/03 决策层", "状态推演+因果链解释 → 交互环境路线",
         "预演「接下来会怎样」",
         "出口结果预演 / 推荐理由/降级提示"),
        ("L/04 协同层", "共享三维场景+Multi-Agent → 3D+交互环境路线",
         "多人共享同一空间状态",
         "多人实时空间定位 / 集合点推荐"),
    ]

    col_ws = [2.2 * cm, 4.5 * cm, 3.5 * cm, 4.5 * cm]
    header_row = [
        Paragraph("痛点层", s["section_header"]),
        Paragraph("技术路线", s["section_header"]),
        Paragraph("核心能力", s["section_header"]),
        Paragraph("产品表达", s["section_header"]),
    ]
    map_rows = [header_row]
    for layer, tech, capability, product in mapping:
        map_rows.append([
            Paragraph(layer, s["body"]),
            Paragraph(tech, s["body"]),
            Paragraph(capability, s["body"]),
            Paragraph(product, s["body"]),
        ])
    map_tbl = Table(map_rows, colWidths=col_ws)
    map_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_NAVY),
        ("TEXTCOLOR",  (0, 0), (-1, 0), white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, C_LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.3, C_RULE),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(map_tbl)

    story += conclusion_line(s,
        "四层痛点恰好对应世界模型四条技术路线——不是巧合，是世界模型本来就该服务真实出行")

    # ─────────────────────────────────────────────────
    # SLIDE 14 – 延展痛点
    # ─────────────────────────────────────────────────
    story += slide_header(s, 14, "延展痛点：未来可能衍生的方向")

    extensions = [
        ("01", "AR眼镜时代，导航的下一代形态",
         "从「低头看屏幕」到「抬头看世界」，路口标识与入口指引叠加在真实视野中，"
         "高德世界模型成为AR的空间理解引擎。",
         "新终端入口 · 阿里AI眼镜生态协同"),
        ("02", "低空经济，三维空域的数字底座",
         "eVTOL、无人机配送、空中出租车——低空经济开启垂直出行维度，高德已布局低空数字地图，"
         "世界模型提供立体航线规划与空地协同导航的推演基础。",
         "阿里低空战略协同 · 城市三维导航新入口"),
        ("03", "多人出行Agent，家庭与社交场景",
         "家庭、团建、约会场景下的多用户协同——位置、偏好、约束统一调度，"
         "共享空间状态即共享决策模型。",
         "从「工具」到「生活协同平台」"),
        ("04", "车路协同，世界模型的终极形态",
         "同时服务车、人、路、城市基建——红绿灯、车辆、行人进入同一空间状态。"
         "不只是智驾，而是城市级实时智能体。",
         "集团对城市治理与智驾的长期布局"),
    ]

    for num, title, desc, tag in extensions:
        story.append(Paragraph(f"  {num}  {title}", s["section_header"]))
        story.append(Paragraph(desc, s["body"]))
        story.append(Paragraph(tag, s["callout"]))
        story.append(Spacer(1, 0.2 * cm))

    story.append(rule(C_NAVY, thickness=1.5, spaceBefore=10, spaceAfter=6))
    story.append(Paragraph(
        "总结：我的痛点是入口，真正的产品机会是把高德从「导航工具」升级为"
        "「可推演真实世界变化的空间智能平台」",
        s["conclusion"]))

    return story


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    output_path = "/home/user/air/presentation-content.pdf"
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN_L,
        rightMargin=MARGIN_R,
        topMargin=MARGIN_T,
        bottomMargin=MARGIN_B,
        title="高德 × 世界模型 — 空间智能时代的产品思考",
        author="产品研究",
    )

    styles = make_styles()
    story = build_story(styles)
    doc.build(story)
    print(f"PDF saved to: {output_path}")
    size = os.path.getsize(output_path)
    print(f"File size: {size:,} bytes")


if __name__ == "__main__":
    main()
