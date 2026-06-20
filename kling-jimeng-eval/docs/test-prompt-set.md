# 标准化测试 Prompt 集

> 每条 prompt 针对一种已知的视频生成难点，避免「挑好样本」的偏差。
> 评测时两家使用**完全相同**的 prompt、时长、分辨率、seed。

## T2V 文生视频测试集（10 类挑战）

| # | 挑战类别 | 考察点 | Prompt（中 / 英） |
|---|---------|--------|------------------|
| T1 | 简单运动 | 基础运动自然度 | 一只红狐在雪林中奔跑，逆光晨曦，镜头缓慢跟拍 / A red fox running through a snowy forest at sunrise, camera slowly tracking, volumetric light, photorealistic |
| T2 | 复杂物理 | 物理合理性、碰撞 | 玻璃杯从桌面坠落摔碎，慢动作，碎片四溅 / A glass cup falling off a table and shattering in slow motion, shards flying, high-speed photography |
| T3 | 多主体交互 | 多对象一致与遮挡 | 三个孩子在公园里互相传球奔跑追逐 / Three children running and passing a ball to each other in a park, dynamic interaction |
| T4 | 镜头语言 | 运镜控制、景深 | 无人机环绕拍摄山顶古寺，由近及远拉升 / Drone orbiting an ancient temple on a mountain peak, pulling up and away, cinematic |
| T5 | 精细纹理 | 高频细节保真 | 微距镜头：蜂鸟悬停吸食花蜜，翅膀高速振动 / Macro shot of a hummingbird hovering and feeding on a flower, wings beating rapidly |
| T6 | 文字渲染 | 画面内文字稳定性 | 霓虹灯招牌闪烁显示「OPEN」，雨夜街道 / A neon sign flickering the word "OPEN" on a rainy night street |
| T7 | 风格化 | 非写实风格一致 | 吉卜力风格：少女站在风吹麦田中，长发飘动 / Studio Ghibli style: a girl standing in a windy wheat field, long hair flowing |
| T8 | 人物表情 | 面部微表情、口型 | 特写：一位老人从沉思到露出微笑 / Close-up of an elderly man's face transitioning from contemplation to a warm smile |
| T9 | 流体 | 流体/烟雾模拟 | 热咖啡杯升起袅袅蒸汽，柔和侧光 / Steam rising gently from a hot cup of coffee, soft side lighting, slow motion |
| T10 | 长时一致性 | 长镜头主体不漂移 | 一辆红色跑车沿海岸公路行驶，10秒连续镜头 / A red sports car driving along a coastal highway, continuous 10-second shot |

## I2V 图生视频测试集（5 张标准输入图）

| # | 输入图类型 | 考察点 | 运动 Prompt |
|---|-----------|--------|------------|
| I1 | 人物肖像 | 首帧保真 + 自然微动 | 人物轻轻眨眼并微笑，头发被微风吹动 |
| I2 | 风景照 | 环境动效、不破坏构图 | 云层缓慢飘动，水面泛起涟漪，光线渐变 |
| I3 | 产品图 | 商业级运镜、主体稳定 | 镜头缓慢环绕产品 360°，背景虚化 |
| I4 | 动物照 | 生物运动合理 | 猫咪转头看向镜头，耳朵和胡须轻动 |
| I5 | 插画/二次元 | 风格保持、避免写实化 | 角色头发与衣袂随风飘动，眼睛眨动，保持原画风 |

> 标准输入图请放入 ComfyUI 的 `input/` 目录，并在 `LoadImage` 节点中选择。建议命名：`I1_portrait.png` … `I5_anime.png`。

## 评分记录建议

每条样本生成一行记录，汇总成表：

| 样本ID | 场景 | 维度1 | 维度2 | 维度3 | 维度4 | 维度5 | 可灵加权 | 即梦加权 | 胜出 | 耗时(可/即) | 成本(可/即) |
|--------|------|------|------|------|------|------|---------|---------|------|-----------|-----------|
| T1 | 简单运动 | ... | | | | | | | | | |

跑满 15 条（10 T2V + 5 I2V）即可得到有统计意义的横向对比。
