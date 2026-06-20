#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可灵(Kling) vs 即梦(Seedance) 视频评测工作流 —— ComfyUI 工作流生成器（云端原生版 v3）

仅使用【官方内置】节点（已核对 ComfyUI 源码 NODE_CLASS_MAPPINGS），ComfyUI Cloud 零自定义节点即可运行：
  - 可灵 T2V : KlingTextToVideoNode        inputs: prompt, negative_prompt, ...
  - 可灵 I2V : KlingImage2VideoNode         inputs: start_frame, prompt, negative_prompt, ...
  - 即梦 T2V : ByteDanceTextToVideoNode     inputs: prompt, ...(Seedance, 无独立 negative)
  - 即梦 I2V : ByteDanceImageToVideoNode    inputs: image, prompt, ...
  - 评委     : GeminiNode                   inputs: prompt, video(直接收视频), images, ...
  - 其他     : LoadImage / PrimitiveNode / SaveVideo / SaveText / Note (核心内置)

设计：每个生成视频直接喂一个 GeminiNode，按 Rubric 独立打 5 维分（绝对分），
对比在看板里完成。比"抽帧+合帧"更少节点、云端更稳，且单视频绝对评分更少偏见。

运行：  python build_workflow.py
输出：  workflow/kling_jimeng_eval.json
"""

import json
import os


class Graph:
    def __init__(self):
        self.nodes, self.links, self.groups = [], [], []
        self._nid = self._lid = 0

    def add_node(self, type_, pos, size, title=None, widgets=None,
                 inputs=None, outputs=None, bgcolor=None):
        self._nid += 1
        node = {
            "id": self._nid, "type": type_, "pos": list(pos), "size": list(size),
            "flags": {}, "order": self._nid, "mode": 0,
            "inputs": inputs or [], "outputs": outputs or [],
            "properties": {"Node name for S&R": type_},
            "widgets_values": widgets if widgets is not None else [],
        }
        if title: node["title"] = title
        if bgcolor: node["bgcolor"] = bgcolor
        self.nodes.append(node)
        return node

    def link(self, fn, fs, tn, ts, t):
        self._lid += 1
        lid = self._lid
        o = fn["outputs"][fs]
        o.setdefault("links", [])
        if o["links"] is None: o["links"] = []
        o["links"].append(lid); o["slot_index"] = fs
        tn["inputs"][ts]["link"] = lid
        self.links.append([lid, fn["id"], fs, tn["id"], ts, t])
        return lid

    def group(self, title, b, color="#3f789e"):
        self.groups.append({"title": title, "bounding": list(b),
                            "color": color, "font_size": 24, "flags": {}})

    def to_dict(self):
        return {"last_node_id": self._nid, "last_link_id": self._lid,
                "nodes": self.nodes, "links": self.links, "groups": self.groups,
                "config": {}, "extra": {"ds": {"scale": 0.6, "offset": [0, 0]},
                    "info": {"name": "Kling vs Seedance(即梦) 视频评测 · 云端原生 v3",
                             "version": "3.0-cloud"}}, "version": 0.4}


def O(name, t): return {"name": name, "type": t, "links": [], "slot_index": 0}
def I(name, t): return {"name": name, "type": t, "link": None}


g = Graph()
KLING_BG, SEED_BG, JUDGE_BG, IO_BG = "#1c3a52", "#522c1c", "#2c5230", "#3a3a3a"
X_IN, X_GEN, X_SAVE, X_JUDGE, X_OUT = 40, 660, 1240, 1620, 2160

# ① 输入 -------------------------------------------------------------------
intro = (
    "## 🎬 可灵 vs 即梦(Seedance) 视频评测 · 云端原生 v3\n\n"
    "**全官方内置节点，ComfyUI Cloud 零自定义节点即可运行。**\n\n"
    "- 可灵 = 官方 Kling 节点 / 即梦 = 官方 ByteDance Seedance 节点（即梦同源模型）\n"
    "- 评委 = 官方 GeminiNode，直接收视频，按 5 维 Rubric 给每个视频打绝对分\n"
    "- 对比在 dashboard/comparison-dashboard.html 看板完成\n\n"
    "**控制变量**：左侧共享 Prompt / 输入图 / 运动描述，两家一致。\n"
    "**用法**：填输入 → 各生成节点授权额度 → Queue → 读 4 张评分卡 → 填看板。\n\n"
    "> ① I2V 输入图记得在 LoadImage 上传选择，否则提示'缺少输入·图像'。"
)
g.add_node("Note", (X_IN, -360), (560, 300), title="📖 评测说明", widgets=[intro], bgcolor=IO_BG)

n_prompt = g.add_node("PrimitiveNode", (X_IN, 0), (560, 180), title="① 共享 Prompt（受控）",
    widgets=["A cinematic shot of a red fox running through a snowy forest at sunrise, "
             "camera slowly tracking, volumetric light, photorealistic, 4k", "fixed"],
    outputs=[O("STRING", "STRING")], bgcolor=IO_BG)

n_neg = g.add_node("PrimitiveNode", (X_IN, 220), (560, 130), title="① 共享负向（仅可灵用）",
    widgets=["morphing, flicker, extra limbs, distortion", "fixed"],
    outputs=[O("STRING", "STRING")], bgcolor=IO_BG)

n_img = g.add_node("LoadImage", (X_IN, 390), (560, 380), title="① I2V 共享输入图（受控）",
    widgets=["test_input.png", "image"],
    outputs=[O("IMAGE", "IMAGE"), O("MASK", "MASK")], bgcolor=IO_BG)

rubric = (
    "你是资深视频生成质量评测专家。请只针对【这一个视频】按以下5维各打1-10分并给简短理由，"
    "最后输出 JSON：{video_label, scores:[{dimension, score, reason}], weighted_total, comment}。\n"
    "该视频对应的 prompt 与另一家完全相同，评分需中立、可复现：\n"
    "1. 画面质量(25%)：清晰度/细节/无伪影\n"
    "2. 运动合理性(25%)：自然/无闪烁形变/物理合理\n"
    "3. 文本一致性(25%)：准确还原 prompt 的主体/动作/场景\n"
    "4. 时序一致性(15%)：跨帧稳定不漂移\n"
    "5. 美学(10%)：构图/光影/色彩/电影感\n"
    "weighted_total = Σ(维度分×权重)，满分10。"
)
n_rubric = g.add_node("PrimitiveNode", (X_IN, 800), (560, 320), title="① 评分 Rubric（喂 Gemini）",
    widgets=[rubric, "fixed"], outputs=[O("STRING", "STRING")], bgcolor=JUDGE_BG)

# ② 可灵 / ③ 即梦 生成 -----------------------------------------------------
n_k_t2v = g.add_node("KlingTextToVideoNode", (X_GEN, 0), (420, 260), title="② 可灵 文生视频 T2V",
    widgets=["kling-v1-6", 5, "16:9", "std", 0.5, 12345],
    inputs=[I("prompt", "STRING"), I("negative_prompt", "STRING")],
    outputs=[O("VIDEO", "VIDEO")], bgcolor=KLING_BG)

n_k_i2v = g.add_node("KlingImage2VideoNode", (X_GEN, 300), (420, 290), title="② 可灵 图生视频 I2V",
    widgets=["kling-v1-6", 5, "16:9", "std", 0.5, 12345],
    inputs=[I("start_frame", "IMAGE"), I("prompt", "STRING"), I("negative_prompt", "STRING")],
    outputs=[O("VIDEO", "VIDEO")], bgcolor=KLING_BG)

n_s_t2v = g.add_node("ByteDanceTextToVideoNode", (X_GEN, 650), (420, 260), title="③ 即梦/Seedance 文生 T2V",
    widgets=["seedance-1-0-pro", "1080p", "16:9", 5, 12345],   # model, resolution, ratio, duration, seed
    inputs=[I("prompt", "STRING")], outputs=[O("VIDEO", "VIDEO")], bgcolor=SEED_BG)

n_s_i2v = g.add_node("ByteDanceImageToVideoNode", (X_GEN, 950), (420, 290), title="③ 即梦/Seedance 图生 I2V",
    widgets=["seedance-1-0-pro", "1080p", 5, 12345],
    inputs=[I("image", "IMAGE"), I("prompt", "STRING")],
    outputs=[O("VIDEO", "VIDEO")], bgcolor=SEED_BG)

# 保存视频 -----------------------------------------------------------------
def savevid(y, label, bg):
    return g.add_node("SaveVideo", (X_SAVE, y), (300, 110), title="保存 " + label,
        widgets=["eval/" + label, "mp4", "h264"], inputs=[I("video", "VIDEO")], bgcolor=bg)

sv = [savevid(0, "kling_t2v", KLING_BG), savevid(300, "kling_i2v", KLING_BG),
      savevid(650, "seedance_t2v", SEED_BG), savevid(950, "seedance_i2v", SEED_BG)]

# ④ Gemini 评委（每视频一个，直接收 video） -------------------------------
def judge(y, label):
    return g.add_node("GeminiNode", (X_JUDGE, y), (380, 220), title="④ Gemini 评委 · " + label,
        widgets=["gemini-2.5-pro", 12345],   # model, seed
        inputs=[I("prompt", "STRING"), I("video", "VIDEO")],
        outputs=[O("text", "STRING")], bgcolor=JUDGE_BG)

j = [judge(0, "可灵 T2V"), judge(300, "可灵 I2V"), judge(650, "即梦 T2V"), judge(950, "即梦 I2V")]

# ⑤ 评分卡输出 -------------------------------------------------------------
def savetext(y, name):
    return g.add_node("SaveText", (X_OUT, y), (340, 120), title="⑤ 评分卡 " + name,
        widgets=["eval/scorecard_" + name + ".json", "overwrite"], inputs=[I("text", "STRING")], bgcolor=IO_BG)

st = [savetext(0, "kling_t2v"), savetext(300, "kling_i2v"),
      savetext(650, "seedance_t2v"), savetext(950, "seedance_i2v")]

metrics = (
    "## 📊 客观指标（手动补录）\n\n| 指标 | 可灵 | 即梦 |\n|---|---|---|\n"
    "| 生成耗时(s) |  |  |\n| 一次成功率(%) |  |  |\n| 实际分辨率 |  |  |\n"
    "| 单条成本(¥) |  |  |\n\n> 质量×成本×效率 三角。"
)
g.add_node("Note", (X_OUT, 1150), (340, 260), title="⑤ 客观指标记录表", widgets=[metrics], bgcolor=IO_BG)

# 连线 ---------------------------------------------------------------------
gens = [n_k_t2v, n_k_i2v, n_s_t2v, n_s_i2v]

# 共享 Prompt -> 各生成 prompt 槽
g.link(n_prompt, 0, n_k_t2v, 0, "STRING")
g.link(n_prompt, 0, n_k_i2v, 1, "STRING")
g.link(n_prompt, 0, n_s_t2v, 0, "STRING")
g.link(n_prompt, 0, n_s_i2v, 1, "STRING")
# 负向 -> 仅可灵
g.link(n_neg, 0, n_k_t2v, 1, "STRING")
g.link(n_neg, 0, n_k_i2v, 2, "STRING")
# 输入图 -> 两家 I2V
g.link(n_img, 0, n_k_i2v, 0, "IMAGE")
g.link(n_img, 0, n_s_i2v, 0, "IMAGE")

# 每个生成 -> 保存 + Gemini.video；Rubric -> Gemini.prompt；Gemini -> 评分卡
for k in range(4):
    g.link(gens[k], 0, sv[k], 0, "VIDEO")
    g.link(gens[k], 0, j[k], 1, "VIDEO")
    g.link(n_rubric, 0, j[k], 0, "STRING")
    g.link(j[k], 0, st[k], 0, "STRING")

# 分组 ---------------------------------------------------------------------
g.group("① 评测输入（受控变量）", (X_IN - 20, -420, 600, 1580), "#595")
g.group("② 可灵 Kling 生成", (X_GEN - 20, -60, 460, 650), "#36c")
g.group("③ 即梦 Seedance 生成", (X_GEN - 20, 590, 460, 660), "#c63")
g.group("④ Gemini 评委（每视频独立打分）", (X_JUDGE - 20, -60, 440, 1290), "#393")
g.group("⑤ 评分卡输出 & 客观指标", (X_OUT - 20, -60, 380, 1480), "#777")

here = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(here, "workflow", "kling_jimeng_eval.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(g.to_dict(), f, ensure_ascii=False, indent=2)
print("已生成:", out_path, "| 节点:", len(g.nodes), "连线:", len(g.links))
