#!/usr/bin/env python3
"""
Generate REVISED PDF text draft — content updates only, do NOT modify presentation.html
Changes: S4 (Fantasy World/Gaussian Splatting), S5 (数字孪生 vs 仿真), S6 (竞合关系重构),
         S8 (专业产品语言), S9 (真实技术资产), S10 (RoadMap更新), S12 (3层+图片占位),
         S13 (具体解决方案), S14 (阿里/高德技术资产绑定)
"""

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
    pdfmetrics.registerFont(TTFont(FONT_NAME + "B", FONT_PATH, subfontIndex=0))
    print(f"Registered font: {FONT_NAME} from {FONT_PATH}")
except Exception as e:
    print(f"Font registration failed: {e}")
    FONT_NAME = "Helvetica"

FONT_B = FONT_NAME

# ── Color Palette ──────────────────────────────────────────────────────────────
C_NAVY      = HexColor("#1a2744")
C_BLUE      = HexColor("#2563eb")
C_TEAL      = HexColor("#0891b2")
C_ORANGE    = HexColor("#ea580c")
C_LIGHT     = HexColor("#f0f4ff")
C_GRAY      = HexColor("#6b7280")
C_RULE      = HexColor("#cbd5e1")
C_GREEN     = HexColor("#059669")
C_PURPLE    = HexColor("#7c3aed")
C_AMBER     = HexColor("#d97706")

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

    s["callout_orange"] = ps("callout_orange",
        fontSize=10, leading=15, textColor=C_ORANGE,
        spaceBefore=4, spaceAfter=4)

    s["note"] = ps("note",
        fontSize=9, leading=13, textColor=C_AMBER,
        spaceBefore=4, spaceAfter=4,
        leftIndent=10)

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

    s["photo_placeholder"] = ps("photo_placeholder",
        fontSize=9, leading=13, textColor=HexColor("#9ca3af"),
        spaceBefore=4, spaceAfter=4, alignment=TA_CENTER)

    s["diff_note"] = ps("diff_note",
        fontSize=9, leading=13, textColor=C_GREEN,
        spaceBefore=2, spaceAfter=2, leftIndent=8)

    return s


# ── Helper Flowable Builders ──────────────────────────────────────────────────
def rule(color=C_RULE, thickness=0.5, spaceBefore=4, spaceAfter=6):
    return HRFlowable(width="100%", thickness=thickness,
                      color=color, spaceAfter=spaceAfter, spaceBefore=spaceBefore)


def chapter_block(s, num, title, subtitle):
    data = [[Paragraph(f"CHAPTER {num}", s["chapter_label"])],
            [Paragraph(title, s["chapter_title"])],
            [Paragraph(subtitle, s["chapter_sub"])]]
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
    return [
        Paragraph(f"SLIDE {num}", s["slide_num"]),
        Paragraph(title, s["slide_title"]),
        rule(C_BLUE, thickness=1.5, spaceBefore=2, spaceAfter=8),
    ]


def bullet_item(s, text, indent=0):
    style = s["sub_bullet"] if indent else s["bullet"]
    return Paragraph(f"• {text}", style)


def photo_placeholder_box(s, label):
    """Create a placeholder box for a photo."""
    data = [[Paragraph(f"[ 图片占位 — {label} ]", s["photo_placeholder"])]]
    tbl = Table(data, colWidths=[PAGE_W - MARGIN_L - MARGIN_R - 1 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#f3f4f6")),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, C_RULE),
    ]))
    return tbl


def conclusion_line(s, text):
    return [
        rule(C_ORANGE, thickness=0.8, spaceBefore=10, spaceAfter=4),
        Paragraph(f"结论：{text}", s["conclusion"]),
    ]


def tech_tag(s, text, color=C_TEAL):
    """Small inline tech tag."""
    badge = Table([[Paragraph(text, s["route_label"])]],
                  colWidths=[None])
    badge.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
    ]))
    return badge


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
        ("01  行业发展分析", "技术路线 · 应用痛点 · 竞合格局"),
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
    # SLIDE 4 – 技术路线  【改动】
    # 3D路线：引入 Fantasy World + Gaussian Splatting
    # 交互环境路线：去掉 Scenario Lab（存疑），改为高德自研情景推演
    # ─────────────────────────────────────────────────
    story += slide_header(s, 4, "世界模型当前的技术路线")

    routes = [
        {
            "num": "01",
            "title": "视频生成路线",
            "subtitle": "(Sora · Veo)",
            "bullets": [
                "从海量视频中学习光影、材质、运动和场景连续性，画面高度逼真。",
                "但模型对因果关系理解薄弱，无法真正懂得交通规则与行动后果。",
                "生成内容「看起来真」不等于「可用于决策」。",
            ],
            "cutpoint": "高德切入：用于路线预览与解释层，不替代地图事实",
            "color": C_ORANGE,
            "changed": False,
        },
        {
            "num": "02",
            "title": "3D空间智能路线",
            "subtitle": "(World Labs · Marble · Fantasy World)",
            "bullets": [
                "生成可转身、可探索、具备三维一致性的空间模型，支持多视角查看与室内外连续导航。",
                "高德/阿里自研 Fantasy World 世界模型提供三维空间推理基础设施。",
                "高斯泼溅（Gaussian Splatting）技术：从多角度拍摄图像重建高质量三维场景，可实时渲染并交互——已在高德局部场景（停车场/重点路口）落地验证。",
                "核心挑战：全国规模化采集成本高，动态人流、车流实时更新仍是工程难点。",
            ],
            "cutpoint": "高德切入：基于 Fantasy World + 高斯泼溅，优先在地铁站、商圈、停车场等高频枢纽构建可交互的动态三维场景；以真实3D路况数据为训练底座，逐步扩展城市覆盖",
            "color": C_TEAL,
            "changed": True,
        },
        {
            "num": "03",
            "title": "交互环境路线",
            "subtitle": "(Genie · SIMA)",
            "bullets": [
                "在可交互环境中训练智能体，通过观察「动作→后果」来学习策略。",
                "具备强交互性与可评测性，适合验证极端场景（演唱会散场/地震疏散）。",
                "将游戏规则迁移至真实道路，需要严格的地图数据约束与物理合规性。",
            ],
            "cutpoint": "高德切入：自研情景推演引擎，构建演唱会散场 / 商场临时关闭 / 自然灾害等极端场景，用于导航策略仿真评测与主动预警",
            "color": C_PURPLE,
            "changed": True,
        },
        {
            "num": "04",
            "title": "JEPA抽象状态路线",
            "subtitle": "(V-JEPA 2)",
            "bullets": [
                "不预测像素，预测高维抽象状态的下一步变化，更接近对世界的真实「理解」。",
                "利于规划、长时序推理与机器人决策。",
                "不直接输出可展示画面，产品表达需要额外转化层。",
            ],
            "cutpoint": "高德切入：路线风险预测、动态分流与可解释决策内核",
            "color": C_NAVY,
            "changed": False,
        },
    ]

    for r in routes:
        story.append(Paragraph(f"0{r['num']} / {r['title']}  {r['subtitle']}", s["section_header"]))
        if r["changed"]:
            story.append(Paragraph("▲ 内容已更新", s["diff_note"]))
        for line in r["bullets"]:
            story.append(bullet_item(s, line))
        story.append(Paragraph(f"→ {r['cutpoint']}", s["callout"]))
        story.append(Spacer(1, 0.2 * cm))

    story += conclusion_line(s, "高德独特优势：Fantasy World + 高斯泼溅 + 170M真实出行数据，构建行业最难复制的3D路况训练底座")

    # ─────────────────────────────────────────────────
    # SLIDE 5 – 切入点  【改动】
    # 明确区分 数字孪生 vs 仿真模拟，补充技术基础说明
    # ─────────────────────────────────────────────────
    story += slide_header(s, 5, "世界模型应用的切入点")

    story.append(Paragraph("▲ 内容更新说明：数字孪生 vs 仿真模拟 区分说明", s["diff_note"]))
    story.append(Spacer(1, 0.15 * cm))

    # 概念区分说明
    concept_rows = [
        [
            Paragraph("概念", s["section_header"]),
            Paragraph("数字孪生（Digital Twin）", s["section_header"]),
            Paragraph("仿真模拟（Simulation）", s["section_header"]),
        ],
        [
            Paragraph("核心问题", s["body"]),
            Paragraph("「现在是什么状态？」", s["body"]),
            Paragraph("「如果…会怎样？」", s["body"]),
        ],
        [
            Paragraph("关键词", s["body"]),
            Paragraph("镜像 · 实时 · 同步", s["body"]),
            Paragraph("推演 · 假设 · 反事实", s["body"]),
        ],
        [
            Paragraph("技术基础", s["body"]),
            Paragraph("IoT传感器 + 高精地图 + 实时数据流 + 高斯泼溅三维重建", s["body"]),
            Paragraph("世界模型 + 因果推理引擎 + 交互式智能体", s["body"]),
        ],
        [
            Paragraph("对高德的意义", s["body"]),
            Paragraph("路口/枢纽/停车场「现在是什么状态」", s["body"]),
            Paragraph("演唱会散场关闭出口「会堵多久」/地震「最优疏散路线」", s["body"]),
        ],
        [
            Paragraph("关系", s["body"]),
            Paragraph("数字孪生 ≈ 实时更新的地图底座", s["body"]),
            Paragraph("仿真模拟 = 在孪生基础上运行 What-If 推演", s["body"]),
        ],
    ]
    col_w_3 = [2.8 * cm, (PAGE_W - MARGIN_L - MARGIN_R - 2.8 * cm) / 2,
               (PAGE_W - MARGIN_L - MARGIN_R - 2.8 * cm) / 2]
    concept_tbl = Table(concept_rows, colWidths=col_w_3)
    concept_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_NAVY),
        ("TEXTCOLOR",  (0, 0), (-1, 0), white),
        ("BACKGROUND", (1, 1), (1, -1), HexColor("#eff6ff")),
        ("BACKGROUND", (2, 1), (2, -1), HexColor("#f0fdf4")),
        ("ROWBACKGROUNDS", (0, 1), (0, -1), [HexColor("#f9fafb")]),
        ("GRID", (0, 0), (-1, -1), 0.3, C_RULE),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(concept_tbl)
    story.append(Spacer(1, 0.3 * cm))

    opportunities = [
        ("智能交互", "SHORT-TERM", C_ORANGE,
         "用户真实需求包含多个约束：顺路接人、避堵、带小孩……当前系统只能一个一个回答，无法综合最优",
         "小高老师多约束规划 · 路线解释 · 临时改计划"),
        ("数字孪生", "MID-TERM", C_TEAL,
         "路口/商圈/停车场的状态是动态的——施工封道、人流聚集、出口临时关闭，难以实时融入地图底座\n→ 技术基础：IoT + 高精地图 + 高斯泼溅三维重建",
         "高频枢纽局部实时孪生（停车场/地铁站/商圈）"),
        ("仿真模拟", "MID-TERM", C_PURPLE,
         "导航策略上线前极难覆盖：演唱会散场、临时封道、极端天气等长尾场景，线上暴露代价高\n→ 数字孪生是前提，仿真在孪生底座上运行 What-If 推演",
         "极端场景预演 · 导航策略评测 · 应急路径规划"),
        ("决策支持", "LONG-TERM", C_NAVY,
         "ETA预测、绕行推荐对用户是黑盒——用户不理解为什么走这条路，不信任、不采纳",
         "可解释分流策略 · 城市级事件推演 · 应急调度"),
    ]

    for title, horizon, color, pain, solution in opportunities:
        badge = Table([[Paragraph(f"{title}  [{horizon}]", s["route_label"])]],
                      colWidths=[None])
        badge.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), color),
            ("TOPPADDING",    (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ]))
        story.append(badge)
        for line in pain.split("\n"):
            story.append(bullet_item(s, line.strip("→ ")))
        story.append(Paragraph(f"切口：{solution}", s["callout"]))
        story.append(Spacer(1, 0.2 * cm))

    story += conclusion_line(s, "数字孪生 = 知道现在；仿真模拟 = 预见未来。高德需要两者，而不只是地图更新")

    # ─────────────────────────────────────────────────
    # SLIDE 6 – 竞品分析  【改动】
    # 重构为「生态格局 / 竞合关系」，区分直接竞争者 vs 参照系
    # 建议位置移至 Chapter 2，放在 SWOT 之后、RoadMap 之前
    # ─────────────────────────────────────────────────
    story += slide_header(s, 6, "行业生态格局与竞合关系")

    story.append(Paragraph("▲ 内容更新：重构为竞合关系分析，而非简单竞品对比", s["diff_note"]))
    story.append(Paragraph(
        "注：Google Maps 在中国不可用，受监管限制；百度 Apollo 主要定位自动驾驶B2B，"
        "与高德C端导航赛道差异明显。建议改为「行业生态格局」框架，以竞合关系视角分析。",
        s["note"]))
    story.append(Paragraph(
        "【版面建议】本页适合移至 Chapter 2（高德×世界模型），置于 SWOT 之后、RoadMap 之前，"
        "作为高德战略选择的外部参照依据。",
        s["note"]))
    story.append(Spacer(1, 0.2 * cm))

    ecosystem = [
        {
            "name": "Google Maps / Apple Maps",
            "type": "全球技术标杆（非直接竞争）",
            "color": C_BLUE,
            "bullets": [
                "Immersive View（沉浸式三维导航）、Ask Maps、Live View AR——视觉体验全球领先",
                "在中国市场不可用，受监管限制；对高德不构成直接用户竞争",
                "对高德的意义：技术方向标，尤其是 3D/AR 视觉表达维度",
            ],
            "relation": "参照系：高德 3D 体验缺口有多大，跟着 Google 的节奏判断",
        },
        {
            "name": "百度地图 + Apollo",
            "type": "直接竞争者（地图C端）+ 智驾深耕（B端）",
            "color": C_ORANGE,
            "bullets": [
                "百度地图：中国C端导航直接竞对，市占率约 30–40%（vs 高德约 50%+）",
                "百度 Apollo：自动驾驶解决方案，已与多家车厂签约合作（吉利、长城、比亚迪等）",
                "Apollo 的核心逻辑：通过提供高精地图+算法包，嵌入OEM智驾产品线",
                "与高德的根本差异：Apollo 主打车端B2B；高德主打手机端C端用户出行",
            ],
            "relation": "竞合关系：地图层面竞争（C端）；智驾层面路线不同（高德暂无 OEM 深度整合）",
        },
        {
            "name": "腾讯地图",
            "type": "C端直接竞争者（微信生态）",
            "color": C_TEAL,
            "bullets": [
                "依托微信入口，社交+位置场景天然耦合（发定位/多人协同场景）",
                "技术积累相对薄弱，但微信生态粘性是差异化壁垒",
            ],
            "relation": "直接竞争：社交场景中的位置分享与协同导航",
        },
        {
            "name": "高德 Amap",
            "type": "中国出行数据最强 · 阿里生态协同",
            "color": C_GREEN,
            "bullets": [
                "170M+ DAU，中国实时交通数据覆盖最全",
                "Fantasy World（幻世界）：阿里自研世界模型基础设施，高德作为核心应用场景",
                "Qwen（通义千问）内部直连，多模态能力已集成进 AI 功能",
                "高斯泼溅技术已局部落地，三维场景重建能力有实际积累",
                "阿里全域生态：本地生活、淘宝、支付宝——商业闭环是独特护城河",
            ],
            "relation": "优势：数据 + 阿里AI基础设施 + 生态闭环  /  缺口：3D体验（对标Google）、智驾深度（对标Apollo）",
        },
    ]

    for item in ecosystem:
        story.append(Paragraph(f"{item['name']}  —  {item['type']}", s["section_header"]))
        for b in item["bullets"]:
            story.append(bullet_item(s, b))
        story.append(Paragraph(f"→ {item['relation']}", s["callout"]))
        story.append(Spacer(1, 0.15 * cm))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("竞合矩阵（更新版）", s["section_header"]))

    matrix_data = [
        [Paragraph("维度", s["section_header"]),
         Paragraph("Google Maps", s["section_header"]),
         Paragraph("百度Apollo", s["section_header"]),
         Paragraph("腾讯地图", s["section_header"]),
         Paragraph("高德", s["section_header"])],
        [Paragraph("中国C端用户", s["body"]),
         Paragraph("✗ 不可用", s["body"]),
         Paragraph("●● 地图竞争", s["body"]),
         Paragraph("●● 微信入口", s["body"]),
         Paragraph("●●● 最强", s["body"])],
        [Paragraph("3D/AR体验", s["body"]),
         Paragraph("●●● 标杆", s["body"]),
         Paragraph("●", s["body"]),
         Paragraph("●", s["body"]),
         Paragraph("● 缺口", s["body"])],
        [Paragraph("智驾/车路协同", s["body"]),
         Paragraph("●", s["body"]),
         Paragraph("●●● Apollo", s["body"]),
         Paragraph("●", s["body"]),
         Paragraph("● 机会待建", s["body"])],
        [Paragraph("阿里/AI基础设施", s["body"]),
         Paragraph("Google AI", s["body"]),
         Paragraph("百度大模型", s["body"]),
         Paragraph("腾讯混元", s["body"]),
         Paragraph("Fantasy World/Qwen", s["body"])],
        [Paragraph("商业生态", s["body"]),
         Paragraph("Google全球", s["body"]),
         Paragraph("智驾OEM", s["body"]),
         Paragraph("微信社交", s["body"]),
         Paragraph("阿里全域生态", s["body"])],
    ]
    col_w_5 = (PAGE_W - MARGIN_L - MARGIN_R) / 5
    matrix_tbl = Table(matrix_data, colWidths=[col_w_5] * 5)
    matrix_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_NAVY),
        ("TEXTCOLOR",  (0, 0), (-1, 0), white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, C_LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.3, C_RULE),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    story.append(matrix_tbl)

    story += conclusion_line(s,
        "Google定义3D体验方向标，百度Apollo深耕智驾B端，高德的不对称机会是："
        "中国出行数据最密集处，率先建立仿真推演层 + 可解释层")

    # ─────────────────────────────────────────────────
    # CHAPTER 2
    # ─────────────────────────────────────────────────
    story += chapter_block(s, 2, "高德 × 世界模型",
                           "从行业判断，推导高德专属的产品机会与战略节奏")

    # ─────────────────────────────────────────────────
    # SLIDE 8 – 为什么做世界模型  【改动】
    # 用专业产品语言重写痛点，四个结构性能力缺口
    # ─────────────────────────────────────────────────
    story += slide_header(s, 8, "高德·为什么做世界模型")

    story.append(Paragraph("▲ 内容更新：用产品框架语言重写系统性痛点", s["diff_note"]))
    story.append(Spacer(1, 0.1 * cm))

    structural_gaps = [
        ("P/01", "感知层断层", C_ORANGE,
         "室内外定位切换断裂：GPS 精度 2–10m，无楼层感知",
         "二维坐标系无法表达三维垂直空间（1F/B1/不同楼层）",
         "视觉环境与地图坐标脱节，用户在复杂枢纽内「地图漂移」",
         "影响：最后 100m 失效，室内场景完全靠人工描述"),
        ("P/02", "理解层黑盒", C_BLUE,
         "ETA 预测与绕行策略缺乏因果链说明",
         "系统默认「最优解」无法被用户理解和信任",
         "用户不采纳推荐 → 采纳率低 → 正向反馈信号稀缺",
         "影响：路线推荐价值未充分实现，差评积累"),
        ("P/03", "状态层滞后", C_TEAL,
         "施工封道、活动人流、临时出口关闭——数据更新延迟数小时到数天",
         "现有地图是「过去的快照」，不是「当前的状态」",
         "动态事件（演唱会/地震/大型节假日）无法提前感知",
         "影响：极端场景下导航失效，用户信任损失"),
        ("P/04", "情境层缺失", C_PURPLE,
         "不区分用户身体状态（带轮椅 / 崴脚 / 推婴儿车 / 带老人）",
         "不感知场景变化（演唱会散场 / 商场部分出口关闭 / 节假日高峰）",
         "系统服务「平均人」，不服务「具体人」",
         "影响：个性化导航机会完全缺失"),
    ]

    for code, title, color, b1, b2, b3, impact in structural_gaps:
        row_data = [[
            Paragraph(f"{code}\n{title}", s["route_label"]),
            [
                bullet_item(s, b1),
                bullet_item(s, b2),
                bullet_item(s, b3),
                Paragraph(f"影响：{impact}", s["callout_orange"]),
            ],
        ]]
        row_tbl = Table(row_data,
                        colWidths=[2.0 * cm, PAGE_W - MARGIN_L - MARGIN_R - 2.0 * cm])
        row_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), color),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ]))
        story.append(row_tbl)
        story.append(Spacer(1, 0.15 * cm))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("机会（Opportunities）", s["section_header"]))
    opportunities_2 = [
        ("O/01", "空间感知连续化", C_GREEN,
         "AR入口确认 + 室内外无缝定位 → VLM 视觉锚定 + 高斯泼溅三维场景"),
        ("O/02", "推荐可解释化", C_TEAL,
         "把路线推荐理由「说出来」→ Qwen 因果解释 + 用户信任建立"),
        ("O/03", "状态动态化", C_BLUE,
         "提前感知场景变化，主动响应 → Fantasy World 状态推演"),
        ("O/04", "情境个性化", C_ORANGE,
         "多端共享空间状态，服务具体人的具体约束 → 世界模型 + 用户画像"),
    ]
    for code, title, color, desc in opportunities_2:
        row_data = [[
            Paragraph(f"{code}", s["route_label"]),
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

    story += conclusion_line(s,
        "四个系统性缺口——感知断、理解黑盒、状态滞后、情境缺失——正是世界模型能填补的结构性空间")

    # ─────────────────────────────────────────────────
    # SLIDE 9 – SWOT  【改动】
    # 引入高德实际技术资产：Fantasy World, Gaussian Splatting, Qwen, VLM
    # ─────────────────────────────────────────────────
    story += slide_header(s, 9, "高德×世界模型·优势和挑战")

    story.append(Paragraph("▲ 内容更新：引入高德/阿里实际技术资产", s["diff_note"]))
    story.append(Spacer(1, 0.1 * cm))

    story.append(Paragraph("优势（Strengths）", s["section_header"]))
    strengths = [
        ("S/01", "数据飞轮",
         "170M DAU + 实时路况 + 200M+ POI。Google / 百度在中国无法复制的训练底座。"
         "真实出行轨迹密度是世界模型最难造假的核心资产。"),
        ("S/02", "Fantasy World — 阿里自研世界模型",
         "阿里巴巴内部基础设施，高德作为战略核心应用场景之一。"
         "提供三维空间推理与状态预测能力，区别于通用视频生成模型。"),
        ("S/03", "高斯泼溅（Gaussian Splatting）",
         "从多角度图像重建高质量、可交互的三维场景。"
         "已在高德局部场景验证（停车场/重点路口三维重建）。"
         "相比激光雷达点云，成本更低、可大规模部署，适合城市级快速覆盖。"),
        ("S/04", "VLM — 视觉语言模型",
         "图像-位置对齐能力：用手机拍摄周围环境即可精准定位。"
         "支持 AR 导航视觉锚定、室内场景识别、「用图片找位置」新交互范式。"),
        ("S/05", "Qwen — 通义千问",
         "阿里大模型内部直连，无需外部API授权。"
         "多模态能力（语音+图像+文字）已集成进高德AI功能。"
         "本地生活+电商生态闭环，商业转化链路完整。"),
        ("S/06", "本土高频场景",
         "中国出行场景反馈信号丰富（春运/演唱会/节假日商圈）。"
         "训练数据质量和密度远超通用基础模型。"),
    ]
    for code, title, desc in strengths:
        story.append(Paragraph(f"<b>{code}  {title}</b>", s["body"]))
        story.append(Paragraph(desc, s["bullet"]))
        story.append(Spacer(1, 0.05 * cm))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("挑战（Weaknesses & Risks）", s["section_header"]))
    weaknesses = [
        ("W/01", "高斯泼溅全国规模化",
         "采集车覆盖密度 × 算力 × 动态更新频率——三项成本叠加，短期难以全量铺开"),
        ("W/02", "Fantasy World 与地图事实对齐",
         "世界模型的三维推理结果需与高德地图实时数据严格融合，工程难度高"),
        ("W/03", "智驾生态弱",
         "车端数据与 OEM 协同深度不及百度 Apollo，高德在车机场景的渗透率仍低"),
        ("W/04", "VLM 室内场景覆盖",
         "室内场景图像-位置配对训练数据稀缺，VLM 室内定位精度仍是产品难点"),
    ]
    for code, title, desc in weaknesses:
        story.append(Paragraph(f"<b>{code}  {title}</b>  —  {desc}", s["body"]))

    story.append(Spacer(1, 0.2 * cm))
    story += conclusion_line(s,
        "高德的不对称优势：Fantasy World + 高斯泼溅 + VLM + 真实数据飞轮，"
        "四张牌同时在手，是行业唯一能做「真实世界3D路况建模」的玩家")

    # ─────────────────────────────────────────────────
    # SLIDE 10 – RoadMap  【改动】
    # 对应真实技术路线，三阶段视觉设计说明
    # Phase 1: 室内导航 + agent归因解释
    # Phase 2: 3D空间大范围铺开
    # Phase 3: 地震等灾难预演，城市级B端
    # ─────────────────────────────────────────────────
    story += slide_header(s, 10, "未来 RoadMap")

    story.append(Paragraph("▲ 内容更新：与高德真实技术路径对齐；HTML版将加入分阶段3D动效", s["diff_note"]))
    story.append(Spacer(1, 0.1 * cm))

    phases = [
        {
            "label": "PHASE 01",
            "timeframe": "0–12 个月",
            "theme": "近场可验证",
            "tagline": "让用户感受到「高德懂我在哪 + 懂我为什么」",
            "color": C_ORANGE,
            "tech_core": "Fantasy World 局部建模 · VLM 视觉锚定 · Qwen 解释生成 · 高斯泼溅枢纽三维",
            "products": [
                "室内连续导航：停车场/地铁站/商圈——高斯泼溅三维场景 + VLM 视觉定位，实现楼层级精准引导",
                "路线推荐归因解释：「为什么走这条路」→ Qwen 自然语言因果说明，建立用户信任",
                "Agent 归因解释卡片：每次导航推荐自动附带 1–2 句理由（首要原因 + 次要原因）",
            ],
            "metrics": "室内定位准确率 ↑  /  路线推荐采纳率 ↑  /  错过率 ↓",
            "visual_note": "【动效方向】平面地图 → 楼层级3D剖面展开动画；路线逐步点亮绘制",
        },
        {
            "label": "PHASE 02",
            "timeframe": "1–2 年",
            "theme": "3D空间智能铺开",
            "tagline": "城市核心枢纽全面三维化，主动出行规划落地",
            "color": C_TEAL,
            "tech_core": "大规模高斯泼溅部署 · Fantasy World 城市级建模 · Qwen 多模态 Agent",
            "products": [
                "城市核心区三维孪生：Top-100 枢纽（机场/高铁站/大型商圈）高斯泼溅三维场景上线",
                "主动出行规划 Agent：感知场景变化（演唱会/商场关闭/节假日高峰），提前推送规避路线",
                "AR 空间导航：手机相机画面实时叠加路径指引和空间标注",
                "车机-手机统一空间状态：多端共享同一三维场景模型，连续导航不断链",
            ],
            "metrics": "3D场景覆盖城市数 ↑  /  主动推送采纳率 ↑  /  ETA误差 ↓",
            "visual_note": "【动效方向】城市平面图 → 3D楼层爆炸展开 → 路径在三维空间中飞行绘制",
        },
        {
            "label": "PHASE 03",
            "timeframe": "2–3 年 +",
            "theme": "灾难预演 + 城市级智能",
            "tagline": "世界模型从「服务出行」升级为「服务城市安全与应急」",
            "color": C_NAVY,
            "tech_core": "Fantasy World 大规模仿真 · 多智能体协同 · 城市数字孪生平台",
            "products": [
                "极端事件推演：地震/洪水疏散路线实时重算，演唱会/大型活动散场分流预演",
                "城市级应急调度：政府/交管 B 端接口，基于 Fantasy World 提供路网状态预测与疏导建议",
                "低空三维空域：扩展世界模型至垂直维度，支持无人机配送和低空出行路径规划",
                "空间智能 API 生态：车企/机器人/城市治理平台接入高德三维世界模型能力",
            ],
            "metrics": "灾害预演准确率  /  B端接入量  /  API 调用量",
            "visual_note": "【动效方向】城市三维场景 → 灾难波纹动画扩散 → 逃生路径实时亮起（红→绿渐变）",
        },
    ]

    for p in phases:
        header_data = [[
            Paragraph(p["label"], s["route_label"]),
            Paragraph(p["timeframe"], s["route_label"]),
            Paragraph(p["theme"], s["route_label"]),
        ]]
        h_col_w = (PAGE_W - MARGIN_L - MARGIN_R) / 3
        header_tbl = Table(header_data, colWidths=[h_col_w] * 3)
        header_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), p["color"]),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(header_tbl)
        story.append(Paragraph(f"目标：{p['tagline']}", s["callout"]))
        story.append(Paragraph(f"技术核心：{p['tech_core']}", s["note"]))
        for b in p["products"]:
            story.append(bullet_item(s, b))
        story.append(Paragraph(f"指标：{p['metrics']}", s["callout_orange"]))
        story.append(Paragraph(p["visual_note"], s["note"]))
        story.append(Spacer(1, 0.25 * cm))

    story.append(Spacer(1, 0.2 * cm))
    summary_items = [
        "事实层  来自地图",
        "模型层  Fantasy World",
        "解释层  Qwen驱动",
        "执行层  可确认可回滚",
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
    # SLIDE 12 – 我的出行痛点  【改动】
    # 4层 → 3层（去掉 L/04 协同层）
    # L/02 路径层：商场关门/出口关闭/打车绕路 + 演唱会场景
    # L/03 决策层：崴脚找电梯出口
    # 5张图片占位（3张 位置层微信对话 + 2张 路径层打车绕路）
    # ─────────────────────────────────────────────────
    story += slide_header(s, 12, "我的出行痛点")

    story.append(Paragraph("▲ 内容更新：合并为3层（去掉协同层），更新具体场景，增加图片占位", s["diff_note"]))
    story.append(Spacer(1, 0.1 * cm))

    # L/01
    story.append(Paragraph("L/01  位置层", s["section_header"]))
    story.append(Paragraph(
        "场景：大商场里找朋友，地图显示「已到达」但彼此还是找不到。"
        "只能靠微信电话互相描述「我在优衣库旁边」「我在B1出口」……最后靠蒙。",
        s["body"]))
    story.append(Paragraph(
        "本质：二维坐标无法区分不同楼层和垂直空间；室内定位精度不足，「地图漂移」无处反馈。",
        s["callout"]))

    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph("图片占位（位置层）", s["label_tag"]))

    photo_row_1 = [
        [photo_placeholder_box(s, "截图1 — 微信对话：找朋友，互相描述位置")],
        [photo_placeholder_box(s, "截图2 — 微信对话：对方说「我在B1」但找不到")],
        [photo_placeholder_box(s, "截图3 — 地图显示「已到达」但实际位置偏差截图")],
    ]
    photo_tbl_1 = Table(photo_row_1, colWidths=[(PAGE_W - MARGIN_L - MARGIN_R - 0.4 * cm) / 3] * 3)
    photo_tbl_1.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 3),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 3),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(photo_tbl_1)
    story.append(Spacer(1, 0.25 * cm))

    # L/02
    story.append(Paragraph("L/02  路径层", s["section_header"]))
    story.append(Paragraph(
        "场景A：商场打烊前离开，导航推荐的地铁出口已关闭。"
        "但导航没有提前告知，叫了车出发后才发现大幅绕路。",
        s["body"]))
    story.append(Paragraph(
        "场景B：演唱会散场，3条出口都在陆续关闭，"
        "导航依然推荐人流最多的那条，完全没有场景感知。",
        s["body"]))
    story.append(Paragraph(
        "本质：系统不感知「场景状态变化」——路网动态约束（出口关闭/人流激增）无法实时融入导航决策。",
        s["callout"]))

    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph("图片占位（路径层）", s["label_tag"]))

    photo_row_2 = [
        [photo_placeholder_box(s, "截图4 — 打车绕路截图（出口关闭导致绕行）")],
        [photo_placeholder_box(s, "截图5 — 打车费用或地图截图（绕路明显）")],
    ]
    photo_tbl_2 = Table(photo_row_2, colWidths=[(PAGE_W - MARGIN_L - MARGIN_R - 0.4 * cm) / 2] * 2)
    photo_tbl_2.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 3),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 3),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(photo_tbl_2)
    story.append(Spacer(1, 0.25 * cm))

    # L/03
    story.append(Paragraph("L/03  决策层", s["section_header"]))
    story.append(Paragraph(
        "场景：崴脚之后，想走最省力的出口路线，但不知道哪个出口有电梯、哪个是最近的坡道。"
        "选了「最近」的出口，才发现全是楼梯，只能原路返回。",
        s["body"]))
    story.append(Paragraph(
        "本质：导航不理解用户的身体状态和个性化软约束；没有「结果预演」能力——"
        "无法提前告知「这条路需要上2段楼梯」。",
        s["callout"]))

    story += conclusion_line(s,
        "地图只懂路网拓扑，不懂空间；只服务平均人，不服务具体人在具体处境下的具体需求")

    # ─────────────────────────────────────────────────
    # SLIDE 13 – 解决方案  【改动】
    # 标题：「具体解决方案」
    # 对应3层（去掉协同层）
    # L/01：VLM + 高斯泼溅 → 实时3D路径导航
    # L/02：状态推演（演唱会/商场关门/灾难预演）→ 特定情况路径规划
    # L/03：个性化建议 + 因果解释
    # ─────────────────────────────────────────────────
    story += slide_header(s, 13, "具体解决方案")

    story.append(Paragraph("▲ 标题已更新；内容对应3层痛点，去掉协同层", s["diff_note"]))
    story.append(Spacer(1, 0.1 * cm))

    solutions = [
        {
            "layer": "L/01  位置层",
            "title": "VLM + 高斯泼溅 → 实时3D视觉定位与导航",
            "tech": ["VLM（视觉语言模型）：用手机摄像头拍摄周围环境，识别场景特征自动定位",
                     "高斯泼溅（Gaussian Splatting）：生成枢纽/商圈的三维场景，与VLM定位实时匹配",
                     "产品表达：AR导航 — 在手机相机画面直接叠加「往左走20m，3号店右转」"],
            "user_experience": "用户感受：「拍一下，告诉我在哪，然后直接带我走」",
            "color": C_ORANGE,
        },
        {
            "layer": "L/02  路径层",
            "title": "状态推演 → 特定场景动态路径规划",
            "tech": ["Fantasy World 情景推演引擎：基于历史数据+当前场景状态，预测未来路网变化",
                     "感知「场景触发器」：演唱会散场 / 商场出口关闭 / 节假日人流高峰 / 地震疏散",
                     "产品表达：散场前1小时推送预警 — 「X号出口将关闭，建议提前改走Y路线」",
                     "灾难预演：地震时实时重算疏散路线，排除已损毁路段"],
            "user_experience": "用户感受：「高德帮我想到了，我没想到的事」",
            "color": C_TEAL,
        },
        {
            "layer": "L/03  决策层",
            "title": "个性化因果推理 → 懂你处境的路线建议",
            "tech": ["感知用户状态：崴脚/轮椅/带小孩——从用户输入或历史行为推断",
                     "Qwen 多模态个性化推理：结合用户状态+当前场景，生成最优路径并附带因果解释",
                     "产品表达：「您选的出口需要上2段楼梯。根据您当前状态，建议改用C出口（有电梯，多走3分钟）」",
                     "降级通知：提前告知约束冲突，而不是让用户走到才发现"],
            "user_experience": "用户感受：「高德像一个懂我身体状态的朋友，而不是只管最短路线的机器」",
            "color": C_PURPLE,
        },
    ]

    col_ws = [2.2 * cm, 3.8 * cm, 4.5 * cm, 3.5 * cm]
    header_row = [
        Paragraph("痛点层", s["section_header"]),
        Paragraph("技术方案", s["section_header"]),
        Paragraph("产品实现", s["section_header"]),
        Paragraph("用户体验感知", s["section_header"]),
    ]
    sol_rows = [header_row]

    for sol in solutions:
        sol_rows.append([
            Paragraph(sol["layer"], s["body"]),
            [Paragraph(f"<b>{sol['title']}</b>", s["body"])] + [bullet_item(s, t) for t in sol["tech"][:2]],
            [bullet_item(s, t) for t in sol["tech"][2:]],
            Paragraph(sol["user_experience"], s["callout_orange"]),
        ])

    sol_tbl = Table(sol_rows, colWidths=col_ws)
    sol_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_NAVY),
        ("TEXTCOLOR",  (0, 0), (-1, 0), white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, C_LIGHT, HexColor("#fdf4ff")]),
        ("GRID", (0, 0), (-1, -1), 0.3, C_RULE),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(sol_tbl)

    story += conclusion_line(s,
        "三层痛点 × 三项技术能力（VLM定位 / 状态推演 / 因果解释）——"
        "高德世界模型不是概念PPT，而是有具体产品落脚点的技术路径")

    # ─────────────────────────────────────────────────
    # SLIDE 14 – 延展痛点  【改动】
    # 与高德/阿里实际数据/模型/技术资产绑定
    # ─────────────────────────────────────────────────
    story += slide_header(s, 14, "延展痛点：未来可能衍生的方向")

    story.append(Paragraph("▲ 内容更新：与高德真实技术资产明确绑定", s["diff_note"]))
    story.append(Spacer(1, 0.1 * cm))

    extensions = [
        {
            "num": "01",
            "title": "AR眼镜时代，导航的下一代形态",
            "desc": "从「低头看屏幕」到「抬头看世界」——路口标识与入口指引叠加在真实视野中。"
                    "高德世界模型成为AR眼镜的空间理解引擎，解决「现实空间里找到目标位置」的根本需求。",
            "tech_assets": [
                "Fantasy World：提供三维空间理解与坐标对齐",
                "高斯泼溅：真实场景三维重建，AR渲染底座",
                "VLM：实时视觉定位，AR锚定精度保障",
            ],
            "biz": "新终端入口 · 阿里AI眼镜生态协同（对标Meta Glasses战略布局）",
        },
        {
            "num": "02",
            "title": "低空经济，三维空域的数字底座",
            "desc": "eVTOL、无人机配送、空中出租车——低空经济开启垂直维度出行。"
                    "高德已布局低空数字地图，世界模型需要从二维路网延伸到三维立体空域。",
            "tech_assets": [
                "高德低空数字地图：已有垂直空域基础数据",
                "Fantasy World：扩展三维建模至50m–1000m垂直范围",
                "状态推演：空中交通流量预测 + 空地协同路径规划",
            ],
            "biz": "阿里低空战略协同 · 城市三维导航新入口（地面+低空一体化）",
        },
        {
            "num": "03",
            "title": "多人出行Agent，家庭与社交协同",
            "desc": "家庭出行、团建、约会场景——多用户的位置、偏好、约束需要统一调度。"
                    "不再是「各自看各自的地图」，而是共享同一空间状态做协同决策。",
            "tech_assets": [
                "Qwen 多模态 Agent：理解多用户偏好与约束",
                "VLM 多人定位：在同一三维场景中追踪多用户位置",
                "Fantasy World：共享空间状态即共享决策模型",
            ],
            "biz": "从「工具」到「家庭出行协同平台」· 微信社交场景防御",
        },
        {
            "num": "04",
            "title": "城市级灾难预演与应急调度",
            "desc": "地震/洪水/大型活动应急——需要实时重算疏散路线、协调交通管控。"
                    "这是「世界模型」从消费产品升级为城市基础设施的关键跃迁。",
            "tech_assets": [
                "Fantasy World 大规模仿真：城市级路网状态推演",
                "Qwen 因果推理：多因素权衡（已损毁路段/人流密度/医疗资源）",
                "高德170M DAU数据：真实人口流动做推演底座",
            ],
            "biz": "政府/交管 B端接口 · 集团城市治理战略 · 阿里云城市大脑延伸",
        },
    ]

    for item in extensions:
        story.append(Paragraph(f"  {item['num']}  {item['title']}", s["section_header"]))
        story.append(Paragraph(item["desc"], s["body"]))
        story.append(Paragraph("技术资产绑定：", s["label_tag"]))
        for asset in item["tech_assets"]:
            story.append(bullet_item(s, asset, indent=1))
        story.append(Paragraph(f"商业逻辑：{item['biz']}", s["callout"]))
        story.append(Spacer(1, 0.2 * cm))

    story.append(rule(C_NAVY, thickness=1.5, spaceBefore=10, spaceAfter=6))
    story.append(Paragraph(
        "总结：我的痛点是入口，真正的产品机会是把高德从「导航工具」升级为"
        "「可推演真实世界变化的空间智能平台」——"
        "Fantasy World + 高斯泼溅 + VLM + Qwen，四件套齐，只等产品落地。",
        s["conclusion"]))

    return story


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    output_path = "/home/user/air/presentation-content-v2.pdf"
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN_L,
        rightMargin=MARGIN_R,
        topMargin=MARGIN_T,
        bottomMargin=MARGIN_B,
        title="高德 × 世界模型 — 内容改稿 v2（PDF草稿）",
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
