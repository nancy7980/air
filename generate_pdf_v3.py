#!/usr/bin/env python3
"""
PDF 改稿 v3：
- S5  去掉数字孪生 vs 仿真模拟对比表（内部参考用，不入 PPT）
- S9  优势改为战略视角（非技术名词堆砌），经验证后再写入
- S10 RoadMap 大幅减字
- 全文减少 Fantasy World / 高斯泼溅 / VLM / Qwen 重复次数
不动 presentation.html，不推送 GitHub
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# ── Font ──────────────────────────────────────────────────────────────────────
FONT_NAME = "WQYZenHei"
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
try:
    pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH, subfontIndex=0))
    print(f"Font: {FONT_NAME}")
except Exception as e:
    print(f"Font fallback: {e}"); FONT_NAME = "Helvetica"

# ── Colors ────────────────────────────────────────────────────────────────────
C_NAVY   = HexColor("#1a2744")
C_BLUE   = HexColor("#2563eb")
C_TEAL   = HexColor("#0891b2")
C_ORANGE = HexColor("#ea580c")
C_LIGHT  = HexColor("#f0f4ff")
C_GRAY   = HexColor("#6b7280")
C_RULE   = HexColor("#cbd5e1")
C_GREEN  = HexColor("#059669")
C_PURPLE = HexColor("#7c3aed")
C_AMBER  = HexColor("#d97706")

# ── Page ──────────────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4
ML, MR, MT, MB = 2.2*cm, 2.2*cm, 2.0*cm, 2.0*cm
CW = PAGE_W - ML - MR  # content width

# ── Styles ────────────────────────────────────────────────────────────────────
def make_styles():
    def ps(name, **kw):
        kw.setdefault("fontName", FONT_NAME)
        return ParagraphStyle(name, **kw)

    return {
        "cover_title":  ps("ct", fontSize=28, leading=36, textColor=C_NAVY, spaceAfter=8, alignment=TA_CENTER),
        "cover_sub":    ps("cs", fontSize=14, leading=20, textColor=C_BLUE, spaceAfter=6, alignment=TA_CENTER),
        "cover_tag":    ps("cg", fontSize=11, leading=16, textColor=C_GRAY, spaceAfter=4, alignment=TA_CENTER),
        "ch_label":     ps("cl", fontSize=9,  leading=12, textColor=white, spaceBefore=18, spaceAfter=4),
        "ch_title":     ps("cht", fontSize=18, leading=24, textColor=white, spaceAfter=6),
        "ch_sub":       ps("chs", fontSize=10, leading=14, textColor=HexColor("#bfdbfe"), spaceAfter=0),
        "slide_num":    ps("sn", fontSize=9,  leading=12, textColor=C_ORANGE, spaceAfter=2),
        "slide_title":  ps("st", fontSize=16, leading=22, textColor=C_NAVY, spaceBefore=20, spaceAfter=6),
        "sec":          ps("sh", fontSize=12, leading=16, textColor=C_TEAL, spaceBefore=10, spaceAfter=4),
        "body":         ps("b",  fontSize=10, leading=15, textColor=C_GRAY, spaceAfter=4),
        "bullet":       ps("bu", fontSize=10, leading=15, textColor=C_GRAY, leftIndent=14, spaceAfter=3),
        "sub_bullet":   ps("sb", fontSize=9,  leading=13, textColor=C_GRAY, leftIndent=28, spaceAfter=2),
        "lbl":          ps("lb", fontSize=9,  leading=12, textColor=white),
        "callout":      ps("ca", fontSize=10, leading=15, textColor=C_NAVY, spaceBefore=6, spaceAfter=4),
        "callout_o":    ps("co", fontSize=10, leading=15, textColor=C_ORANGE, spaceBefore=4, spaceAfter=4),
        "note":         ps("nt", fontSize=9,  leading=13, textColor=C_AMBER, spaceBefore=3, spaceAfter=3, leftIndent=8),
        "conclusion":   ps("cn", fontSize=10, leading=15, textColor=C_ORANGE, spaceBefore=8, spaceAfter=4),
        "toc_item":     ps("ti", fontSize=12, leading=18, textColor=C_NAVY, spaceAfter=6, leftIndent=10),
        "toc_desc":     ps("td", fontSize=10, leading=14, textColor=C_GRAY, spaceAfter=8, leftIndent=10),
        "summary_box":  ps("sm", fontSize=10, leading=15, textColor=C_NAVY, spaceAfter=4),
        "photo":        ps("ph", fontSize=9,  leading=13, textColor=HexColor("#9ca3af"), spaceAfter=4, alignment=TA_CENTER),
        "diff":         ps("df", fontSize=9,  leading=13, textColor=C_GREEN, spaceBefore=2, spaceAfter=4, leftIndent=6),
    }


# ── Helpers ───────────────────────────────────────────────────────────────────
def rule(color=C_RULE, t=0.5, sb=4, sa=6):
    return HRFlowable(width="100%", thickness=t, color=color, spaceAfter=sa, spaceBefore=sb)

def chapter_block(s, num, title, sub):
    data = [[Paragraph(f"CHAPTER {num}", s["ch_label"])],
            [Paragraph(title, s["ch_title"])],
            [Paragraph(sub, s["ch_sub"])]]
    tbl = Table(data, colWidths=[CW])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), C_NAVY),
        ("TOPPADDING",(0,0),(-1,-1),10), ("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("LEFTPADDING",(0,0),(-1,-1),16), ("RIGHTPADDING",(0,0),(-1,-1),16),
    ]))
    return [Spacer(1, 0.3*cm), tbl, Spacer(1, 0.4*cm)]

def slide_header(s, num, title):
    return [
        Paragraph(f"SLIDE {num}", s["slide_num"]),
        Paragraph(title, s["slide_title"]),
        rule(C_BLUE, t=1.5, sb=2, sa=8),
    ]

def bi(s, text, sub=False):
    return Paragraph(f"• {text}", s["sub_bullet"] if sub else s["bullet"])

def conclusion_line(s, text):
    return [rule(C_ORANGE, t=0.8, sb=10, sa=4), Paragraph(f"结论：{text}", s["conclusion"])]

def badge_row(s, code, title, desc, color):
    row = Table([[Paragraph(code, s["lbl"]),
                  Paragraph(f"<b>{title}</b>  —  {desc}", s["body"])]],
                colWidths=[1.6*cm, CW-1.6*cm])
    row.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,0),color),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("TOPPADDING",(0,0),(-1,-1),4), ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),6), ("RIGHTPADDING",(0,0),(-1,-1),6),
    ]))
    return row

def photo_box(s, label):
    tbl = Table([[Paragraph(f"[ 图片占位 — {label} ]", s["photo"])]],
                colWidths=[CW - 0.8*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),HexColor("#f3f4f6")),
        ("TOPPADDING",(0,0),(-1,-1),12), ("BOTTOMPADDING",(0,0),(-1,-1),12),
        ("LEFTPADDING",(0,0),(-1,-1),8), ("RIGHTPADDING",(0,0),(-1,-1),8),
        ("BOX",(0,0),(-1,-1),0.5,C_RULE),
    ]))
    return tbl


# ── Story ─────────────────────────────────────────────────────────────────────
def build_story(s):
    story = []

    # ── S1 COVER ──────────────────────────────────────────────────────────────
    story += [
        Spacer(1, 1.5*cm),
        Paragraph("高德 × 世界模型", s["cover_title"]),
        Paragraph("空间智能时代的产品思考", s["cover_sub"]),
        Spacer(1, 0.4*cm),
        rule(C_BLUE, t=2, sb=0, sa=10),
        Paragraph("行业技术研判 · 高德战略机会 · 用户痛点洞察", s["cover_tag"]),
        Spacer(1, 1.5*cm),
    ]

    # ── S2 目录 ───────────────────────────────────────────────────────────────
    story += slide_header(s, 2, "目录")
    for num_t, desc in [
        ("01  行业发展分析", "技术路线 · 应用痛点 · 竞合格局"),
        ("02  高德 × 世界模型", "痛点机会 · 优势劣势 · 落地节奏"),
        ("03  用户视角", "出行痛点 · 解法对应 · 未来延展"),
    ]:
        story += [Paragraph(num_t, s["toc_item"]), Paragraph(desc, s["toc_desc"])]
    story.append(Spacer(1, 0.5*cm))

    # ── CHAPTER 1 ─────────────────────────────────────────────────────────────
    story += chapter_block(s, 1, "世界模型行业发展分析",
                           "先判断技术路线与行业格局，再判断高德该如何落地")

    # ── S4 技术路线 ────────────────────────────────────────────────────────────
    # 改动：3D路线引入高德空间建模能力；交互路线去掉 Scenario Lab 名称
    story += slide_header(s, 4, "世界模型当前的技术路线")

    routes = [
        ("01", "视频生成路线", "(Sora · Veo)", C_ORANGE,
         ["从海量视频学习光影、材质与场景连续性，画面高度逼真。",
          "但对因果关系理解薄弱——「看起来真」≠「可用于决策」。"],
         "高德切入：路线预览与解释层，不替代地图事实"),
        ("02", "3D空间智能路线", "(World Labs · Marble)", C_TEAL,
         ["生成可探索、具备三维一致性的空间模型，支持多视角与室内外连续导航。",
          "高德已积累三维空间建模能力，在停车场、重点路口完成局部场景验证。",
          "挑战：全国规模化采集成本高，动态人流实时更新是工程难点。"],
         "高德切入：以真实3D路况数据为底座，优先覆盖地铁站、商圈、停车场等高频枢纽"),
        ("03", "交互环境路线", "(Genie · SIMA)", C_PURPLE,
         ["在可交互环境中训练智能体，通过「动作→后果」学习策略。",
          "适合验证极端场景（演唱会散场/地震疏散），但迁移真实道路需严格地图约束。"],
         "高德切入：自研情景推演引擎，构建极端场景用于导航策略仿真评测与主动预警"),
        ("04", "JEPA抽象状态路线", "(V-JEPA 2)", C_NAVY,
         ["预测高维抽象状态而非像素，更接近对世界的真实「理解」。",
          "利于长时序规划与可解释决策，但不直接输出可展示画面。"],
         "高德切入：路线风险预测、动态分流与可解释决策内核"),
    ]

    for num, title, sub, color, bullets, cutpoint in routes:
        story.append(Paragraph(f"0{num} / {title}  {sub}", s["sec"]))
        for b in bullets:
            story.append(bi(s, b))
        story.append(Paragraph(f"→ {cutpoint}", s["callout"]))
        story.append(Spacer(1, 0.2*cm))

    story += conclusion_line(s, "视频真实感只是表层；地图对齐、行动后果、可解释性才是高德的核心")

    # ── S5 切入点 ──────────────────────────────────────────────────────────────
    # 改动：去掉数字孪生 vs 仿真模拟对比表；保留四个应用机会
    story += slide_header(s, 5, "世界模型应用的切入点")

    story.append(Paragraph(
        "注：数字孪生（知道现在是什么状态）与仿真模拟（推演如果…会怎样）是递进关系，"
        "两者并非同类，仿真需以孪生为底座。以下四个切入方向按时间节奏排列。",
        s["note"]))
    story.append(Spacer(1, 0.1*cm))

    opps = [
        ("智能交互", "SHORT-TERM", C_ORANGE,
         "用户真实需求往往包含多个约束：顺路接人、避堵、带小孩……当前系统只能逐一回答，无法给出综合最优方案。",
         "小高老师多约束规划 · 路线解释 · 临时改计划"),
        ("数字孪生", "MID-TERM", C_TEAL,
         "路口/商圈/停车场的状态是动态的——施工封道、人流聚集、出口临时关闭，难以实时融入地图底座。",
         "高频枢纽局部实时孪生（停车场/地铁站/商圈）"),
        ("仿真模拟", "MID-TERM", C_PURPLE,
         "导航策略上线前极难覆盖长尾极端场景（演唱会散场/临时封道/极端天气），线上暴露代价极高。",
         "极端场景预演 · 导航策略评测 · 应急路径规划"),
        ("决策支持", "LONG-TERM", C_NAVY,
         "ETA预测与绕行推荐对用户是黑盒——用户不理解为什么走这条路，信任低、采纳率低。",
         "可解释分流策略 · 城市级事件推演 · 应急调度"),
    ]

    for title, horizon, color, pain, solution in opps:
        badge = Table([[Paragraph(f"{title}  [{horizon}]", s["lbl"])]],
                      colWidths=[None])
        badge.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),color),
            ("TOPPADDING",(0,0),(-1,-1),3), ("BOTTOMPADDING",(0,0),(-1,-1),3),
            ("LEFTPADDING",(0,0),(-1,-1),8), ("RIGHTPADDING",(0,0),(-1,-1),8),
        ]))
        story.append(badge)
        story.append(bi(s, pain))
        story.append(Paragraph(f"切口：{solution}", s["callout"]))
        story.append(Spacer(1, 0.2*cm))

    story += conclusion_line(s, "先做近场高频可量化，再扩城市级生态")

    # ── S6 竞合关系 ────────────────────────────────────────────────────────────
    # 改动：重构为生态格局/竞合关系；注明建议版面移至 Chapter 2
    story += slide_header(s, 6, "行业生态格局与竞合关系")

    story.append(Paragraph(
        "【版面建议】本页适合移至 Chapter 2，置于 SWOT 之后、RoadMap 之前。"
        "Google Maps 在中国不可用；百度 Apollo 主定位自动驾驶 B2B，与高德 C 端赛道差异明显——"
        "建议用「竞合关系」取代简单竞品对比。",
        s["note"]))
    story.append(Spacer(1, 0.15*cm))

    ecosystem = [
        ("Google Maps", "全球技术标杆（非直接竞争）", C_BLUE,
         ["Immersive View、AR导航——视觉体验全球领先；在中国受监管限制不可用。",
          "对高德的意义：3D/AR方向的技术参照系，而非用户竞争对手。"],
         "参照系：高德 3D 体验缺口有多大，对着 Google 的节奏判断"),
        ("百度地图 + Apollo", "直接竞争（C端） + 智驾深耕（B端）", C_ORANGE,
         ["百度地图：中国C端导航直接竞对，市占约 30–40%（高德约 50%+）。",
          "百度 Apollo：已与吉利、长城、比亚迪等多家车企签约，OEM智驾 B2B 路径成熟。",
          "根本差异：Apollo 主打车端；高德主打手机端用户出行。"],
         "竞合关系：地图C端直接竞争；智驾B端路线不同，暂无正面冲突"),
        ("腾讯地图", "C端竞争者（微信生态）", C_TEAL,
         ["依托微信入口，社交+位置场景天然耦合；技术积累相对薄弱。"],
         "直接竞争：社交场景中的位置分享与多人协同"),
        ("高德 Amap", "中国出行数据最强 · 阿里生态协同", C_GREEN,
         ["170M+ DAU，中国实时交通数据覆盖最全，是行业内无可复制的数据壁垒。",
          "背靠阿里AI基础设施与全域生态（本地生活/支付/电商），商业闭环完整。",
          "已建立三维空间建模能力积累，并具备大模型资源直连优势。"],
         "优势：数据 + AI基础设施 + 阿里生态  /  缺口：3D体验、智驾深度"),
    ]

    for name, type_, color, bullets, relation in ecosystem:
        story.append(Paragraph(f"{name}  —  {type_}", s["sec"]))
        for b in bullets:
            story.append(bi(s, b))
        story.append(Paragraph(f"→ {relation}", s["callout"]))
        story.append(Spacer(1, 0.15*cm))

    # matrix
    story.append(Paragraph("竞合矩阵", s["sec"]))
    mdata = [
        [Paragraph(h, s["sec"]) for h in ["维度", "Google Maps", "百度Apollo", "腾讯地图", "高德"]],
        [Paragraph(c, s["body"]) for c in ["中国C端用户", "✗ 不可用", "●● 地图竞争", "●● 微信入口", "●●● 最强"]],
        [Paragraph(c, s["body"]) for c in ["3D/AR体验", "●●● 标杆", "●", "●", "● 缺口"]],
        [Paragraph(c, s["body"]) for c in ["智驾/车路协同", "●", "●●● Apollo", "●", "● 待建"]],
        [Paragraph(c, s["body"]) for c in ["AI基础设施", "Google AI", "百度大模型", "腾讯混元", "阿里AI生态"]],
        [Paragraph(c, s["body"]) for c in ["商业生态", "Google全球", "智驾OEM", "微信社交", "阿里全域"]],
    ]
    col5 = CW / 5
    mtbl = Table(mdata, colWidths=[col5]*5)
    mtbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),C_NAVY), ("TEXTCOLOR",(0,0),(-1,0),white),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[white, C_LIGHT]),
        ("GRID",(0,0),(-1,-1),0.3,C_RULE),
        ("TOPPADDING",(0,0),(-1,-1),4), ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),4), ("RIGHTPADDING",(0,0),(-1,-1),4),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"), ("FONTSIZE",(0,0),(-1,-1),8),
    ]))
    story.append(mtbl)
    story += conclusion_line(s,
        "Google定义3D方向标；百度Apollo深耕智驾B端；高德的不对称机会：中国数据最密处，率先建立仿真推演层+可解释层")

    # ── CHAPTER 2 ─────────────────────────────────────────────────────────────
    story += chapter_block(s, 2, "高德 × 世界模型",
                           "从行业判断，推导高德专属的产品机会与战略节奏")

    # ── S8 为什么做世界模型 ────────────────────────────────────────────────────
    # 改动：用产品框架语言，四个结构性能力缺口
    story += slide_header(s, 8, "高德·为什么做世界模型")

    gaps = [
        ("P/01", "感知层断层", C_ORANGE,
         "室内外定位切换断裂：GPS精度2–10m，无楼层感知；视觉环境与坐标脱节，复杂枢纽内「地图漂移」",
         "最后100m失效，室内导航完全靠人工描述"),
        ("P/02", "理解层黑盒", C_BLUE,
         "ETA预测与绕行策略缺乏因果链说明；系统默认「最优解」无法被用户理解和信任",
         "路线推荐采纳率低，用户信任损失积累"),
        ("P/03", "状态层滞后", C_TEAL,
         "施工封道、活动人流、临时出口关闭——数据更新延迟数小时到数天；现有地图是「过去的快照」",
         "极端场景下导航失效，用户信任关键损失节点"),
        ("P/04", "情境层缺失", C_PURPLE,
         "不区分用户身体状态（崴脚/轮椅/推婴儿车）；不感知场景变化（演唱会散场/商场出口关闭）",
         "个性化导航机会完全缺失，系统服务「平均人」不服务「具体人」"),
    ]

    for code, title, color, problem, impact in gaps:
        row = Table([[Paragraph(f"{code}\n{title}", s["lbl"]),
                      [Paragraph(problem, s["body"]),
                       Paragraph(f"影响：{impact}", s["callout_o"])]]],
                    colWidths=[2.0*cm, CW-2.0*cm])
        row.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(0,0),color),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("TOPPADDING",(0,0),(-1,-1),6), ("BOTTOMPADDING",(0,0),(-1,-1),6),
            ("LEFTPADDING",(0,0),(-1,-1),6), ("RIGHTPADDING",(0,0),(-1,-1),8),
        ]))
        story.append(row)
        story.append(Spacer(1, 0.12*cm))

    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("机会（Opportunities）", s["sec"]))
    opps_b = [
        ("O/01", "空间感知连续化", C_GREEN,   "AR入口确认 + 室内外无缝定位"),
        ("O/02", "推荐可解释化",   C_TEAL,    "把路线推荐理由用自然语言「说出来」"),
        ("O/03", "状态动态化",     C_BLUE,    "提前感知场景变化，主动响应而非被动更新"),
        ("O/04", "情境个性化",     C_ORANGE,  "服务具体人的具体约束，而非平均最优解"),
    ]
    for code, title, color, desc in opps_b:
        story.append(badge_row(s, code, title, desc, color))
        story.append(Spacer(1, 0.08*cm))

    story += conclusion_line(s,
        "四个结构性缺口——感知断层、理解黑盒、状态滞后、情境缺失——正是世界模型能填补的空间")

    # ── S9 优势和挑战 ──────────────────────────────────────────────────────────
    # 改动：优势改为战略视角，经验证后写入；减少技术名词堆砌
    # 注：以下优势均有公开来源或行业验证支撑（数据规模/阿里生态/产品积累）
    story += slide_header(s, 9, "高德×世界模型·优势和挑战")

    story.append(Paragraph("优势（Strengths）", s["sec"]))

    strengths = [
        ("S/01", "中国出行数据壁垒", C_GREEN,
         "170M+ DAU + 实时路况 + 200M+ POI——规模和密度是行业天花板。"
         "这不是靠钱能短期堆出来的，是十余年用户积累形成的飞轮。"
         "Google在中国无法运营，百度地图数据规模落后，腾讯地图缺乏深度交通数据。"),
        ("S/02", "背靠阿里，AI能力不靠外采", C_TEAL,
         "直连阿里大模型（通义千问系列），阿里云提供算力支撑，无需依赖第三方 API 或支付高昂调用成本。"
         "这是 AI 时代「有粮有兵」的结构性优势——独立导航公司根本没有这个条件。"),
        ("S/03", "阿里全域商业生态闭环", C_BLUE,
         "导航 → 本地生活（饿了么/口碑）→ 支付（支付宝）→ 电商（淘宝/天猫）。"
         "高德是阿里全域流量的空间入口，商业转化链路完整。"
         "竞争对手只有「地图」，高德背后有整条消费链路。"),
        ("S/04", "本土高频场景的独特训练信号", C_PURPLE,
         "中国特有的出行场景密度：春运、演唱会散场、节假日商圈、高密度城市路网。"
         "这些场景的数据多样性和极端情况覆盖，是国际模型无法获得的训练素材。"),
        ("S/05", "三维空间建模能力积累", C_ORANGE,
         "已在停车场、重点路口等局部场景完成三维建模验证，具备从点到面扩展的能力基础。"
         "叠加阿里 AI 视觉能力，室内外空间理解有技术路径支撑——"
         "而非从零开始。"),
    ]

    for code, title, color, desc in strengths:
        story.append(Paragraph(f"<b>{code}  {title}</b>", s["body"]))
        story.append(Paragraph(desc, s["bullet"]))
        story.append(Spacer(1, 0.05*cm))

    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("挑战（Weaknesses & Risks）", s["sec"]))
    weaknesses = [
        ("W/01", "3D体验缺口",      "与 Google Immersive View 相比，沉浸式三维体验差距明显，短期难以追平"),
        ("W/02", "车端整合深度弱",  "在 OEM 智驾合作层面远不及百度 Apollo，车机场景渗透率有限"),
        ("W/03", "室内场景数据稀缺","商场/枢纽室内图覆盖率不足，视觉定位训练数据需大规模采集"),
        ("W/04", "规模化工程难度",  "三维建模大范围铺开，采集成本 × 算力 × 动态更新频率三项叠加"),
    ]
    for code, title, desc in weaknesses:
        story.append(Paragraph(f"<b>{code}  {title}</b>  —  {desc}", s["body"]))

    story.append(Spacer(1, 0.2*cm))
    story += conclusion_line(s,
        "不做全球3D、不追赶智驾。做中国出行链路上数据最密、生态最全的空间智能平台——"
        "这是高德独有的不对称优势。")

    # ── S10 RoadMap ────────────────────────────────────────────────────────────
    # 改动：大幅减字，保留核心；附注 HTML 动效方向
    story += slide_header(s, 10, "未来 RoadMap")

    phases = [
        {
            "label": "PHASE 01", "time": "0–12 个月", "theme": "近场可验证",
            "color": C_ORANGE,
            "bullets": [
                "室内连续导航：停车场 / 地铁站 / 商圈楼层级精准引导",
                "路线推荐归因解释：每次导航附带 1–2 句理由，建立用户信任",
                "复杂路口风险解释：「前方路口事故，预计延误 8 分钟，建议绕行 X 路」",
            ],
            "metric": "室内定位准确率 ↑  ·  路线推荐采纳率 ↑  ·  错过率 ↓",
            "anim":   "动效：平面地图 → 楼层剖面展开 → 路径逐步点亮",
        },
        {
            "label": "PHASE 02", "time": "1–2 年", "theme": "3D空间铺开",
            "color": C_TEAL,
            "bullets": [
                "Top-100 核心枢纽（机场/高铁站/大型商圈）三维场景上线",
                "主动出行规划：感知场景变化（演唱会/商场关闭），提前推送规避路线",
                "AR 空间导航：手机相机画面实时叠加路径指引",
            ],
            "metric": "3D场景覆盖城市数 ↑  ·  主动推送采纳率 ↑  ·  ETA 误差 ↓",
            "anim":   "动效：城市平面图 → 3D 楼层爆炸展开 → 路径在空间中飞行绘制",
        },
        {
            "label": "PHASE 03", "time": "2–3 年+", "theme": "灾难预演 · 城市级",
            "color": C_NAVY,
            "bullets": [
                "极端事件推演：地震/洪水疏散路线实时重算，大型活动散场分流预演",
                "城市级应急调度：政府/交管 B 端接口，路网状态预测与疏导建议",
                "空间智能 API：车企/机器人/城市治理平台接入能力",
            ],
            "metric": "灾害预演准确率  ·  B端接入量  ·  API 调用量",
            "anim":   "动效：城市三维场景 → 灾难波纹扩散 → 逃生路径实时亮起（红→绿）",
        },
    ]

    for p in phases:
        hdata = [[Paragraph(p["label"], s["lbl"]),
                  Paragraph(p["time"], s["lbl"]),
                  Paragraph(p["theme"], s["lbl"])]]
        htbl = Table(hdata, colWidths=[CW/3]*3)
        htbl.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),p["color"]),
            ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),8), ("RIGHTPADDING",(0,0),(-1,-1),8),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ]))
        story.append(htbl)
        for b in p["bullets"]:
            story.append(bi(s, b))
        story.append(Paragraph(f"指标：{p['metric']}", s["callout"]))
        story.append(Paragraph(f"【HTML动效参考】{p['anim']}", s["note"]))
        story.append(Spacer(1, 0.25*cm))

    smdata = [[Paragraph(item, s["summary_box"]) for item in
               ["事实层  来自地图", "模型层  阿里AI基础设施", "解释层  大模型驱动", "执行层  可确认可回滚"]]]
    smtbl = Table(smdata, colWidths=[CW/4]*4)
    smtbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),C_LIGHT),
        ("GRID",(0,0),(-1,-1),0.5,C_RULE),
        ("TOPPADDING",(0,0),(-1,-1),8), ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("LEFTPADDING",(0,0),(-1,-1),6), ("RIGHTPADDING",(0,0),(-1,-1),6),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
    ]))
    story.append(smtbl)

    # ── CHAPTER 3 ─────────────────────────────────────────────────────────────
    story += chapter_block(s, 3, "用户视角的优化思路",
                           "从亲身出行体验出发，看高德与世界模型的真实结合点")

    # ── S12 我的出行痛点 ───────────────────────────────────────────────────────
    # 改动：4层→3层（去掉协同层）；更新场景；5个图片占位
    story += slide_header(s, 12, "我的出行痛点")

    # L/01
    story.append(Paragraph("L/01  位置层", s["sec"]))
    story.append(Paragraph(
        "场景：大商场里找朋友，地图显示「已到达」但彼此还是找不到。"
        "只能靠微信电话互相描述「我在优衣库旁边」「我在B1出口」……最后靠蒙。",
        s["body"]))
    story.append(Paragraph(
        "本质：二维坐标无法区分楼层；室内定位精度不足，「地图漂移」无处反馈。",
        s["callout"]))
    story.append(Spacer(1, 0.1*cm))

    # 3 photo placeholders
    pw3 = (CW - 0.4*cm) / 3
    ptbl3 = Table([
        [photo_box(s, "截图1 — 微信对话：互相描述位置"),
         photo_box(s, "截图2 — 微信对话：「我在B1」但找不到"),
         photo_box(s, "截图3 — 地图「已到达」但位置偏差")]
    ], colWidths=[pw3]*3)
    ptbl3.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),3), ("RIGHTPADDING",(0,0),(-1,-1),3),
        ("TOPPADDING",(0,0),(-1,-1),3), ("BOTTOMPADDING",(0,0),(-1,-1),3),
    ]))
    story.append(ptbl3)
    story.append(Spacer(1, 0.2*cm))

    # L/02
    story.append(Paragraph("L/02  路径层", s["sec"]))
    story.append(Paragraph(
        "场景A：商场打烊前离开，导航推荐的地铁出口已关——未提前告知，叫车出发后才发现大幅绕路。",
        s["body"]))
    story.append(Paragraph(
        "场景B：演唱会散场，出口陆续关闭，导航依然推荐人流最多的那条，没有任何场景感知。",
        s["body"]))
    story.append(Paragraph(
        "本质：系统不感知「场景状态变化」——路网动态约束无法实时融入导航决策。",
        s["callout"]))
    story.append(Spacer(1, 0.1*cm))

    # 2 photo placeholders
    pw2 = (CW - 0.3*cm) / 2
    ptbl2 = Table([
        [photo_box(s, "截图4 — 打车绕路截图（出口关闭导致绕行）"),
         photo_box(s, "截图5 — 打车费用或地图截图（绕路对比）")]
    ], colWidths=[pw2]*2)
    ptbl2.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),3), ("RIGHTPADDING",(0,0),(-1,-1),3),
        ("TOPPADDING",(0,0),(-1,-1),3), ("BOTTOMPADDING",(0,0),(-1,-1),3),
    ]))
    story.append(ptbl2)
    story.append(Spacer(1, 0.2*cm))

    # L/03
    story.append(Paragraph("L/03  决策层", s["sec"]))
    story.append(Paragraph(
        "场景：崴脚后想走最省力的出口，不知道哪个有电梯。"
        "选了「最近」的出口，走到才发现全是楼梯，只能原路返回。",
        s["body"]))
    story.append(Paragraph(
        "本质：导航不理解用户的身体状态与软约束；没有「结果预演」能力——"
        "无法提前告知「这条路需要上2段楼梯」。",
        s["callout"]))

    story += conclusion_line(s, "地图只懂路网，不懂空间；只服务平均人，不服务具体人在具体处境下的具体需求")

    # ── S13 具体解决方案 ───────────────────────────────────────────────────────
    # 改动：标题更新；三层对应；VLM/高斯泼溅/Qwen 各出现一次
    story += slide_header(s, 13, "具体解决方案")

    story.append(Paragraph(
        "三层痛点 × 三项技术能力，从感知→路径→决策逐层击穿。",
        s["note"]))
    story.append(Spacer(1, 0.1*cm))

    solutions = [
        {
            "layer": "L/01  位置层",
            "solution": "视觉定位 + 三维场景匹配 → 实时3D导航",
            "color": C_ORANGE,
            "tech": [
                "VLM（视觉语言模型）：拍摄周围环境，识别场景特征自动定位，精度达楼层级",
                "高斯泼溅（Gaussian Splatting）：生成枢纽/商圈三维场景，与视觉定位实时匹配",
                "产品表达：AR导航——相机画面直接叠加「往左走20m，3号店右转」",
            ],
            "ue": "用户感受：「拍一下，告诉我在哪，然后直接带我走」",
        },
        {
            "layer": "L/02  路径层",
            "solution": "状态推演 → 特定场景动态路径规划",
            "color": C_TEAL,
            "tech": [
                "情景推演引擎：基于历史数据+当前场景状态，预测路网变化",
                "场景触发器：演唱会散场 / 商场出口关闭 / 节假日高峰 / 地震疏散",
                "产品表达：散场前1小时推送「X号出口将关闭，建议改走Y路线」",
            ],
            "ue": "用户感受：「高德帮我想到了，我没想到的事」",
        },
        {
            "layer": "L/03  决策层",
            "solution": "个性化因果推理 → 懂你处境的路线建议",
            "color": C_PURPLE,
            "tech": [
                "感知用户状态：崴脚/轮椅/带小孩——从输入或历史行为推断",
                "Qwen 多模态推理：结合用户状态+当前场景，生成最优路径并附带因果解释",
                "产品表达：「C出口有电梯，多走3分钟，根据您当前状态建议改走」",
            ],
            "ue": "用户感受：「像一个懂我身体状态的朋友，不是只管最短路线的机器」",
        },
    ]

    col_ws = [2.0*cm, 4.0*cm, 4.5*cm, 3.2*cm]
    hrow = [Paragraph(h, s["sec"]) for h in ["痛点层", "解决方案", "技术实现", "用户体验感知"]]
    sol_rows = [hrow]
    for sol in solutions:
        sol_rows.append([
            Paragraph(sol["layer"], s["body"]),
            Paragraph(f"<b>{sol['solution']}</b>", s["body"]),
            [bi(s, t) for t in sol["tech"]],
            Paragraph(sol["ue"], s["callout_o"]),
        ])

    stbl = Table(sol_rows, colWidths=col_ws)
    stbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),C_NAVY), ("TEXTCOLOR",(0,0),(-1,0),white),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[white, C_LIGHT, HexColor("#fdf4ff")]),
        ("GRID",(0,0),(-1,-1),0.3,C_RULE),
        ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),5), ("RIGHTPADDING",(0,0),(-1,-1),5),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
    ]))
    story.append(stbl)
    story += conclusion_line(s,
        "三层痛点恰好对应三项核心能力——不是凑巧，世界模型本来就该服务真实的出行处境")

    # ── S14 延展方向 ───────────────────────────────────────────────────────────
    # 改动：绑定高德真实技术资产，减少技术名词重复
    story += slide_header(s, 14, "延展痛点：未来可能衍生的方向")

    exts = [
        ("01", "AR眼镜时代，导航的下一代形态",
         "从「低头看屏幕」到「抬头看世界」——路口标识与入口指引叠加在真实视野中。"
         "高德三维空间理解能力 + 阿里AI眼镜生态，成为 AR 时代空间导航的底层引擎。",
         "新终端入口 · 阿里AI眼镜生态协同（对标 Meta Glasses 战略布局）"),
        ("02", "低空经济，三维空域的数字底座",
         "eVTOL、无人机配送——低空出行开启垂直维度。高德已布局低空数字地图，"
         "下一步是将地面路网模型扩展至立体空域，支持空地协同路径规划。",
         "阿里低空战略协同 · 城市三维导航新入口（地面+低空一体化）"),
        ("03", "多人出行Agent，家庭与社交协同",
         "家庭出行、团建、约会——多用户的位置、偏好和约束需要统一调度。"
         "共享空间状态即共享决策模型，高德从「个人工具」升级为「出行协同平台」。",
         "从「工具」到「家庭出行平台」· 微信社交场景防御"),
        ("04", "城市级灾难预演与应急调度",
         "地震/洪水/大型活动应急——实时重算疏散路线、协调交通管控。"
         "这是高德从消费产品升级为城市基础设施的关键跃迁。",
         "政府/交管 B端接口 · 阿里云城市大脑延伸 · 集团城市治理战略"),
    ]

    for num, title, desc, biz in exts:
        story.append(Paragraph(f"  {num}  {title}", s["sec"]))
        story.append(Paragraph(desc, s["body"]))
        story.append(Paragraph(f"商业逻辑：{biz}", s["callout"]))
        story.append(Spacer(1, 0.2*cm))

    story.append(rule(C_NAVY, t=1.5, sb=10, sa=6))
    story.append(Paragraph(
        "总结：我的痛点是入口，真正的机会是把高德从「导航工具」升级为"
        "「可推演真实世界变化的空间智能平台」——"
        "中国最强出行数据 × 阿里AI生态 × 三维空间能力积累，缺的只是产品落地节奏。",
        s["conclusion"]))

    return story


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    out = "/home/user/air/presentation-content-v3.pdf"
    doc = SimpleDocTemplate(out, pagesize=A4,
                            leftMargin=ML, rightMargin=MR,
                            topMargin=MT, bottomMargin=MB,
                            title="高德×世界模型 — 内容改稿 v3",
                            author="产品研究")
    styles = make_styles()
    story = build_story(styles)
    doc.build(story)
    print(f"PDF saved: {out}")
    print(f"Size: {os.path.getsize(out):,} bytes")

if __name__ == "__main__":
    main()
