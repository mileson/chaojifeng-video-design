# 按任务加载方法

先按观众所得选择场景，再读当前任务所需的一行。风格与场景可跨用，说明适配理由并重新核对事实、素材、阅读和能力。

| 场景 | 观众所得与主要方法 |
| --- | --- |
| product-promo | 看见结果、理解价值、记住产品；读 [产品宣传视频](product-promo-direction.md)，选参考素材、模板名称或产品源码入口；首尾两幕纳入必检 |
| product-demo | 看懂真实任务、操作与结果；读 [产品表达](product-expression.md) |
| knowledge-explainer | 理解概念、关系与过程；读 [物即解释](knowledge-visualization.md)、[行业规范](domain-standards.md)、[逐层递进](layered-reveal.md)和[知识包](knowledge-pack.md) |
| news-brief | 分清事件、来源、日期、变化与未知；沿用知识包，额外核对时效与事实画面 |
| interview-commentary | 听懂一段外文访谈的关键判断并对照自己；读 [访谈解读](interview-commentary-direction.md)，引语、来源与本人判断分层，图形或卡片结构对应这句话的逻辑结构 |
| image-story | 用给定图片建立顺序与重点；读 [素材表演与调度](asset-motion-direction.md)，保留主体与裁切安全 |
| story-video | 保持人物、事件与转折连续；读 [镜头生产统筹](shot-production.md) |
| feature-motion | 展示初态、触发、变化与终态；读 [视觉强调](visual-emphasis.md)和[产品表达](product-expression.md) |
| brand-film | 建立品牌感受与视觉记忆；按 [创意导演](creative-direction.md) 区分事实、愿景和象征 |
| music-visual | 用乐段、动机、变奏与释放组织体验；先读 [歌曲视觉导演](song-visual-direction.md)和[音乐镜头与运动编排](music-shot-choreography.md)，再读 [音乐导演](music-direction.md)与[声音和节奏](sound-and-rhythm.md) |

## 按明确意图补读

| 用户意图或制作条件 | 路由与约束 |
| --- | --- |
| 给参考素材制作产品宣传片 | product-promo；先读 [参考片研究](reference-film-study.md)和[产品宣传视频](product-promo-direction.md)，提炼首尾编排、主体结构与声音，按当前产品事实适配 |
| 按“极简左右讲解”或已登记模板名称制作 | product-promo；精确查询 recipe 的名称／别名／ID，加载[极简左右讲解](../templates/product-split-explainer.md)，无需另找参考片；未知名称不静默替换 |
| 给产品源码和几项选题侧重点，做说明类产品宣传片 | product-promo；先读 [源码说明片](product-source-explainer.md)，精确查询 recipe `product-source-explainer`（名称“源码说明片”），加载[源码说明片模板](../templates/product-source-explainer.md)；用 `product_ledger.py` 建账本并检查闭合，真实证据按证据阶梯取，视觉语法沿用极简左右讲解；叙事默认先抛观众的麻烦与疑问、再揭晓产品、再讲怎么操作（开场句登记为 `framings`，顾虑不能被说成产品承诺）；旁白声音按 [讲解配音的声音方向](narration-voice-direction.md)：超级峰自己的产品默认用其授权的本人声音，语速偏快、有起伏，替他人制作或授权不明才用通用声 |
| 把外文访谈、演讲或播客解读成中文视频，或复刻“引语 + 卡片 + 本人判断”形式 | interview-commentary；先读 [访谈解读](interview-commentary-direction.md)，精确查询 recipe `interview-commentary-explainer`（名称／别名／ID），加载 [访谈解读模板](../templates/interview-commentary.md)；可执行流水线用 `chaojifeng-interview-commentary`；本人音色只用于授权的本人讲解，听感未听审保持 `not_checked` |
| 诗词、乐器、景物与立体文字共同表达 | music-event-performance；在音乐驱动流程中补读 [诗词音乐世界](poetry-music-world.md)，按当前唱词和事件建立意象、运动映射与接触关系 |
| 用三维对象响应音乐，主题或风格可由歌曲推导 | music-event-performance 的音乐先行分支；先读 [歌曲视觉导演](song-visual-direction.md)和[音乐镜头与运动编排](music-shot-choreography.md)，再读 [音乐驱动三维世界](music-driven-world.md)，默认连续完成；理论主题补知识表达 |
| 概念、原理或机制需要音乐推进 | knowledge-music-explainer；读 [概念知识科普编排](knowledge-music-direction.md)，先按所选曲目的实际结构反推知识层与镜头 |
| 用 Rap／嘻哈／说唱讲知识、历史、机制、产业或社会议题 | 自动选 knowledge-rap-explainer；读 [说唱科普](knowledge-rap-direction.md)。背景音乐需求不自动切 Rap，产品宣传按主要目标选配方 |
| 产品宣传需要歌词、乐段组织动作或副歌变奏 | product-music-story；读 [产品音乐叙事](product-music-story.md)，先核任务与歌词主张 |
| 信息流科普或宣传 | 默认读 [开场设计](opening-design.md)，检查首帧、前三秒、声音承接与正文兑现 |
| 30 秒级发布片、多功能章节串联 | 读 [发布片语法](launch-film-grammar.md)，按需选 launch-film-arc／feature-chapter-reel；短单功能片只取合适部分 |
| 角色表演、电影运镜、空间、灯光反射或跨引擎组装 | 读 [场景与工具组合](scene-tool-composition.md)，先写表情、姿势、移动与终态，再建场景 |
| 角色、动作、道具、环境或声音资产 | 读 [制作工具合同](production-tool-contract.md)，先项目缓存与授权库，后补缺；HDRI 用同镜对照，日语旁白与 BGM 分流 |
| 界面重点、操作解释与动态标注 | 读 [视觉强调](visual-emphasis.md)，定义目标与保护区，核相机映射、标签跟随和遮挡 |
| 旁白、本人声音或角色讲解 | 读 [讲解导演](explainer-narration.md)；定音色、语速、激情感、配乐与音效取向，或用户反馈配音单调、偏慢时，先读 [讲解配音的声音方向](narration-voice-direction.md)；需要本地参考音色配音时读 [Qwen 配音接入](qwen3-tts-narration.md)，由 Agent 检测并按需下载；先清晰稿件和获准参考，再取得真实音频，不强制人物出镜；云端克隆音色是收费路线，先写预算上限，本地失败不悄悄切换 |
| 寻找、生成、组合或分层素材 | 读 [素材选择](asset-routing.md)；独立移动、装回与跨镜接力再读 [素材调度](asset-motion-direction.md) |
| 研究参考成片与创作过程 | 读 [参考片研究](reference-film-study.md)，保留指令、版本、失败与产物对应，区分观察、测量、推断和未听审 |
| 组合局部表达与动作 | 读 [表达组合](expression-method.md)；动作、关系、约束、配方和生产规则分别使用，查询条目不等于调用特效 |

配方音乐配置运行时读取：用户指定 → 项目已选 → 当前配方默认。单次选曲不改候选池，明确加入候选或设为默认后才改配置；换曲重新量时，源缺失不静默替换。完整规则见 [音乐导演](music-direction.md)。
