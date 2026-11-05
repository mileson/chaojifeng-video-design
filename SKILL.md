---
name: chaojifeng-video-design
description: 设计和制作产品宣传（参考素材或模板名称两种入口）、产品演示、知识讲解（含 Rap／说唱）、外文访谈解读、资讯、图片成片、故事、功能动效、品牌短片与音乐视觉视频。支持选择或扩展视频风格、组合动效、强化前三秒、素材调度、音乐编排、参考片研究和局部修改；从导演意图到可编辑计划、制作、审片及可播放成片，也可只交方案或分镜。模型与引擎中立，按任务加载风格包和技术能力。
---

# 超级峰的视频设计方法论

先决定观众要理解或感受到什么，再组织镜头、素材、文字与声音。故事属于当前题材，风格提供材质和表达语法，实现由实际可用工具完成。

## 先确定范围

1. 读 [已确认经验](data/memory.md)、用户输入和项目适用说明。复用已有工程、素材、进程与渲染器，核实资源归属。
2. “做视频、宣传片、生成成片”交付可播放视频、必要编辑源和验证摘要。只要方案、分镜或单个动效时按明确范围完成。已有作品局部修改保留其他内容和稳定 ID。
3. 从上下文补齐受众、观众变化、事实、品牌、素材、画幅、时长、声音和用途。新视频未指定画幅时默认 **9:16（1080×1920）**；用户明确 16:9、1:1 或其他比例时优先采用。局部修改已有作品保留原画幅，除非用户要求改变。写分镜前确定宽高，按目标画幅安排主体、文字和字幕，不先做横版再整体缩小或裁切。参考片的比例仅作为观察，用户只参考风格时不自动继承。自行决定低影响选择；事实、必要素材或费用授权真正阻断结果时再问。
4. 明确 direct 时连续完成整片、内部检查和必要返修，不增加试片或方向确认门禁。只有用户要求 staged 才在约定节点等待。两种模式均检查事实、阅读、声音与实际导出。

## 按职责加载

| 要解决的问题 | 读取与动作 |
| --- | --- |
| 故事、镜头、声音、观众变化 | [DIRECTOR.md](DIRECTOR.md)，再按 [任务路由](references/task-routing.md) 加载相关方法 |
| 产品宣传、参考片套用、按模板名称制作，或给产品源码和选题侧重点 | 先读 [产品宣传视频](references/product-promo-direction.md)；参考素材先拆首幕、主体和尾幕，模板名称精确查询配方；“极简左右讲解”加载 [完整模板](templates/product-split-explainer.md)；给了产品源码目录和侧重点时读 [源码说明片](references/product-source-explainer.md)，配方 `product-source-explainer`（名称“源码说明片”，别名“源码驱动产品宣传”“产品源码说明片”）加载 [完整模板](templates/product-source-explainer.md)，先建事实账本、按证据阶梯取真实证据，开场默认先抛观众的疑问再揭晓产品，渲染、取证与编码的工程细节读 [真实界面成片工程](references/real-ui-film-engineering.md)；均连续完成声画制作与实际验收 |
| 把外文访谈、演讲或播客解读成中文视频，或复刻“引语 + 卡片 + 本人判断”形式 | 先读 [访谈解读](references/interview-commentary-direction.md)；配方 `interview-commentary-explainer`（名称“访谈解读”，别名“超级峰解读”“黄叔精读”）加载 [完整模板](templates/interview-commentary.md)；选题、下载、转写、配音、渲染、封面的可执行流水线用 `chaojifeng-interview-commentary`（画面以图表为主，铺底与音效默认用本机 ACE 生成，收尾用固定的品牌落款）；本人音色只用于授权的本人讲解，听感未听审保持 `not_checked` |
| 给歌曲设计音乐视频，包括未指定主题或风格 | 先读 [歌曲视觉导演](references/song-visual-direction.md)、[声画事件模型](references/music-event-model.md)和[音乐镜头与运动编排](references/music-shot-choreography.md)，有演唱先取得歌词时间线，再用[音乐导演编排模板](templates/music-direction.md)或已有计划落实多层声音锚点、事件前后变化、视线与运镜、动作峰值、空间材质及实际感知验收 |
| 匹配剪辑、动作接力或音乐转场 | 读 [匹配剪辑与音乐转场](references/match-cut-relay.md)，在现有事件卡明确出镜／入镜状态、共同含义、动作阶段与落定；由统一排程驱动代码实现，预演并核对实际切口 |
| 有旁白、歌词或需要字幕 | 读 [字幕导演与配色](references/subtitle-direction.md)，在分镜阶段确定语言、语义分组、场景锚点、视线接力、阅读窗和音乐落点，优先探索空间文字与动态排版，保留固定字幕选项 |
| 需要生成旁白，或缺少转写、音乐理解、人声分离能力 | 按 [音频能力检测与按需安装](references/audio-capability-setup.md) 独立选择 Qwen3-TTS、Whisper、ACE-Step 1.5 或 HTDemucs；本地参考音色配音读 [Qwen 配音接入](references/qwen3-tts-narration.md)，先复用环境，缺项由 Agent 按平台、资源与任务授权下载、安装和短样验证 |
| 定旁白的音色、语速、激情感、配乐与音效取向，或用户反馈配音单调、偏慢、没劲 | 先读 [讲解配音的声音方向](references/narration-voice-direction.md)：超级峰自己的作品默认用其授权的本人声音，语速偏快、有起伏，配乐托住人声，音效落在情绪点；先量旧版基线再定数字目标，分段多取样择优，画面按口播起止重定时；回听只证字准，激情、像不像本人和节奏卡点保持 `not_checked`；授权与状态读 [讲解导演](references/explainer-narration.md)，本机配音读 [Qwen 配音接入](references/qwen3-tts-narration.md) |
| 选择、变体、借用或新增风格 | 用 [风格画廊](assets/gallery/index.html) 看画面、来源样片与并排对比；按 [风格包合同](references/style-pack-contract.md) 精确查询 ID／中文名／英文名，只读选中包的 STYLE.md 与其引用 |
| 用三维世界呈现音乐 | 沿 music-event-performance 读取 [音乐驱动三维世界](references/music-driven-world.md)，复用分析工具与起步工程，内部检查后直接完成成片 |
| 诗词、乐器与景物形成三维意象 | 沿音乐分支补读 [诗词音乐世界](references/poetry-music-world.md)，组织意象接力、运动时钟及人物与乐器接触 |
| 内容中的物体或现象需要具体构建方法；水、咖啡、茶、雨水等液体的形态、光泽与变化 | 先读 [物体形象构建](references/object-construction.md)，按“元素＋表现重点＋镜头尺度”匹配配方；液体加载 [水与液体构建](objects/water-liquid/METHOD.md)，选型前必读方法与工程基线；液体为表现主体且无明确平面风格要求时默认三维构建，禁止先自选二维绕过工程要求；绑定实现能力；开放海面加载 [可执行配方](objects/water-liquid/OCEAN.md)，三维任务补读 [画质构建与排错](objects/water-liquid/QUALITY.md)，验证全程覆盖与目标原生质量，发现可见缺陷须返修 |
| 工具、引擎、素材、实际制作 | [TECHNIQUE.md](TECHNIQUE.md)，能力探测后沿已有工程制作 |
| 首次扩展、维护、导入与目录生成 | [MAINTAINING.md](MAINTAINING.md)，维护库与制作当前作品分别处理 |
| 让计划落实到代码、检查实际状态或局部重做 | 读 [执行绑定与观测](references/execution-contract.md)，复用主计划 ID 和时间，绑定实现与依赖；从引擎回传实际状态，检查关键片段并按影响范围返修 |
| 从计划走到成片 | [制作流程](references/production-workflow.md)、[计划合同](references/plan-contract.md)和[审片与修改](references/review-and-revision.md) |

三种编排方式继续可用：recipe 选择场景配方，compose 组合局部布局和动作，free 自由设计。场景、风格、动效、表达与配方通过 [目录工具](references/commands.md) 按需查询；数量以生成目录为准。表达是指导，源码是实现参考；各自不代表某个宿主已经安装或渲染通过。

```sh
python3 SKILL_ROOT/scripts/catalog.py --kind style list --scenario knowledge-explainer
python3 SKILL_ROOT/scripts/stylepacks.py resolve 中国水墨
python3 SKILL_ROOT/scripts/catalog.py --kind recipe get 极简左右讲解
python3 SKILL_ROOT/scripts/catalog.py --kind recipe get knowledge-rap-explainer
python3 SKILL_ROOT/scripts/catalog.py --kind recipe get 访谈解读
python3 SKILL_ROOT/scripts/catalog.py --kind recipe get 源码说明片
python3 SKILL_ROOT/scripts/product_ledger.py check /project/video/ledger.json --source /path/to/product-source
python3 SKILL_ROOT/scripts/validate_plan.py /project/video/plan.json
python3 SKILL_ROOT/scripts/check_delivery.py /project/video/plan.json /project/video/delivery.json --probe --require-video
```

## 制作中持续落实

- 先写观众变化、贯穿线、元素使命和声音职责，再选择特效。关键镜头明确新增信息、焦点、揭示顺序、稳定停留与下一镜接力。简单任务保持轻量。
- 事实镜头先找真实产品、原始照片、录像、档案与数据；先查项目缓存与授权资产，只补缺口。无法成立时换镜头或收缩主张。
- 信息流科普与宣传默认检查首帧和前三秒；概念讲解先核事实、标准与术语，再逐层揭示；Rap 先核知识与可唱歌词，再按真实音轨编排。
- 有旁白或歌词时取得真实音频，逐句关联画面与字幕；换音轨后重新测量、编排和核对。音乐选择遵循用户指定、项目已选、配方默认的顺序；候选池与默认分开维护，不将某首曲子升为全局默认。
- 音乐视频默认以代码构建可独立控制的动态主体与场景；图片可作为背景、纹理或局部素材，单张整图推拉不能作为默认成片。用户明确指定静态图片作品或其他表现方式时遵循其要求。先用可播放短段兑现前三秒及关键乐句的主体动作、运镜、转场和字幕动效，再完成全片；表达未兑现先返修，能力不足时交候选并说明缺口。
- 音乐视频以音乐驱动画面的节奏，歌曲营造氛围，场景编排、主体动作、运镜、转场与动效共同建立吸引力和沉浸感。慢歌同样需要设计声画落点，随唱句、旋律、呼吸、重音和停顿安排蓄势、推进、释放与余韵；快慢影响速度、幅度和密度，不能成为弱化编排的理由。有演唱却无现成稿时，先按字幕指南探测并尝试可用转写／对齐能力，不能直接省略歌词和默认字幕。
- 有旁白或歌词且字幕语言未指定时，默认中文为主、英文为辅，英文紧贴对应中文下方并保持成组；用户明确要求英文时纯英文。用户指定其他语言、无字幕，或项目已有明确字幕要求时优先遵循；纯器乐不凭空补歌词。字幕的翻译、节奏和配色按 [字幕导演与配色](references/subtitle-direction.md) 实际落实并审片。
- 时间使用整片绝对秒与稳定 ID；画面、声音和字幕从同一排程派生。音效较多时使用 [声音事件表](templates/audio-event-map.json)，必要时用 film_probe.py 与 audio_event_audit.py 实测。统一时钟、随机 seek 或声音同步只有实测后才能登记通过。
- 代码制作把必要镜头、相机、主体、字幕和声音绑定到实际实现；按 [执行合同](references/execution-contract.md) 派生时间、回传对象与字幕位置，并核前三秒及关键切口的连续片段。记录存在、数值变化和实际视觉效果分别验收；局部修改先算依赖影响，直接成片模式内部检查返修后继续。
- 上游风格的完整规则和可复用源已纳入包中。先确定本片意图，再读案例实现；本片品牌、事实、指定音乐、语言、画幅与交付要求优先。素材、模型或工具许可不从代码许可推断。
- 内部来源、重建与执行记录单独保存。正文、业务提示词、可见路径、字幕、口播及导出附件直接面向受众，不自动附加制作身份标签或创作自述；保留必要事实边界和授权检查。
- 必要要求未过先返修。结构、源码可用、实际导出、观看、听审与观众理解分别记录；候选版本不能继承旧版或上游案例的通过状态。

## 修改、交付与记忆

按镜头、对象或时间窗定位修改并复验依赖；改配音重新量时，改事实重核来源和图形语义，改色不无故重做声音。扩展读 [扩展合同](references/extension.md)，单片变体写项目，稳定个人风格用外置包与新 ID。

交付真实视频、必要编辑源、素材引用与验证摘要，说明实际工具、未完成项和保留资源。未经要求不上传或发布。清理本次归属明确且不再需要的资源。

运行记录留在项目内；仅将简短结果、明确偏好和可核验问题更新到 data/memory.md，最近 20 次，不存私密素材或长对话。修改 Skill、风格包规范和行为仍遵守宿主已授权的确认流程。来源及许可见 [sources.md](references/sources.md) 和 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
