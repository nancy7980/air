# 可灵 vs 即梦 · ComfyUI 视频生成评测工作流

一套用于横向评测 **可灵 Kling** 与 **即梦 Jimeng** 视频生成能力的 ComfyUI 工作流 + 评测体系，
面向「可灵视频模型产品经理」面试作品集。强调 **受控变量、多维 Rubric、LLM 评委自动打分 + 客观指标交叉验证**。

```
kling-jimeng-eval/
├── workflow/kling_jimeng_eval.json     # ★ ComfyUI 工作流（导入即用）
├── build_workflow.py                   # 工作流生成器（改结构后重跑生成 JSON）
├── docs/
│   ├── evaluation-framework.md         # 评测框架：维度/权重/评分方式/流程（PM 核心）
│   └── test-prompt-set.md              # 标准化测试 Prompt 集（10 T2V + 5 I2V）
├── dashboard/comparison-dashboard.html # 结果对比看板（雷达图，自包含可离线）
└── README.md
```

---

## 工作流长什么样

```
① 共享输入(受控)        ② 生成              ④ 保存+抽帧         ⑤ LLM评委 → 评分卡
┌─ Prompt ─┐         ┌ 可灵 T2V ┐        ┌ 抽8帧 ┐         ┌ T2V 对比打分 → JSON
├─ 运动描述 ─┼────────┤ 可灵 I2V ┼────────┤ 抽8帧 ┼────────┤
├─ 输入图  ─┤         ├ 即梦 T2V ┤        ├ 抽8帧 ┤         └ I2V 对比打分 → JSON
└─ Rubric ─┘         └ 即梦 I2V ┘        └ 抽8帧 ┘         + 客观指标记录表
```

一份输入，两家在**完全相同参数**下并排生成，自动抽帧交给多模态大模型按 5 维 Rubric 打分。

---

## 快速开始

### 1. 导入工作流
ComfyUI 界面 → 菜单 **Load** → 选择 `workflow/kling_jimeng_eval.json`（或直接把文件拖进画布）。

### 2. 安装所需节点
导入后若出现红色「缺失节点」，用 **ComfyUI Manager → Install Missing Custom Nodes** 安装。本工作流用到：

| 节点 | 来源 | 说明 |
|------|------|------|
| `KlingTextToVideoNode` / `KlingImageToVideoNode` | **ComfyUI 官方 API Nodes**（内置） | 新版 ComfyUI 自带「API Nodes」，登录后即可用可灵 |
| `JimengTextToVideoNode` / `JimengImageToVideoNode` | **社区自定义节点** | 通过 ComfyUI Manager 搜 “Jimeng / 即梦 / Dreamina / 火山引擎”安装；若无现成节点，可用通用 HTTP 请求节点对接火山引擎即梦 API（见下方备注） |
| `VHS_VideoToImages` | **ComfyUI-VideoHelperSuite** | 抽取关键帧 |
| `LLMVideoJudge` | **多模态 LLM 节点**（占位类型） | 用任一支持「图像+文本」的 LLM 节点替代：如 ComfyUI-Ollama 的 Vision、或 Claude / GPT-4o API 节点。把两家关键帧 + Prompt + Rubric 输入，输出评分 JSON |
| `SaveVideo` / `SaveText` / `Note` / `LoadImage` / `PrimitiveNode` | ComfyUI 内置 | 输入/输出/保存 |

> **诚实备注**：`JimengTextToVideoNode` 与 `LLMVideoJudge` 是为表达工作流结构而使用的命名占位。
> 即梦官方未提供统一 ComfyUI 节点，落地时二选一：
> (a) 安装社区即梦节点；(b) 用通用 HTTP/API 节点（如 ComfyUI 的 `HTTP Request` 类节点）按火山引擎即梦视频生成 API 文档对接。
> LLM 评委同理，用你已有的多模态 LLM 节点接上即可——拓扑不变。

### 3. 配置 API Key
- **可灵**：快手 [可灵开放平台](https://app.klingai.com) 申请 API Key；新版 ComfyUI 在「Settings → API Nodes / 登录」中配置。
- **即梦**：[火山引擎](https://www.volcengine.com) 开通即梦/视频生成服务，获取 AccessKey/SecretKey，填入对应节点。
- **LLM 评委**：填入你所用大模型的 API Key（或本地 Ollama 无需 Key）。

### 4. 填入受控输入（左侧绿/灰色组）
- `共享 Prompt`：从 `docs/test-prompt-set.md` 取一条
- `共享运动/负向描述`：保持两家一致
- `I2V 共享输入图`：把标准图放入 ComfyUI `input/` 目录后在 `LoadImage` 选择
- `评分 Rubric`：已预置 5 维标准，一般无需改

> ⚠️ 公平性关键：两家的 prompt / 图 / 时长 / 分辨率 / seed 必须一致，已通过「共享输入节点」从源头保证。

### 5. 运行并读取结果
点 **Queue**。完成后：
- 视频保存在 `output/eval/`
- 评分卡 JSON 保存为 `output/eval/scorecard_t2v.json`、`scorecard_i2v.json`

### 6. 汇总到看板
打开 `dashboard/comparison-dashboard.html`：
- 把两家视频路径填入 `<source src="">`（或拖入）
- 按评分卡 JSON 填 5 维分数 → 雷达图 / 加权总分 / 胜出方实时更新
- 补充客观指标（耗时/成功率/成本）与结论

---

## 跑一轮完整评测的建议
1. 按 `test-prompt-set.md` 依次跑 10 条 T2V + 5 条 I2V
2. 每条导出一张看板截图 + 评分卡 JSON
3. 汇总各维度均分、胜率、强弱场景
4. 产出一页结论：**两家强弱场景图 + 给本方产品的 3 条迭代建议**（这是面试官最想看的部分）

---

## 修改工作流结构
工作流 JSON 由 `build_workflow.py` 生成。若要增删节点/调整布局：

```bash
python build_workflow.py   # 重新生成 workflow/kling_jimeng_eval.json
```

脚本用集中式 link-id 管理，避免手改 JSON 时连线错位。

---

## 设计取舍（面试可讲）
- **为什么 LLM 评委为主**：视频质量本质是体感，多模态 LLM 能按统一 Rubric 给出可解释、可复现的多维评分，比纯算法指标更贴近用户感知。
- **为什么仍要客观指标**：LLM 是「观点」，需用耗时/成功率/成本兜底，构成「质量×成本×效率」的产品决策三角。
- **为什么强调受控变量与盲评**：消除 prompt 差异与品牌先验，让结论可信。
- **局限**：抽帧评判会漏瞬时瑕疵、LLM 评分需小样本与人工对齐。详见 `docs/evaluation-framework.md` 第 8 节。
