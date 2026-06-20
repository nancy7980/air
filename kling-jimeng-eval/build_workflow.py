#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可灵(Kling) vs 即梦(Seedance) 视频评测工作流 —— ComfyUI 工作流生成器（云端原生版）

设计目标：在【官方 ComfyUI Cloud】上零自定义节点、零外网 HTTP 即可运行。
全部使用官方 API / 合作节点 + 核心内置节点：
  - 可灵   : KlingTextToVideoNode / KlingImageToVideoNode          (官方 API 节点)
  - 即梦   : ByteDance2TextToVideoNode / ByteDanceImageToVideoNode  (官方 Seedance 合作节点)
            说明：即梦视频由字节 Seedance 模型驱动，官方内置 Seedance 节点评测同源能力。
  - 评委   : Gemini                                                (Google 官方合作节点，多模态)
  - 抽帧   : GetVideoComponents                                    (核心内置节点，视频->帧)
  - 合帧   : ImageBatch                                            (核心内置节点，两批帧合一)
  - 其他   : SaveVideo / SaveText / LoadImage / PrimitiveNode / Note (核心内置)

为什么用脚本生成而不是手写 JSON：
litegraph 节点靠一组全局唯一 link id 串联，手写极易 id 错位导致连线断裂。
脚本集中管理 id，保证结构合法。

运行：  python build_workflow.py
输出：  workflow/kling_jimeng_eval.json
"""

import json
import os


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
            "id": self._nid, "type": type_, "pos": list(pos), "size": list(size),
            "flags": {}, "order": self._nid, "mode": 0,
            "inputs": inputs or [], "outputs": outputs or [],
            "properties": properties or {"Node name for S&R": type_},
            "widgets_values": widgets if widgets is not None else [],
        }
        if title: node["title"] = title
        if color: node["color"] = color
        if bgcolor: node["bgcolor"] = bgcolor
        self.nodes.append(node)
        return node

    def link(self, from_node, from_slot, to_node, to_slot, type_):
        self._lid += 1
        lid = self._lid
        out = from_node["outputs"][from_slot]
        out.setdefault("links", [])
        if out["links"] is None: out["links"] = []
        out["links"].append(lid)
        out["slot_index"] = from_slot
        to_node["inputs"][to_slot]["link"] = lid
        self.links.append([lid, from_node["id"], from_slot, to_node["id"], to_slot, type_])
        return lid

    def group(self, title, bounding, color="#3f789e"):
        self.groups.append({"title": title, "bounding": list(bounding),
                            "color": color, "font_size": 24, "flags": {}})

    def to_dict(self):
        return {
            "last_node_id": self._nid, "last_link_id": self._lid,
            "nodes": self.nodes, "links": self.links, "groups": self.groups,
            "config": {}, "extra": {"ds": {"scale": 0.55, "offset": [0, 0]},
                "info": {"name": "Kling vs Seedance(即梦) 视频评测 · 云端原生",
                         "author": "PM Portfolio", "version": "2.0-cloud"}},
            "version": 0.4,
        }


def out(name, type_): return {"name": name, "type": type_, "links": [], "slot_index": 0}
def inp(name, type_, link=None): return {"name": name, "type": type_, "link": link}


g = Graph()

KLING_BG = "#1c3a52"
SEED_BG  = "#522c1c"
JUDGE_BG = "#2c5230"
IO_BG    = "#3a3a3a"

X_IN, X_GEN, X_FRAME, X_SAVE, X_BATCH, X_JUDGE, X_OUT = 40, 660, 1280, 1700, 2120, 2560, 3060

# ============================================================================
# ① 评测输入区（受控变量）
# ============================================================================
intro_md = (
    "## 🎬 可灵 vs 即梦(Seedance) 视频评测 · 云端原生版\n\n"
    "**全官方节点，ComfyUI Cloud 零自定义节点即可运行。**\n\n"
    "- 可灵 = 官方 Kling API 节点\n"
    "- 即梦 = 官方 ByteDance **Seedance** 节点（即梦视频同源模型）\n"
    "- 评委 = 官方 **Gemini** 多模态节点，按 5 维 Rubric 打分\n"
    "- 抽帧 = 核心 **GetVideoComponents** 节点\n\n"
    "**控制变量**：左侧共享 Prompt / 输入图 / 运动描述，两家完全一致。\n\n"
    "**用法**：① 填左侧输入 → ② 各生成节点选模型(已配 API 额度) → ③ Queue → "
    "④ 读 Gemini 评分卡 → ⑤ 填入对比看板。\n\n"
    "> 颜色：蓝=可灵，橙=即梦/Seedance，绿=评委，灰=输入/输出。"
)
g.add_node("Note", (X_IN, -380), (560, 320), title="📖 评测说明 / README",
           widgets=[intro_md], bgcolor=IO_BG)

n_prompt = g.add_node("PrimitiveNode", (X_IN, 0), (560, 190),
    title="① 共享 Prompt（受控变量）",
    widgets=["A cinematic shot of a red fox running through a snowy forest at sunrise, "
             "camera slowly tracking, volumetric light, photorealistic, 4k", "fixed"],
    outputs=[out("STRING", "STRING")], bgcolor=IO_BG)

n_motion = g.add_node("PrimitiveNode", (X_IN, 230), (560, 140),
    title="① 共享运动/负向描述",
    widgets=["smooth natural motion; avoid: morphing, flicker, extra limbs", "fixed"],
    outputs=[out("STRING", "STRING")], bgcolor=IO_BG)

n_image = g.add_node("LoadImage", (X_IN, 410), (560, 380),
    title="① I2V 共享输入图（受控变量）", widgets=["test_input.png", "image"],
    outputs=[out("IMAGE", "IMAGE"), out("MASK", "MASK")], bgcolor=IO_BG)

rubric_text = (
    "你是资深视频生成质量评测专家。画面前半部分帧来自【视频A=可灵】，后半部分帧来自【视频B=即梦/Seedance】，"
    "二者使用完全相同的 prompt。请按以下5个维度各打1-10分并给简短理由，最后输出 JSON："
    "{results:[{dimension,kling_score,jimeng_score,reason}],weighted_total:{kling,jimeng},winner,summary}。\n"
    "维度与权重：\n"
    "1. 画面质量(25%)：清晰度/细节/无伪影\n"
    "2. 运动合理性(25%)：自然/无闪烁形变/物理合理\n"
    "3. 文本一致性(25%)：准确还原主体/动作/场景\n"
    "4. 时序一致性(15%)：跨帧稳定不漂移\n"
    "5. 美学(10%)：构图/光影/色彩/电影感\n"
    "评分需中立可复现，最后给加权总分与胜出方。"
)
n_rubric = g.add_node("PrimitiveNode", (X_IN, 840), (560, 320),
    title="① 评分 Rubric（喂给 Gemini 评委）",
    widgets=[rubric_text, "fixed"], outputs=[out("STRING", "STRING")], bgcolor=JUDGE_BG)

# ============================================================================
# ② 可灵生成 / ③ 即梦(Seedance)生成
# ============================================================================
n_k_t2v = g.add_node("KlingTextToVideoNode", (X_GEN, 0), (430, 270),
    title="② 可灵 文生视频 T2V",
    widgets=["kling-v1-6", 5, "16:9", "std", 0.5, 12345],
    inputs=[inp("prompt", "STRING"), inp("negative_prompt", "STRING")],
    outputs=[out("VIDEO", "VIDEO")], bgcolor=KLING_BG)

n_k_i2v = g.add_node("KlingImageToVideoNode", (X_GEN, 320), (430, 300),
    title="② 可灵 图生视频 I2V",
    widgets=["kling-v1-6", 5, "16:9", "std", 0.5, 12345],
    inputs=[inp("start_frame", "IMAGE"), inp("prompt", "STRING"), inp("negative_prompt", "STRING")],
    outputs=[out("VIDEO", "VIDEO")], bgcolor=KLING_BG)

n_s_t2v = g.add_node("ByteDance2TextToVideoNode", (X_GEN, 700), (430, 270),
    title="③ 即梦/Seedance 文生视频 T2V",
    widgets=["seedance-2.0", "1080p", 5, "16:9", 12345],   # model, resolution, duration, ratio, seed
    inputs=[inp("prompt", "STRING")],
    outputs=[out("VIDEO", "VIDEO")], bgcolor=SEED_BG)

n_s_i2v = g.add_node("ByteDanceImageToVideoNode", (X_GEN, 1020), (430, 300),
    title="③ 即梦/Seedance 图生视频 I2V",
    widgets=["seedance-1.0-pro", "1080p", 5, 12345],
    inputs=[inp("image", "IMAGE"), inp("prompt", "STRING")],
    outputs=[out("VIDEO", "VIDEO")], bgcolor=SEED_BG)

# ============================================================================
# ④ 抽帧（GetVideoComponents，核心节点）
# ============================================================================
def frames(y, title, bg):
    return g.add_node("GetVideoComponents", (X_FRAME, y), (340, 110), title=title,
        inputs=[inp("video", "VIDEO")],
        outputs=[out("images", "IMAGE"), out("audio", "AUDIO"), out("fps", "FLOAT")],
        bgcolor=bg)

f_k_t2v = frames(0,    "④ 可灵-T2V 抽帧", KLING_BG)
f_s_t2v = frames(700,  "④ 即梦-T2V 抽帧", SEED_BG)
f_k_i2v = frames(320,  "④ 可灵-I2V 抽帧", KLING_BG)
f_s_i2v = frames(1020, "④ 即梦-I2V 抽帧", SEED_BG)

# 保存视频
def savevid(y, title, bg):
    return g.add_node("SaveVideo", (X_SAVE, y), (320, 120), title=title,
        widgets=["eval/" + title.split()[1], "mp4", "h264"],
        inputs=[inp("video", "VIDEO")], outputs=[], bgcolor=bg)

sv_k_t2v = savevid(150,  "保存 可灵-T2V", KLING_BG)
sv_s_t2v = savevid(850,  "保存 即梦-T2V", SEED_BG)
sv_k_i2v = savevid(470,  "保存 可灵-I2V", KLING_BG)
sv_s_i2v = savevid(1170, "保存 即梦-I2V", SEED_BG)

# ============================================================================
# ⑤ 合帧（ImageBatch）→ Gemini 评委 → 评分卡
# ============================================================================
def imagebatch(y, title):
    return g.add_node("ImageBatch", (X_BATCH, y), (300, 90), title=title,
        inputs=[inp("image1", "IMAGE"), inp("image2", "IMAGE")],
        outputs=[out("IMAGE", "IMAGE")], bgcolor=JUDGE_BG)

b_t2v = imagebatch(180,  "⑤ 合帧 T2V（A可灵+B即梦）")
b_i2v = imagebatch(880,  "⑤ 合帧 I2V（A可灵+B即梦）")

def gemini(y, title):
    return g.add_node("Gemini", (X_JUDGE, y), (380, 240), title=title,
        widgets=["gemini-2.5-pro", 0.0],   # model, temperature
        inputs=[inp("prompt", "STRING"), inp("images", "IMAGE")],
        outputs=[out("text", "STRING")], bgcolor=JUDGE_BG)

j_t2v = gemini(120, "⑤ Gemini 评委 · T2V 打分")
j_i2v = gemini(820, "⑤ Gemini 评委 · I2V 打分")

st_t2v = g.add_node("SaveText", (X_OUT, 140), (360, 150),
    title="⑤ T2V 评分卡输出(JSON)", widgets=["eval/scorecard_t2v.json", "overwrite"],
    inputs=[inp("text", "STRING")], outputs=[], bgcolor=IO_BG)
st_i2v = g.add_node("SaveText", (X_OUT, 320), (360, 150),
    title="⑤ I2V 评分卡输出(JSON)", widgets=["eval/scorecard_i2v.json", "overwrite"],
    inputs=[inp("text", "STRING")], outputs=[], bgcolor=IO_BG)

metrics_md = (
    "## 📊 轻量客观指标（手动/脚本补录）\n\n"
    "| 指标 | 可灵 | 即梦 |\n|---|---|---|\n"
    "| 生成耗时(s) |  |  |\n| 一次成功率(%) |  |  |\n"
    "| 实际分辨率 |  |  |\n| 单条成本(¥) |  |  |\n"
    "| 失败/驳回次数 |  |  |\n\n"
    "> 贴近 PM 关心的「质量×成本×效率」三角。"
)
g.add_node("Note", (X_OUT, 520), (360, 340), title="⑤ 客观指标记录表",
           widgets=[metrics_md], bgcolor=IO_BG)

# ============================================================================
# 连线
# ============================================================================
# 共享 Prompt -> 四个生成节点
g.link(n_prompt, 0, n_k_t2v, 0, "STRING")
g.link(n_prompt, 0, n_k_i2v, 1, "STRING")
g.link(n_prompt, 0, n_s_t2v, 0, "STRING")
g.link(n_prompt, 0, n_s_i2v, 1, "STRING")
# 负向 -> 可灵（Seedance 节点无独立负向输入，写入 prompt 内）
g.link(n_motion, 0, n_k_t2v, 1, "STRING")
g.link(n_motion, 0, n_k_i2v, 2, "STRING")
# 共享输入图 -> 两家 I2V
g.link(n_image, 0, n_k_i2v, 0, "IMAGE")
g.link(n_image, 0, n_s_i2v, 0, "IMAGE")

# 生成视频 -> 抽帧 + 保存
for vid, fr, sv in [(n_k_t2v, f_k_t2v, sv_k_t2v), (n_s_t2v, f_s_t2v, sv_s_t2v),
                    (n_k_i2v, f_k_i2v, sv_k_i2v), (n_s_i2v, f_s_i2v, sv_s_i2v)]:
    g.link(vid, 0, fr, 0, "VIDEO")
    g.link(vid, 0, sv, 0, "VIDEO")

# 抽帧 -> 合帧（A=可灵 image1, B=即梦 image2）
g.link(f_k_t2v, 0, b_t2v, 0, "IMAGE")
g.link(f_s_t2v, 0, b_t2v, 1, "IMAGE")
g.link(f_k_i2v, 0, b_i2v, 0, "IMAGE")
g.link(f_s_i2v, 0, b_i2v, 1, "IMAGE")

# 合帧 + Rubric -> Gemini -> 评分卡
g.link(n_rubric, 0, j_t2v, 0, "STRING")
g.link(b_t2v, 0, j_t2v, 1, "IMAGE")
g.link(j_t2v, 0, st_t2v, 0, "STRING")

g.link(n_rubric, 0, j_i2v, 0, "STRING")
g.link(b_i2v, 0, j_i2v, 1, "IMAGE")
g.link(j_i2v, 0, st_i2v, 0, "STRING")

# ============================================================================
# 分组框
# ============================================================================
g.group("① 评测输入（受控变量）", (X_IN - 20, -440, 600, 1620), "#595")
g.group("② 可灵 Kling 生成", (X_GEN - 20, -60, 470, 700), "#36c")
g.group("③ 即梦 Seedance 生成", (X_GEN - 20, 640, 470, 700), "#c63")
g.group("④ 抽帧 & 保存", (X_FRAME - 20, -60, 800, 1400), "#777")
g.group("⑤ 合帧 · Gemini 评委 · 评分输出", (X_BATCH - 20, 60, 1380, 1080), "#393")

here = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(here, "workflow", "kling_jimeng_eval.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(g.to_dict(), f, ensure_ascii=False, indent=2)

print("已生成:", out_path)
print("节点数:", len(g.nodes), " 连线数:", len(g.links))
