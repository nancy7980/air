#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kling vs Jimeng 视频生成评测工作流 —— ComfyUI 工作流生成器

为什么用脚本生成而不是手写 JSON：
ComfyUI 的工作流是 litegraph 格式，节点之间靠一组全局唯一的 link id 串联，
手写极易出现 id 错位导致导入后连线断裂。用脚本集中管理 id，保证结构合法。

运行：  python build_workflow.py
输出：  workflow/kling_jimeng_eval.json
"""

import json
import os

# ----------------------------------------------------------------------------
# 轻量级 litegraph 图构建器
# ----------------------------------------------------------------------------
class Graph:
    def __init__(self):
        self.nodes = []
        self.links = []          # [link_id, from_node, from_slot, to_node, to_slot, type]
        self.groups = []
        self._nid = 0
        self._lid = 0

    def add_node(self, type_, pos, size, title=None, widgets=None,
                 inputs=None, outputs=None, color=None, bgcolor=None, properties=None):
        self._nid += 1
        node = {
            "id": self._nid,
            "type": type_,
            "pos": list(pos),
            "size": list(size),
            "flags": {},
            "order": self._nid,
            "mode": 0,
            "inputs": inputs or [],
            "outputs": outputs or [],
            "properties": properties or {"Node name for S&R": type_},
            "widgets_values": widgets if widgets is not None else [],
        }
        if title:
            node["title"] = title
        if color:
            node["color"] = color
        if bgcolor:
            node["bgcolor"] = bgcolor
        self.nodes.append(node)
        return node

    def link(self, from_node, from_slot, to_node, to_slot, type_):
        """连接 from_node.outputs[from_slot] -> to_node.inputs[to_slot]"""
        self._lid += 1
        lid = self._lid
        # 写出端
        out = from_node["outputs"][from_slot]
        out.setdefault("links", [])
        if out["links"] is None:
            out["links"] = []
        out["links"].append(lid)
        out["slot_index"] = from_slot
        # 写入端
        inp = to_node["inputs"][to_slot]
        inp["link"] = lid
        self.links.append([lid, from_node["id"], from_slot, to_node["id"], to_slot, type_])
        return lid

    def group(self, title, bounding, color="#3f789e"):
        self.groups.append({
            "title": title,
            "bounding": list(bounding),   # [x, y, w, h]
            "color": color,
            "font_size": 24,
            "flags": {},
        })

    def to_dict(self):
        return {
            "last_node_id": self._nid,
            "last_link_id": self._lid,
            "nodes": self.nodes,
            "links": self.links,
            "groups": self.groups,
            "config": {},
            "extra": {
                "ds": {"scale": 0.6, "offset": [0, 0]},
                "info": {
                    "name": "Kling vs Jimeng 视频生成评测工作流",
                    "author": "PM Portfolio",
                    "version": "1.0",
                },
            },
            "version": 0.4,
        }


# 端口构造小工具
def out(name, type_):
    return {"name": name, "type": type_, "links": [], "slot_index": 0}

def inp(name, type_, link=None):
    return {"name": name, "type": type_, "link": link}


g = Graph()

# 颜色主题
KLING_BG = "#1c3a52"      # 蓝 —— 可灵
JIMENG_BG = "#522c1c"     # 橙 —— 即梦
JUDGE_BG = "#2c5230"      # 绿 —— 评委
IO_BG = "#444"            # 灰 —— 输入/输出

# ============================================================================
# 列 X 坐标
# ============================================================================
X_IN   = 40       # 输入
X_GEN  = 620      # 生成
X_MID  = 1240     # 保存 / 抽帧
X_JUDGE= 1820     # LLM 评委
X_OUT  = 2440     # 评分输出 / 汇总

# ============================================================================
# ① 评测输入区
# ============================================================================
intro_md = (
    "## 🎬 可灵 vs 即梦 视频生成能力评测工作流\n\n"
    "**用途**：同一组受控输入下，并排评测可灵(Kling)与即梦(Jimeng)的 T2V / I2V 能力，"
    "由多模态大模型按统一 rubric 自动打分，并辅以客观指标交叉验证。\n\n"
    "**控制变量**：左侧共享的 Prompt / 输入图 / 运动描述，两家完全一致，保证公平。\n\n"
    "**使用顺序**：① 填左侧输入 → ② 在各生成节点填 API Key/模型 → ③ Queue → "
    "④ 读右侧评委打分 → ⑤ 把视频+评分填入对比看板。\n\n"
    "> 节点颜色：蓝=可灵，橙=即梦，绿=LLM评委，灰=输入/输出。"
)

n_intro = g.add_node(
    "Note", (X_IN, -360), (540, 300), title="📖 评测说明 / README",
    widgets=[intro_md], bgcolor=IO_BG,
)

# 共享正向 Prompt（受控变量，喂给两家的 T2V / I2V）
n_prompt = g.add_node(
    "PrimitiveNode", (X_IN, 0), (540, 200), title="① 共享 Prompt（受控变量）",
    widgets=[
        "A cinematic shot of a red fox running through a snowy forest at sunrise, "
        "camera slowly tracking, volumetric light, photorealistic, 4k",
        "fixed",
    ],
    outputs=[out("STRING", "STRING")], bgcolor=IO_BG,
)

# 共享运动 / 负向描述
n_motion = g.add_node(
    "PrimitiveNode", (X_IN, 240), (540, 140), title="① 共享运动/负向描述",
    widgets=["smooth natural motion; avoid: morphing, flicker, extra limbs", "fixed"],
    outputs=[out("STRING", "STRING")], bgcolor=IO_BG,
)

# I2V 共享输入图
n_image = g.add_node(
    "LoadImage", (X_IN, 420), (540, 380), title="① I2V 共享输入图（受控变量）",
    widgets=["test_input.png", "image"],
    outputs=[out("IMAGE", "IMAGE"), out("MASK", "MASK")], bgcolor=IO_BG,
)

# 评分 Rubric（喂给两个 LLM 评委）
rubric_text = (
    "你是资深视频生成质量评测专家。请对【视频A=可灵 / 视频B=即梦】按以下5个维度各打1-10分，"
    "并给出简短理由，最后输出 JSON：{dimension, kling_score, jimeng_score, reason}。\n"
    "维度与权重：\n"
    "1. 画面质量 Visual Quality (25%)：清晰度、细节、无伪影\n"
    "2. 运动合理性 Motion Quality (25%)：运动自然、无闪烁/形变、物理合理\n"
    "3. 文本一致性 Prompt Adherence (25%)：是否准确还原 prompt 的主体/动作/场景\n"
    "4. 时序一致性 Temporal Consistency (15%)：主体/背景跨帧稳定，不漂移\n"
    "5. 美学表现 Aesthetics (10%)：构图、光影、色彩、电影感\n"
    "评分需中立、可复现；同分时说明区分点。最后给出加权总分与胜出方。"
)
n_rubric = g.add_node(
    "PrimitiveNode", (X_IN, 840), (540, 320), title="① 评分 Rubric（受控标准）",
    widgets=[rubric_text, "fixed"],
    outputs=[out("STRING", "STRING")], bgcolor=JUDGE_BG,
)

# ============================================================================
# ② 可灵 Kling 生成（T2V + I2V）
# ============================================================================
# Kling Text-to-Video（ComfyUI 官方 API 节点）
n_kling_t2v = g.add_node(
    "KlingTextToVideoNode", (X_GEN, 0), (430, 280), title="② 可灵 文生视频 T2V",
    widgets=["kling-v1-6", 5, "16:9", "std", 0.5, 12345],  # model, duration, ratio, mode, cfg, seed
    inputs=[inp("prompt", "STRING"), inp("negative_prompt", "STRING")],
    outputs=[out("VIDEO", "VIDEO")], bgcolor=KLING_BG,
)
# Kling Image-to-Video
n_kling_i2v = g.add_node(
    "KlingImageToVideoNode", (X_GEN, 340), (430, 320), title="② 可灵 图生视频 I2V",
    widgets=["kling-v1-6", 5, "16:9", "std", 0.5, 12345],
    inputs=[inp("start_frame", "IMAGE"), inp("prompt", "STRING"), inp("negative_prompt", "STRING")],
    outputs=[out("VIDEO", "VIDEO")], bgcolor=KLING_BG,
)

# ============================================================================
# ③ 即梦 Jimeng 生成（T2V + I2V）
# ============================================================================
n_jimeng_t2v = g.add_node(
    "JimengTextToVideoNode", (X_GEN, 720), (430, 280), title="③ 即梦 文生视频 T2V",
    widgets=["jimeng-video-3.0", 5, "16:9", 12345],  # model, duration, ratio, seed
    inputs=[inp("prompt", "STRING"), inp("negative_prompt", "STRING")],
    outputs=[out("VIDEO", "VIDEO")], bgcolor=JIMENG_BG,
)
n_jimeng_i2v = g.add_node(
    "JimengImageToVideoNode", (X_GEN, 1060), (430, 320), title="③ 即梦 图生视频 I2V",
    widgets=["jimeng-video-3.0", 5, "16:9", 12345],
    inputs=[inp("start_frame", "IMAGE"), inp("prompt", "STRING"), inp("negative_prompt", "STRING")],
    outputs=[out("VIDEO", "VIDEO")], bgcolor=JIMENG_BG,
)

# ============================================================================
# ④ 保存视频 + 抽帧（喂给 LLM 评委）
# ============================================================================
def save_video(node, y, title, bg):
    return g.add_node(
        "SaveVideo", (X_MID, y), (360, 150), title=title,
        widgets=["eval/" + title.split()[0], "mp4", "h264"],
        inputs=[inp("video", "VIDEO")], outputs=[], bgcolor=bg,
    )

def sample_frames(node, y, title, bg):
    # 抽取若干关键帧供视觉 LLM 评判（VideoHelperSuite）
    return g.add_node(
        "VHS_VideoToImages", (X_MID, y + 170), (360, 130), title=title,
        widgets=[8],  # 抽 8 帧
        inputs=[inp("video", "VIDEO")],
        outputs=[out("IMAGE", "IMAGE")], bgcolor=bg,
    )

n_save_k_t2v = save_video(n_kling_t2v, 0,   "可灵-T2V 保存", KLING_BG)
n_frames_k_t2v = sample_frames(n_kling_t2v, 0, "可灵-T2V 抽帧", KLING_BG)

n_save_j_t2v = save_video(n_jimeng_t2v, 720, "即梦-T2V 保存", JIMENG_BG)
n_frames_j_t2v = sample_frames(n_jimeng_t2v, 720, "即梦-T2V 抽帧", JIMENG_BG)

n_save_k_i2v = save_video(n_kling_i2v, 360, "可灵-I2V 保存", KLING_BG)
n_frames_k_i2v = sample_frames(n_kling_i2v, 360, "可灵-I2V 抽帧", KLING_BG)

n_save_j_i2v = save_video(n_jimeng_i2v, 1080, "即梦-I2V 保存", JIMENG_BG)
n_frames_j_i2v = sample_frames(n_jimeng_i2v, 1080, "即梦-I2V 抽帧", JIMENG_BG)

# ============================================================================
# ⑤ LLM 评委：T2V 对比、I2V 对比
# ============================================================================
# 多模态评委节点：输入两家关键帧 + prompt + rubric -> 输出结构化评分
def judge(y, title):
    return g.add_node(
        "LLMVideoJudge", (X_JUDGE, y), (440, 320), title=title,
        widgets=["claude-opus-4-8", 0.0],   # judge_model, temperature
        inputs=[
            inp("frames_a", "IMAGE"),   # A = 可灵
            inp("frames_b", "IMAGE"),   # B = 即梦
            inp("prompt", "STRING"),
            inp("rubric", "STRING"),
        ],
        outputs=[out("scorecard", "STRING")], bgcolor=JUDGE_BG,
    )

n_judge_t2v = judge(40,  "④ LLM 评委 · T2V 对比打分")
n_judge_i2v = judge(720, "④ LLM 评委 · I2V 对比打分")

# ============================================================================
# ⑥ 评分输出 + 客观指标 + 汇总
# ============================================================================
n_save_t2v = g.add_node(
    "SaveText", (X_OUT, 40), (380, 180), title="⑤ T2V 评分卡输出（JSON）",
    widgets=["eval/scorecard_t2v.json", "overwrite"],
    inputs=[inp("text", "STRING")], outputs=[], bgcolor=IO_BG,
)
n_save_i2v = g.add_node(
    "SaveText", (X_OUT, 260), (380, 180), title="⑤ I2V 评分卡输出（JSON）",
    widgets=["eval/scorecard_i2v.json", "overwrite"],
    inputs=[inp("text", "STRING")], outputs=[], bgcolor=IO_BG,
)

metrics_md = (
    "## 📊 轻量客观指标（人工/脚本补录，交叉验证）\n\n"
    "在 LLM 主观打分之外，记录以下可量化、产品化指标：\n\n"
    "| 指标 | 可灵 | 即梦 |\n"
    "|---|---|---|\n"
    "| 生成耗时 (s) |  |  |\n"
    "| 一次成功率 (%) |  |  |\n"
    "| 实际分辨率 |  |  |\n"
    "| 实际时长 (s) |  |  |\n"
    "| 单条成本 (¥) |  |  |\n"
    "| 失败/驳回次数 |  |  |\n\n"
    "> 这些指标不需要复杂模型，却最贴近 PM 关心的「质量×成本×效率」三角。"
)
n_metrics = g.add_node(
    "Note", (X_OUT, 480), (380, 360), title="⑤ 客观指标记录表",
    widgets=[metrics_md], bgcolor=IO_BG,
)

# ============================================================================
# 连线
# ============================================================================
# 共享 Prompt -> 四个生成节点的 prompt
g.link(n_prompt, 0, n_kling_t2v, 0, "STRING")
g.link(n_prompt, 0, n_kling_i2v, 1, "STRING")
g.link(n_prompt, 0, n_jimeng_t2v, 0, "STRING")
g.link(n_prompt, 0, n_jimeng_i2v, 1, "STRING")

# 共享运动/负向 -> negative_prompt
g.link(n_motion, 0, n_kling_t2v, 1, "STRING")
g.link(n_motion, 0, n_kling_i2v, 2, "STRING")
g.link(n_motion, 0, n_jimeng_t2v, 1, "STRING")
g.link(n_motion, 0, n_jimeng_i2v, 2, "STRING")

# 共享输入图 -> 两家 I2V start_frame
g.link(n_image, 0, n_kling_i2v, 0, "IMAGE")
g.link(n_image, 0, n_jimeng_i2v, 0, "IMAGE")

# 生成视频 -> 保存 + 抽帧
g.link(n_kling_t2v, 0, n_save_k_t2v, 0, "VIDEO")
g.link(n_kling_t2v, 0, n_frames_k_t2v, 0, "VIDEO")
g.link(n_jimeng_t2v, 0, n_save_j_t2v, 0, "VIDEO")
g.link(n_jimeng_t2v, 0, n_frames_j_t2v, 0, "VIDEO")
g.link(n_kling_i2v, 0, n_save_k_i2v, 0, "VIDEO")
g.link(n_kling_i2v, 0, n_frames_k_i2v, 0, "VIDEO")
g.link(n_jimeng_i2v, 0, n_save_j_i2v, 0, "VIDEO")
g.link(n_jimeng_i2v, 0, n_frames_j_i2v, 0, "VIDEO")

# 抽帧 -> 评委
g.link(n_frames_k_t2v, 0, n_judge_t2v, 0, "IMAGE")   # A=可灵
g.link(n_frames_j_t2v, 0, n_judge_t2v, 1, "IMAGE")   # B=即梦
g.link(n_prompt, 0, n_judge_t2v, 2, "STRING")
g.link(n_rubric, 0, n_judge_t2v, 3, "STRING")

g.link(n_frames_k_i2v, 0, n_judge_i2v, 0, "IMAGE")
g.link(n_frames_j_i2v, 0, n_judge_i2v, 1, "IMAGE")
g.link(n_prompt, 0, n_judge_i2v, 2, "STRING")
g.link(n_rubric, 0, n_judge_i2v, 3, "STRING")

# 评委 -> 评分卡输出
g.link(n_judge_t2v, 0, n_save_t2v, 0, "STRING")
g.link(n_judge_i2v, 0, n_save_i2v, 0, "STRING")

# ============================================================================
# 分组框
# ============================================================================
g.group("① 评测输入（受控变量）", (X_IN - 20, -420, 580, 1620), "#595")
g.group("② 可灵 Kling 生成", (X_GEN - 20, -60, 470, 760), "#36c")
g.group("③ 即梦 Jimeng 生成", (X_GEN - 20, 660, 470, 760), "#c63")
g.group("④ 保存 & 抽帧", (X_MID - 20, -60, 400, 1480), "#777")
g.group("⑤ LLM 评委 & 评分输出", (X_JUDGE - 20, -20, 1020, 920), "#393")

# ============================================================================
# 写出
# ============================================================================
here = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(here, "workflow", "kling_jimeng_eval.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(g.to_dict(), f, ensure_ascii=False, indent=2)

print("已生成:", out_path)
print("节点数:", len(g.nodes), " 连线数:", len(g.links))
