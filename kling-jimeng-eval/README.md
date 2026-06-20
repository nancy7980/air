# 可灵 vs 即梦 · ComfyUI 视频生成评测工作流（云端原生版）

一套横向评测 **可灵 Kling** 与 **即梦（Seedance）** 视频生成能力的 ComfyUI 工作流 + 评测体系，
面向「可灵视频模型产品经理」面试作品集。强调 **受控变量、多维 Rubric、LLM 评委自动打分 + 客观指标交叉验证**。

> **本版本为 ComfyUI Cloud 官方云端优化**：全部使用官方 API / 合作节点 + 核心内置节点，
> **无需安装任何自定义节点、无需外网 HTTP**，导入即可跑。

```
kling-jimeng-eval/
├── workflow/kling_jimeng_eval.json     # ★ ComfyUI 工作流（导入即用，全官方节点）
├── build_workflow.py                   # 工作流生成器（改结构后重跑生成 JSON）
├── docs/
│   ├── evaluation-framework.md         # 评测框架：维度/权重/评分方式/流程（PM 核心）
│   └── test-prompt-set.md              # 标准化测试集（10 T2V + 5 I2V）
├── dashboard/comparison-dashboard.html # 结果对比看板（雷达图，自包含可离线）
└── README.md
```

---

## 一个关键设计：为什么用 Seedance 代表即梦

ComfyUI 官方**没有**叫「即梦/Jimeng」的节点，但**即梦的视频能力由字节跳动 Seedance 模型驱动**，
而官方已内置 **ByteDance Seedance** 合作节点。所以在云端评测 Seedance = 评测即梦的同源能力，
比依赖不稳定的社区即梦节点更可靠，面试时也能讲清取舍。

---

## 工作流结构（全官方内置节点）

```
① 共享输入(受控)        ② / ③ 生成              ④ 评委（直接收视频）      ⑤ 评分卡
┌─ Prompt ─┐         ┌ 可灵 T2V ┐              ┌ GeminiNode ─5维打分 ┐  → scorecard_kling_t2v.json
├─ 负向    ─┼─────────┤ 可灵 I2V ┼──video──┬────┤ GeminiNode          ┼  → scorecard_kling_i2v.json
├─ 输入图  ─┤         ├ 即梦 T2V ┤         │    │ GeminiNode          ┼  → scorecard_seedance_t2v.json
└─ Rubric ─┘         └ 即梦 I2V ┘         └────┤ GeminiNode          ┘  → scorecard_seedance_i2v.json
                          └─ SaveVideo（各自保存 mp4）                     对比在看板里完成
```

每个生成视频**直接喂给一个 GeminiNode**（官方节点自带 `video` 输入），按 Rubric 打绝对分，
省掉抽帧/合帧节点，云端最稳。

| 角色 | 官方内置节点（已核对 ComfyUI 源码 NODE_CLASS_MAPPINGS） | 是否需安装 |
|------|------|-----------|
| 可灵 T2V | `KlingTextToVideoNode` | ❌ 官方内置 |
| 可灵 I2V | `KlingImage2VideoNode`（注意是 Image**2**Video） | ❌ 官方内置 |
| 即梦 T2V | `ByteDanceTextToVideoNode`（Seedance） | ❌ 官方内置 |
| 即梦 I2V | `ByteDanceImageToVideoNode`（Seedance） | ❌ 官方内置 |
| LLM 评委 | `GeminiNode`（多模态，直接收视频） | ❌ 官方内置 |
| 输入/输出 | `LoadImage` `PrimitiveNode` `SaveVideo` `SaveText` `Note` | ❌ 核心内置 |

> ⚠️ 这些是**官方内置 API/合作节点的精确类名**——不要用社区同名节点（如 `Gemini`、`ByteDance2*`、
> `KlingImageToVideoNode`），那些会被 Comfy Cloud 判为"不支持的节点包"。若云端某节点版本更新导致参数变化，
> 双击画布搜 `Kling` / `Seedance` / `Gemini` 选**官方**节点替换即可，连线拓扑不变。

---

## 在 ComfyUI Cloud 上使用

### 1. 导入工作流
登录 [ComfyUI Cloud](https://www.comfy.org) → **Workflows / Open** → 上传或拖入
`workflow/kling_jimeng_eval.json`。

### 2. 开通 API 额度 / 登录
云端的官方 API 节点按调用计费（credits）：
- **可灵 Kling**、**即梦 Seedance**、**Gemini** 都是官方合作节点，在云端账号里**充值/授权**即可，
  无需自己填第三方 Key（这正是官方云端相比本地的便利）。
- 若节点要求选择具体模型版本，按节点下拉选你已开通的型号。

### 3. 填入受控输入（左侧①区）
- `共享 Prompt`：从 `docs/test-prompt-set.md` 取一条
- `共享运动/负向描述`：两家一致
- `I2V 共享输入图`：上传到云端 input 后在 `LoadImage` 选择
- `评分 Rubric`：已预置 5 维标准，一般无需改

> ⚠️ 公平性关键：两家 prompt / 图 / 时长 / 分辨率 / seed 一致，已由「共享输入节点」从源头保证。

### 4. 运行并读结果
点 **Queue**。完成后：
- 视频保存在 `output/eval/`
- 评分卡 JSON：`output/eval/scorecard_t2v.json`、`scorecard_i2v.json`

### 5. 汇总到看板
打开 `dashboard/comparison-dashboard.html`：填入两家视频与 5 维分数 →
雷达图 / 加权总分 / 胜出方实时更新，再补客观指标与结论。

---

## 云端注意事项（实测会踩的点）
- **"缺少输入·图像"不是 bug**：`LoadImage` 需要你先上传一张 I2V 输入图并在节点里选中，否则会报缺图。
- **评委直接收视频**：`GeminiNode` 自带 `video` 输入，已直接把生成视频接进去，无需抽帧；
  视频较长时 Gemini 会自动采样，建议生成时长设 5s 控制 token。
- **负向提示**：Seedance 节点无独立 negative 输入，负向描述请并入正向 prompt；可灵保留独立 negative。
- **节点版本/参数**：官方节点会迭代，若某节点参数对不上，双击画布搜官方节点重连即可（拓扑不变）。
- **绝对分 vs 对比分**：本版每个视频独立打绝对分，A/B 对比在看板完成（更少偏见、云端更稳）。

---

## 跑一轮完整评测的建议
1. 按 `test-prompt-set.md` 依次跑 10 条 T2V + 5 条 I2V
2. 每条导出看板截图 + 评分卡 JSON
3. 汇总各维度均分、胜率、强弱场景
4. 产出一页结论：**两家强弱场景图 + 给本方产品的 3 条迭代建议**（面试官最想看的部分）

---

## 修改工作流结构
```bash
python build_workflow.py   # 重新生成 workflow/kling_jimeng_eval.json
```
脚本用集中式 link-id 管理，避免手改 JSON 时连线错位。

---

## 设计取舍（面试可讲）
- **为什么用官方 Seedance 代表即梦**：即梦视频由 Seedance 驱动，官方节点同源且云端稳定。
- **为什么 LLM 评委为主**：视频质量本质是体感，多模态 LLM 按统一 Rubric 给出可解释、可复现的多维评分。
- **为什么仍要客观指标**：LLM 是「观点」，用耗时/成功率/成本兜底，构成「质量×成本×效率」决策三角。
- **为什么强调受控变量与盲评**：消除 prompt 差异与品牌先验，让结论可信。
- **局限**：抽帧评判会漏瞬时瑕疵、LLM 评分需小样本与人工对齐。详见 `docs/evaluation-framework.md` 第 8 节。
