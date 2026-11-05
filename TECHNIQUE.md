# 技术：能力、工程与真实交付

创作计划采用 [plan-contract.md](references/plan-contract.md)，具体执行沿用 [runtime-and-delivery.md](references/runtime-and-delivery.md)。现有项目、素材、依赖缓存与工具优先，不以重装环境作为默认起点。

## 三个独立层

| 层 | 内容 | 边界 |
| --- | --- | --- |
| 导演与计划 | 观众变化、镜头任务、声音、整片排程 | 不从模板或案例反推故事 |
| 风格包 | 材质、颜色、文字、运动、镜头、声音和原生动作 | 定义效果与实现参考，不自动成为渲染器 |
| 实际制作路线 | 已有引擎、录屏、素材合成或生成工具 | 经实际探测、接入和导出后登记能力 |

本库的查询、导入和校验脚本只用 Python 标准库。上游文本源码位于各包 demo/ 与 vendor/lemo-opuscar/；它们的运行依赖由本片项目按需准备，查询不会运行这些代码或安装依赖。

## 适配执行路线

| 已有路线 | 风格能力接入 | 验证重点 |
| --- | --- | --- |
| HTML／Canvas／WebGL | 可按上游 render(t)、DUR、READY 接口复用绘制与镜头技术 | 字体与素材就绪、任意时间定位、重复帧一致 |
| Remotion／HyperFrames | 将绝对秒与事件映射为宿主时间，复用材质和动作关系 | 实际宿主版本、帧数、音轨与导出 |
| Blender／Three.js | 按镜头拆摄像机、空间、材质、灯光与终态 | 渲染成本、世界与屏幕映射、实际输出 |
| 现有影像与录屏合成 | 保留源入出点、裁切、速率、字幕和证据关系 | 素材来源、遮挡、阅读窗与声音接缝 |

这些是适配合同；runtime.adapter 仍记录实际路线。能力不足先报告具体缺口，不把一个风格包的源码状态当作全部引擎支持。

音频能力按 [独立检测与按需安装](references/audio-capability-setup.md) 进入：Qwen3-TTS 按需生成参考音色旁白，Whisper 承担转写／时间戳候选，ACE-Step 1.5 按需承担音乐理解或生成，HTDemucs 为混音干扰时的可选分离步骤。先清点已有环境、缓存与资源；缺失时提供来源与容量，由 Agent 在任务授权内只补所需组件。检测不能通过启动服务或加载缺失模型触发下载，安装完成也须用本任务短样验证对应功能。Qwen 的平台选择、模型地址、音色和语速配置见 [配音接入指南](references/qwen3-tts-narration.md)。

## 统一时间与资源

画面、音效、旁白、字幕与检查从同一有效排程派生，使用稳定对象和事件 ID。确定性实现按时间计算状态、固定随机种子、等待字体和素材就绪；顺序、倒序和随机定位对照后再声称可重复。

上游渲染器默认多 worker；本库制作默认串行、一个任务执行实例，明确设置并发上限。可复用现有浏览器、渲染器、端口和缓存时复用，失败先读日志，收尾只处理本任务资源。网站操作遵守宿主 Chrome 路由。

上游的 readcheck、ASR、混音与渲染代码可供项目适配；现有 check_delivery、film_probe、audio_event_audit、explainer_timing_audit 分别检查文件、媒体与声明排程。缺少所需接口时登记未检查，不能当作通过。

## 计划与实际执行的连接

按 [执行合同](references/execution-contract.md) 使用可选 execution 绑定，`execution_contract.py compile` 从当前主计划派生帧范围并核实现文件，`assets/execution/runtime.mjs` 提供无依赖采样与适配入口。项目负责真实绘制和引擎状态回读；`audit` 只核所给状态及双语字幕框，`impact` 沿依赖给出局部重做建议。接口、采样和哈希不证明视觉或听感，原有计划与引擎继续可用。

## 从源码进入项目

先读选中包的 STYLE.md、STYLE.upstream.md；确定本片意图后读 DEMO.md，按需复制 demo/ 中的实现到用户工程。修正 LIB、导入、资源和构建路径，按当前官方文档与本地版本核实 API。不要在库内执行 build.sh，不直接照搬上游模型、声音服务、素材或发布脚本。

素材取用见 [asset-routing.md](references/asset-routing.md) 和 [production-tool-contract.md](references/production-tool-contract.md)；角色、空间与跨引擎组装见 [scene-tool-composition.md](references/scene-tool-composition.md)。

## 音乐驱动三维世界

给音乐、主题、风格时按 [专项流程](references/music-driven-world.md) 复用 `music_world.py` 与 `assets/music-world/starter`。分析只产候选，编排与主题适配由当前Agent完成；两条起步路线分别实测，不把源码存在当作已生成成片。

## 物体形象构建

内容需要具体物体或现象时，按 [构建方法入口](references/object-construction.md) 选择元素级配方。水与液体按形态、光学、运动、接触和镜头关系构建；先读 [设计方法](objects/water-liquid/METHOD.md)，再按需读 [工程实现与复刻](objects/water-liquid/ENGINEERING.md)。沿已有项目选择实现，复用主计划、执行绑定与实际验收，不以方法存在代表能力已经可用。
