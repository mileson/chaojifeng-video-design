# 从表达指导组合到实现

原有 motion 目录提供12种属性变化；expression 目录提供64项跨层表达指导（含11项知识讲解层、14项发布片元素）；recipe目录提供22类组合起点。新层不替换底层稳定ID，不把来源视频或提示词当可执行插件。

## 按问题查询

先查场景候选，再按当前问题查一到三项。将 SKILL_ROOT 换成实际路径。

```text
python3 SKILL_ROOT/scripts/catalog.py --kind expression list --scenario knowledge-explainer
python3 SKILL_ROOT/scripts/catalog.py --kind expression get narrative.follow-unit
python3 SKILL_ROOT/scripts/catalog.py --kind expression get transition.shared-morph
python3 SKILL_ROOT/scripts/catalog.py --kind expression get sound.event-collision
python3 SKILL_ROOT/scripts/catalog.py --kind recipe list --scenario brand-film
```

| 层 | 要解决的问题 | 示例ID |
| --- | --- | --- |
| 叙事 | 按什么顺序组织变化 | narrative.goal-proof、narrative.follow-unit、narrative.energy-arc |
| 相机 | 视点怎样提供信息 | camera.focus-frame、camera.waypoint-travel、camera.velocity-match |
| 转场 | 前后镜头如何保持关系 | transition.shared-morph、transition.match-cut、transition.occlusion-reveal |
| 视觉／动画 | 结构、数量、材质怎样变化 | visual.quantity-progress、visual.structure-separate、animation.fill-transfer |
| 文字 | 文字何时被读、何时参与表演 | text.semantic-emphasis、text.counter-rotate、text.read-then-move |
| 视觉强调 | 框准真实目标，标签避让并与运镜保持归属 | visual.target-callout，配合camera.focus-frame与text.semantic-emphasis |
| 声音 | 节拍、动作与频段怎样关联 | sound.beat-map、sound.event-collision、sound.band-response |
| 交互 | 输入怎样变成可复现的视频 | interaction.direct-manip、interaction.to-video |
| 风格／生产 | 如何维持规则与可导出性 | style.token-contract、production.time-function、production.loop-seam |
| 知识讲解 | 抽象知识或资讯怎样讲清、讲准、一层一层讲 | knowledge.object-is-explanation、knowledge.layered-reveal、knowledge.truth-ledger、knowledge.evidence-board |
| 发布片 | 产品发布片的痛点、转折、自证、行动怎样编成一条弧 | narrative.pain-to-verdict、sound.pivot-drop、narrative.parallel-promise、narrative.cta-as-action、production.dwell-budget |

## 看清抽象层

查看 tier、source_relation、inputs、parameters、composition、required_capabilities、fallback 和 verification_questions。parameters 中的 design-control 是设计选择，不是已经实现的API或数值范围。required_capabilities 是落地需要探测的语义能力，不能抄入 runtime.capabilities 冒充实测。

关系算子、时间约束、领域操作、组合配方与生产规则可以共同出现。例如先让文字读完再移动，是时间约束；围绕主体排一圈媒体，是组合布局；拆解科学结构，需要领域正确性。不要把它们全转成同一层“动画函数”。

## 把视觉角度变成代码中的关系

先用 [从内容到画面](design-method.md#场景视觉角度代码与动效一起推导) 选定表达，再拆出哪些状态由输入或时间决定、哪些可见变化由这些状态推导。“用某引擎做动画”仍缺少构建方式；实现说明要能回答对象怎样生成和关联、哪个变量改变什么、动作为什么有这个顺序。以下是机制选择，不是某个引擎的 API 或已验证能力。

| 画面需要的关系 | 可考虑的代码方式 | 必须保留的语义 |
| --- | --- | --- |
| 多个元素共同指向或响应一个目标 | 保存目标标识与几何锚点，从同一状态推导方向、位置、强调和响应 | 目标切换时所有相关元素仍指向同一对象；响应延迟有表达理由 |
| 对象穿过空间、交接或随镜头保持归属 | 路径采样、父子变换、共享坐标映射；明确世界、对象和画面空间 | 对象身份、接触点和运动方向连续，标签不因运镜脱离对象 |
| 结构展开、内容揭示或遮挡变化 | 分层几何、裁切／遮罩、可见性与状态转换 | 揭示顺序与信息依赖一致，遮挡不能删掉必要条件或证据 |
| 群体形成秩序或表现数量与差异 | 规则排布、分组、参数场或实例生成，数据驱动时绑定真实数值 | 保留分组依据和数量含义，不能用装饰密度冒充统计比例 |
| 材质、线条与形变参与风格 | 给纹理指定附着空间，按对象结构组织描边、形变和局部细节 | 材质随对象保持归属，文字可读；运动符合选定物性而非统一套弹性 |

例如“当前目标”可以是一次状态变化：代码先取得该目标的边界和锚点，再派生主体朝向、强调范围与响应动作；各项共享语义状态，时间上允许有意错开。另一场景可能需要“任务进度”或“条件是否满足”，不必沿用目标跟随。保留稳定对象身份，明确每个变化属性的控制者及合成方式，避免镜头、布局和局部动画争写同一属性。只有运动轨迹相同、语义状态彼此独立时，仍可能出现错指、提前响应或错误因果。

将一次表达按需要分成初态、触发、主变化、次级响应、落定与交接；阶段可以合并或省略。缓动描述怎样到达，速度和停留决定什么能被看清，次级运动体现受力、反馈或情绪。先保证主体和结果可辨，再调整表现力，不给每层都安排持续循环。交互输入转为视频时，使用下节的固定输入与时间规则；实际技术路线由 [TECHNIQUE](../TECHNIQUE.md) 和运行能力决定。

验收同时看关系与运动：关键帧核主体、锚点、遮挡和结果；连续播放核触发顺序、速度、响应与阅读时间。关系复杂或能力未知时，可在制作中先局部验证，再检查上下镜接力，沿用本次 direct／staged 约定。记录实测范围，不能把可写成代码等同于当前执行器已经支持或最终画面已经有效。

## 落地顺序

1. 确认它帮助哪条故事节拍或信息关系；不适合就跳过目录自由设计。
2. 将语义参数变成项目可执行的时间、坐标、材质、声音与输入。复杂效果可先试短段；明确direct时直接制作整片并内部检查修复，不强制试片。
3. 用已有 motion 或项目实现承载；没有现成动效的，用 custom 并填写 channels、implementation、composition_reason 等原合同要求。
4. 将选择记在 design.expression_ids、design.recipe_id 或镜头说明中。目录引用只验证选择是否存在，不自动排镜头或驱动渲染器。
5. 实际核验关键帧、连续运动、声音与语义。来源只演示局部时，不能借此宣布全套实现通过。

相机与对象同时运动需明确坐标空间和合成；匹配剪辑需对应构图／方向／声音；弹性只在适合对象材质时使用；图形数量与面积须依据数据。粒子深度化、三维结构、流体与人物表演能力不足时，按目录回退，并说明损失。

交互演示不是自动可导出的视频。需要固定输入、状态以及适用的随机种子与时钟，再检查受控操作和最终播放。只有执行器声明可随机 seek 时才检查跳转一致性；不支持时可用受控录屏或顺序渲染，并记录限制。交互来源仅提供输入机制，固定输入的视频适配是本Skill的设计建议。

## 验证范围

目录初始为 guidance，design=authored；preview/exported 依实际范围登记。小型索引示意不覆盖全部条目。64项不等于64个已渲染特效，22类配方也不保证任意组合。新增源不能自动提升历史验证状态，升级需保留反例与失效条件。标注轨道与检查范围见 [视觉强调](visual-emphasis.md)；采样几何无碰撞不等于所有帧、字形和语义已经通过。

## 知识讲解的组合入口

讲解抽象知识或资讯时，先读 [物即解释](knowledge-visualization.md)，再选配方：机制类用 `object-explainer`，要把一个概念分层讲透用 `layered-concept-reveal`，资讯用 `evidence-board-brief`。11项 `knowledge.*` 表达是设计指导：它们规定什么要写进 [知识包](knowledge-pack.md)、什么要在画面里兑现，不是已安装的动效。前半段的行业规范、术语与受控表达见 [行业规范先行](domain-standards.md)，层次安排见 [逐层递进](layered-reveal.md)。

选了 `knowledge.*` 表达就写 `plan.knowledge`，并运行 `validate_plan.py`；这些检查只核结构、引用和文字的机械问题，不证明事实为真、比喻贴切或观众看懂。

概念知识科普用 `knowledge-music-explainer`，按 [科普编排](knowledge-music-direction.md) 选择字幕／旁白与direct／staged，从配方音乐池、当前默认或用户指定曲目反推声画编排，沿现有知识包和声音合同组织，不把试片确认设为通用门禁。

用Rap／嘻哈／说唱讲知识时自动选 `knowledge-rap-explainer`，按 [说唱科普](knowledge-rap-direction.md) 逐句关联事实、实际唱词、素材、重音和动作落定；背景音乐科普不切Rap。需要角色、三维、灯光与跨工具合成时按 [场景与工具组合](scene-tool-composition.md) 选择单一或多种路线，最终看真实MP4并检查声音，目录示意不代表工具已接入。

## 产品表达的组合入口

两份新增配方与边界扫描见 [产品表达](product-expression.md)。同框换证据、递进困难和语义槽是组合规则；底层仍复用原12动效，不把每种标题/播放器/品牌外观建立为新原子。镜头注记不扩大机器校验或实际效果声明。

## 发布片的组合入口

做30秒级的产品发布片或多功能串联时，先读 [发布片语法](launch-film-grammar.md)，再选配方：整片情绪弧用 `launch-film-arc`，三到四个功能逐章证明用 `feature-chapter-reel`；`product-task-proof` 仍负责“真实任务与证据”的最小结构，两者不重复。14项发布片元素同样是设计指导，不是已安装动效：它们给出观察依据、迁移写法和失败信号，数值只是来自一部参考片的起点。声音一律先写事件表再排时间线，用 `audio_event_audit.py` 核对，测的是起音时刻，不是听感。研究另一部参考片的方法见 [参考片研究](reference-film-study.md)。

产品宣传由歌词和乐段共同讲述时，选择 [产品音乐叙事](product-music-story.md) 的 `product-music-story`，沿现有动作、主体连续和声音表达组合；先核片型适配与功能主张，再选择素材、开场和实际声音。它跨用产品、品牌与音乐场景，不新增底层动效或必填合同；新配方仍待实际成片与效果验证。
