# 方法归因与使用边界

合同、目录、工具与示意为独立实现。此页仅保留方法归因与使用边界，不作为运行依赖或当前成片的验收记录。

| 原始来源与锁定版本 | 借鉴 | 边界 |
| --- | --- | --- |
| [huashu-design](https://github.com/alchaincyf/huashu-design/tree/798c4235ebff03d5c45e3c8affdf5e9d18f9dfa7) | 方向、分镜、关键帧与声音审查 | 方法不等于执行器已安装，依片型调整深度 |
| [guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill/tree/c91369c449d34755d320a8b81d0734000d99d1ab) | 内容槽位、风格/布局与合同 | 交互演示不自动是确定性视频 |
| [OpenDesign](https://github.com/nexu-io/open-design/tree/78d5637cb49da07e81314d1544b5fc6d37c95084) | viewer takeaway、焦点、变换/停留、寻址 | daemon/编辑器/权限/播放器是宿主能力 |
| [guizang-social-card-skill](https://github.com/op7418/guizang-social-card-skill/tree/cf4b810fac1c73fb65a2bb31d8c9278d82cbc4c5) | 内容/证据→空间、品牌例外、首帧与短动态 | 短Live Photo非长故事；密度不证可读/理解 |
| [guizang-product-video-skill](https://github.com/op7418/guizang-product-video-skill/tree/18842e0f49a9eb2b8c00cc065ec37b314e235aaa) | 产品推方向、真实组件、实测旁白、mark与一致性 | 具体引擎、分支、素材许可和方向数量不泛化 |

来源版本沿用已有记录，未在本次文字整理中重新核验。各根许可证与素材许可不同；复制实现/素材、分发工程与成片用途按具体内容核对，此处不做通用法律结论。表现力、修改效率与理解收益待真实任务验证，不排名模型。

## 代码制作与执行可观测性

方法启发来自 [Eian《6步构建视频工作流》](https://x.com/eianlu/status/2115761407774118044)（2026-10-29 阅读原文）：阶段产物、动作手感、统一声画时间、多画幅布局及局部返修。参考已收录 Lemo 固定版本的 render／events／TEXTS 接口；没有复制文章长提示词或示例媒体。执行绑定、状态采样检查及依赖影响计算由本库独立实现。保留 direct 连续完成，不继承逐阶段用户确认、固定阅读公式或作者对不同模型的优劣判断；未观看听审来源示例，不以传播数据证明工程质量。

## 导演方法与效果研究增量

- [awesome-opus5-5-videos，固定版本](https://github.com/yihui-dev/awesome-opus5-5-videos/tree/92aee2f586ac0715cb3cbcb6384834f98a33383d)：借鉴提示词与作品描述的表达关系，未逐条播放、试听或复现。37项表达和8类配方是原创归纳，source_relation逐项标明。来源不证明单轮生成、模型因果或当前执行器支持，不分发原长提示词、成片或素材库。
- [DiDi_OK 现场分享转录](https://www.ifanr.com/1660654)、[完整问答](https://www.nfpeople.com/index.php/article/14095)：借鉴表达、观众形式、可行性、景别与筛选判断。媒体编辑转录未逐字对音，费用与周期存在口径冲突；个人经历、低饱和度偏好、作息和模型观点不写成通用规则。
- [FoST《Candy》](https://www.xiaoyuzhoufm.com/episode/6abe4228e742e36efcbd7eaa)、[《牌子》](https://www.xiaoyuzhoufm.com/episode/69d75763b977fb2c477da25d)：发布方摘要提供探索、草图转场和声画并行线索，摘要不能当逐字原话。研究转录与回听范围单独留档，不借此宣称本Skill已验证相关效果。
- [Gabe Michael 第一人称制作复盘](https://runway.com/customers/48-hours-to-generate-a-film)：镜头表、粗剪、困难镜头拆步；限时个案不代表通用工时。
- [Philippe Rosco 幕后公开Transcript](https://www.linkedin.com/posts/runwayml_go-behind-the-scenes-to-learn-more-about-activity-7466127958697594880-KsHw)：相机揭示次序、镜头意图与表演选择。无时间码、疑似转录错字、未回听，不能作审定字幕。
- [Paul Trillo 客座制作说明](https://ars.electronica.art/aeblog/en/2024/06/17/a-fall-down-memory-lane/)：记忆主题与生成／剪辑往返；全文访问受限，只取得原文检索段落，证据为partial。
- [Sasha Kasiuha 原始访谈](https://runway.com/customers/inside-creative-campaigns-with-creative-director-sasha-kasiuha)：意图指导筛选、补叙事连接与停止。供应商访谈有宣传选择偏差，不是独立观众研究。

导演字段、场景边界与验收问题为本Skill的设计归纳，不冒称任何创作者原话。

## 本机截图方法的视觉强调适配

视觉强调借鉴本机 screenshot-annotator 的完整视觉单元、保护区域、动作/结果标签、语义编号与最小返修方法；不复制其批量流程、脱敏算法或素材，不要求安装源Skill。

visual.target-callout为新增指导，camera.focus-frame/text.semantic-emphasis/text.read-then-move沿用原ID并补约束。视频时间、源到屏幕映射、跟随与遮挡检查属于本Skill的适配；静态标注引擎不因此成为视频跟踪器。模板和采样检查不证明实际视觉效果，不要求使用者安装源Skill。方法合同见 [visual-emphasis.md](visual-emphasis.md)。

## 产品发布片与声音对照增量

产品表达借鉴 [HyperFrames launches固定源码](https://github.com/heygen-com/hyperframes-launches/tree/d7ac35069d74a3a437780579b3b7fe2f3eeace5f) 的任务证明与声画编排。大媒体、品牌、商业字体与第三方软件不随代码许可自动可用；本Skill不打包其资产或实现源码。

- [PR主入口](https://github.com/heygen-com/hyperframes-launches/blob/d7ac35069d74a3a437780579b3b7fe2f3eeace5f/pr-to-video-launch/index.html#L24-L41)：任务/章节的时序，不证明实际PR运行或生成耗时。
- [SFX主入口](https://github.com/heygen-com/hyperframes-launches/blob/d7ac35069d74a3a437780579b3b7fe2f3eeace5f/sfx-music-launch/index.html#L48-L112)：已有33.8秒整片混音，NO AUDIO旧注释失效；两次源入点1.3/1.1、时长3.0/2.1，仅支持同素材渐增叙事。严格对齐A/B是本Skill新增设计，不是来源已经完成的受控实验；分轨过程与听审未知。
- [01接缝台账](https://github.com/heygen-com/hyperframes-launches/blob/d7ac35069d74a3a437780579b3b7fe2f3eeace5f/heygen-apple-motion/01-ui-sting/ledger.json#L1-L98)、[04操控](https://github.com/heygen-com/hyperframes-launches/blob/d7ac35069d74a3a437780579b3b7fe2f3eeace5f/heygen-apple-motion/04-generate-reel/index.html#L250-L456)：语义槽、字宽、抓点、容器遮挡；台账的方向不证明速度连续。
- [文字到构图](https://github.com/heygen-com/hyperframes-launches/blob/d7ac35069d74a3a437780579b3b7fe2f3eeace5f/frame-md-launch-storyboard/compositions/scene-06-text-to-frame.html#L333-L417)：短语/元素的手工对应，不是任意文档编译器。Inspector拥塞属于阅读节奏/直接操作，不补证对象边界扫描；variables只是参数声明演示，不证明通用联动引擎。

配方、状态边界、失败回退和看听验收均为原创适配，保持guidance；设计审查、结构校验与来源观察不能证明实际渲染、听感或理解收益。

## 发布片整片研究增量（2026-10-19）

用户提供了一部本机成片 `full-film.mp4`，要求抽出编排与呈现方法。它是上一节「PR主入口」所指项目的成片：片内场景起点与固定提交源码的 `data-start`（0、5.2、8.4、9.3、12.3、16.1、18.5、21.0、23.0、25.6 秒）逐一吻合，因此是同一项目的同源材料，不是第二个独立样本。

- 取证分四级：源码是观察（E1），成片抽帧、切点与调色板是观察（E2），响度、能量谷与起音由仪器测量（E3，没有听过），其余归纳是推断（E4）。分级与方法见 [参考片研究](reference-film-study.md)，十四个元素的观察依据、迁移写法与失败信号见 [发布片语法](launch-film-grammar.md)。
- 固定源码入口：[主入口](https://github.com/heygen-com/hyperframes-launches/blob/d7ac35069d74a3a437780579b3b7fe2f3eeace5f/pr-to-video-launch/index.html)、[开场](https://github.com/heygen-com/hyperframes-launches/blob/d7ac35069d74a3a437780579b3b7fe2f3eeace5f/pr-to-video-launch/compositions/opener.html)、[PR滚动](https://github.com/heygen-com/hyperframes-launches/blob/d7ac35069d74a3a437780579b3b7fe2f3eeace5f/pr-to-video-launch/compositions/pr-scroll.html)、[判决牌](https://github.com/heygen-com/hyperframes-launches/blob/d7ac35069d74a3a437780579b3b7fe2f3eeace5f/pr-to-video-launch/compositions/hard-read.html)、[总结](https://github.com/heygen-com/hyperframes-launches/blob/d7ac35069d74a3a437780579b3b7fe2f3eeace5f/pr-to-video-launch/compositions/summarize.html)、[调用](https://github.com/heygen-com/hyperframes-launches/blob/d7ac35069d74a3a437780579b3b7fe2f3eeace5f/pr-to-video-launch/compositions/use-skill.html)、[行动](https://github.com/heygen-com/hyperframes-launches/blob/d7ac35069d74a3a437780579b3b7fe2f3eeace5f/pr-to-video-launch/compositions/cta.html)，章节见同目录 feature-*.html。
- 边界：没有听过成片，没有观众实验。转折区的能量曲线（9.8秒起抬升，约11.9秒落入谷底，约12.05秒回升，早于12.3秒的画面翻转）像音乐的铺垫、断拍与落拍；来源里转折区能查到的音效只有打字、点击与一声轻扫，所以“转折由音乐剪辑承担”是推断，不是听出来的。参考片的时长、比例、速度、层数与字号只是起点，不是默认值。本Skill不分发其视频、素材、品牌、字体或配乐，也不暗示与来源有任何合作。
- `film_probe.py` 与 `audio_event_audit.py` 是本Skill原创的纯标准库实现，只测镜头切点、响度、能量谷与起音时刻，不能判断好看、好听或有效；用到真实成片时仍要看帧、听声。

## 创意导演提示词适配

创意导演方法吸收用户提供的提示词中的参考对照、关键事件、主次运动与声画领拍思路，见 [创意导演](creative-direction.md)。作者与公开入口未知，不分发原文，不沿用固定数值或效果保证。

## 从MV提示词提炼通用创作方法

镜头统筹吸收用户提供MV提示词中的能力试验、参考职责、生成前统筹与表达兑现思路，见 [镜头生产统筹](shot-production.md)。作者与公开入口未知，不复制原文；原声、歌词与口型按任务启用，固定工具、多模型与无限预算不作为默认要求。

## 素材表演与调度的独立实现

素材表演方法借鉴 [lemo-wake固定版本](https://github.com/lemomo-ai/lemo-wake/tree/f070df8bdf891d792012aabc054582b16e04f759) 的素材准备与动作编排思路，独立适配为坐标、遮挡、动作范围与复验指导。未本机复现、连续播放或试听，不继承对方运行结果与能力声明。

方法见 [素材表演与调度](asset-motion-direction.md)。不纳入对方代码、原文、模板、成片、字体或模型；引入具体实现或资产时另核使用条件。

## 讲解导演、本人声音与降噪

讲解导演借鉴本机 ai-avatar-narration 的真实旁白先行、资料/人物/嘴眼/字幕分层与音频绑定方法，见 [讲解导演与声音参考](explainer-narration.md)。不继承固定形象、课堂或WAN流程，不要求安装该Skill。本人声音的授权、哈希和听审状态见 使用者本机的 `assets/voice/manifest.json` 声音清单；授权不扩展为公开分发。

[ACE-Step官方教程](https://github.com/ace-step/ACE-Step-1.5/blob/main/.claude/skills/acestep-docs/getting-started/Tutorial.md) 提供参考音色条件及spoken word标签；[社区TTS-like路线](https://github.com/starsFriday/ComfyUI-ACEStep#tts-like-reference-voice) 与 [节点源码](https://github.com/starsFriday/ComfyUI-ACEStep/blob/main/nodes.py) 提供稿件转歌词、参考音色潜变量条件的研究线索，作者说明措辞、读音和旋律可偏移。社区仓库DeepWiki未索引后回退源码，不复制其节点或XL模型。普通Turbo本机试验与社区XL分开记录，机制不等于讲解质量。

轻降噪依据 [FFmpeg afftdn说明](https://ffmpeg.org/ffmpeg-all.html#afftdn)。处理参数不代表实测改善量，转写通过不证明音色未损伤。

人声增强使用已有 [DeepFilterNet v0.5.6](https://github.com/Rikorose/DeepFilterNet/tree/978576aa8400552a4ce9730838c635aa30db5e61) 与内嵌DeepFilterNet3；模型和二进制不纳入Skill。环境噪声抑制不等于通用多源分离或风声全部移除，具体听感以声音清单与实际听审为准。

## 知识形象化、逐层递进与行业规范先行

知识讲解方法的归因如下。用户提供的公众号文章与评论只作需求线索，不当作实验证据。

| 来源与版本 | 借鉴 | 边界 |
| --- | --- | --- |
| [Anatomy，固定版本](https://github.com/wheresryan22/anatomy/tree/1482e8469b0a9e0d8cc18ea2740a01423d29ae80)（MIT，提交于2026-10-18） | 物即解释、两种失败（太抽象、太平）、先立真值再造物、色调层级与一个亮点、落地标签、分解与装回规则、运动落定、读数同源、像评论家一样核查 | 原作是交互式等距图，不是视频；毫秒、零件数、档位只作起点，需按本片重测。只借鉴方法，不引入其交互、发布或三维实现。不复制其代码、示例和图，不继承其验证状态；作者案例不是观众实验 |
| [ASD-STE100 Issue 9](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf)（2025-01-15） | 受控语言的规则编号与思路：一句一事、主动语态、一词一义、先查词表 | 已读官方 PDF 文本核对规则号与适用边界。官方说明它只为技术文档开发、不能单独使用、不规定缩写与单位。本 Skill 的 STE-zh 是自定中文改编，数字阈值不是 ASD 数字，不得声称“符合 ASD-STE100” |
| [RFC 9293](https://www.rfc-editor.org/rfc/rfc9293.html)（STD 7，2022年8月） | TCP 三次握手示例的事实：§3.5、图 6、图 8 | 2026-10-19 核对；只用于结构示例。示例中的“对账台”是本 Skill 设计的示意载体，不是 RFC 内容 |
| ISO 24495-1:2023 简明语言 | 清晰表达原则的旁证 | 只核对了编号与主题，未读全文，不引用条款 |
| Karpathy 的“文本→图→网页→视频”阶梯 | 受控语言之后逐级升级媒介的线索 | 只见二手转述，没有取得原始出处，不当原话引用 |
| 公众号文章与评论区（用户提供） | 新手四问、桥接、读音词典、长片分块、模型边界与延伸阅读、事实核查需求 | 无公开链接；评论是个人经验，不作统计结论 |

领域起点表中标“种子”的来源没有读过原文；用到时先核版本、条款与现行状态，再把 `status` 改为 `verified`。七层结构、分档时长、关系类型与载体原型表、证据板、真值账本分类与检查码都是本 Skill 的归纳或设计，没有经过观众实验。目录里 `knowledge.*` 的验证状态保持 guidance/authored，不能因为示例通过结构检查而升级。

## 音乐推进知识科普

后续用户确认配方显示名为“概念知识科普”，沿用`knowledge-music-explainer`稳定ID。当前神曲作为配方内初始默认，候选与默认可扩展、更换；用户指定优先，按所选新曲反推编排，不把初始默认曲硬绑为全局默认。默认选曲不重复询问，单次选择、加入候选、更换默认分别处理；原音源与未验证状态保持，选择工具不冒充测拍或听审。

2026-10-21，用户提供本机《Vibe知识大赏保姆级教程》并确认扩展，随后明确要求支持“一次性完成，不需要先试片”。[科普编排](knowledge-music-direction.md)和`knowledge-music-explainer`将片内“定规格、音乐卡点、关键词乐器音效、先试片再分段修改”适配为字幕／旁白双分支、分层同步和可选交付节奏。一次性交付不设置试片确认门禁，最终检查与必要返修仍完成。

观察来自205.056秒文件的联系表、关键帧与片内字幕，未完成整片连续视听；作者模型、成本、流量自述未独立核验。音乐地图、可选任务表、时序校验与效果闭环为原创设计，不把113 BPM、固定10秒或某模型升为默认。参考[AudioLabs速度与拍点](https://www.audiolabs-erlangen.de/resources/MIR/FMP/C6/C6S2_TempoBeat.html)和[Cambridge多媒体学习原则](https://www.cambridge.org/core/books/abs/cambridge-handbook-of-multimedia-learning/principles-for-reducing-extraneous-processing-in-multimedia-learning/F29A19FCD34C542806F736E0661C05F5)补充边界；页面摘要与检索内容支持原则，不宣称已复现实验或证明平台留存提升。原片、私有对话和音乐文件不分发；配方预览、导出、听审与观众效果仍分别记实际状态。

## 产品音乐叙事与创作过程研究

用户于2026-10-20确认，将一部产品音乐短片的过程研究提炼为 [产品音乐叙事](product-music-story.md)、[素材选择](asset-routing.md)、[开场设计](opening-design.md) 和可选声画镜头笔记。研究对照了三次实质创作指令、早晚版本、分镜、真实素材清单、歌曲与事件表、关键场景代码及交付更正；抽看最终关键帧与全片采样，最终文件哈希与交付记录一致。完整私有研究留在用户项目，本Skill不分发聊天、个人路径、人物图像、歌词、声音或项目工程。

一部作品提供了做法与失败条件，未证明跨产品适用或传播提升。案例存在平台笔记读取失败、部分逐字时间由句级识别插值、歌曲局部重绘未听审、抽样口径改变导致运动量数字不同等限制；不把声音事件表、ASR无词、图册预览或结构校验当作听感/审美通过。目录配方保持guidance，新预览与导出状态为not_run，不继承原工程测量或旧版截图的验收。

素材与执行接口参考了本机Eagle、平台图片采集、media-use、imagegen、HyperFrames、ai-avatar-narration、motion-effect-distiller和媒体处理Skill的相关说明，只抽取职责与通用工件，不复制其实现、资产、固定默认值、安装或供应商依赖。未在本轮逐项运行这些能力；宿主用到时按当前说明与授权确认实际可用性。内置生图与CLI选择服从宿主规则，不把一个工具写成通用前提。

外部旁证：

- [TikTok Creative Codes](https://ads.tiktok.com/business/en/blog/creative-best-practices-top-performing-ads)：结构、声音、早期价值表达与编辑刺激的官方广告建议；2026-10-20读到页面，底层研究主要来自2020～2022年。
- [TikTok 2025小企业创意手册](https://ads.tiktok.com/business/library/TikTok_SMB_Creative_Playbook_2025.pdf)：前3～6秒与创意组织的背景材料；2026-10-20读取。只作为该平台广告语境的参考，不证明其他渠道、片长、色彩或开场问句有效。

相关性来自产品宣传与开场任务，时效性按上述版本和底层研究时间判断，权威性来自原始创作材料与官方指南的职责范围。访问人数、访问次数、点赞与评论数未知，不填0；未取得正文的其他检索结果不用于支撑方法。适配判断、声画分工和失败回退为本Skill原创归纳，仍需本次项目实际验证。

## 说唱科普与成品反馈

用户于2026-10-25确认，将指定Cursor制作与Codex返修过程归纳为 [嘻哈知识科普](knowledge-rap-direction.md)，并强化通用素材检索、首帧／前三秒、逐句声画编排、音轨变更后的重验与候选交付判断。研究读取用户原始任务、实质纠正、原工程自查与当前状态；模型思考和结果自述不作为用户确认。两段会话属于同一作品链，不能当作两个独立成功案例。

原任务要求全面采集事实素材、准确而有力度的歌词、沉浸声画和强开场；返修反馈包括前奏过长、词与字幕不符、旋律平、局部修字声线和接缝突兀。上述反馈支持建立失败检查，不证明某种引擎、整首生成或某参数必然改善效果。短试听认可不覆盖全片，自动测量不覆盖听感，新候选导出不等于被接受。

方法为本Skill原创适配，经确认实施；新配方保持guidance，预览／导出与观众效果分别登记，不继承旧工程的测量或接受状态。本Skill不分发原始私有对话、完整歌词、人物声音、曲目与项目素材；详细证据与执行记录只保存在用户项目。访问与互动指标未知，不填0。

初轮提案未取得三维与合成工具文档；用户随后补充指定仓库，已完成结构与针对性问答，并回读相关一手源码，详见 [场景与工具组合及来源](scene-tool-composition.md#一手来源与范围)。场景分工、镜头先行、Poly Haven资产许可、MCP边界、官方Remotion指导和真实MP4验收据此补充；未安装、运行或验证具体三维成片，不能把引擎名称和文档研究当作已验证实现。


## 资产优先与制作工具工件

2026-10-25，用户确认将资产优先、Poly Haven视觉提升、日语旁白与场景组合工程化。新增 [制作工具合同](production-tool-contract.md)、职责清单、只读探测／元信息检索与项目声明校验器。流程与缓存时长是本Skill设计，不是服务端配额、行业标准或画质承诺；代码测试只支持其对应的结构与失败边界。

Blender MCP的Poly Haven接入通过指定仓库结构、问答及`addon.py`交叉核对，资产检索与HDRI／纹理／模型导入属于文档支持的能力；本机默认端口未接通，没有完成MCP导入或渲染。AivisSpeech及Engine的官方README、角色路由和WAV连接源码支持日语TTS与音频拼接，未支持本轮所需的歌唱承诺；程序与声音模型条件分开核。Mixamo／Unreal暂为候选，不宣称完成其架构、现行许可或本机接入核验。具体一手入口与范围见 [场景与工具组合](scene-tool-composition.md#一手来源与范围)。

用户截图中Poly Haven HDRI改善水面和环境的主张用于提出同镜头比较，未取得原始工程，不能独立核实效果或约500KB的压缩结论。质量检查同时覆盖照明、反射、阴影、连续运动与成本；不能以资产已找到替代合理使用。研究记录和直接API元信息检索留在用户输出目录，不分发私有会话与截图；访问及互动指标未知。

## Lemo-Opuscar 工程规范与风格包

2026-10-26，经用户确认，纳入 [lemomo-ai/lemo-opuscar 固定版本](https://github.com/lemomo-ai/lemo-opuscar/tree/413a6bd6d78ebd3bdd5abaec9538a26867f890df) 的全部 59 个风格说明、案例说明与可用文本源码，并保留 MIT 许可证与素材来源清单。借鉴 STYLE／DEMO 分离、导演／技术分层、单一元数据生成索引、统一时间与可复现检查。

DeepWiki 用于架构起点，Context7 未收录该库，工程结论由固定提交源码核对。完整导入记录和哈希见 [第三方声明](../THIRD_PARTY_NOTICES.md)。保留本库真实素材、中文、指定曲目、direct 交付、模型与引擎中立等已确认规则；上游固定次数、模型、BPM 与案例故事不成为本库全局默认。源码收录、包结构校验、最小制作验证、整片观看与听审分别记账。

## 歌曲视觉导演

2026-10-28，用户确认将 [耶鲁音乐视频教学资料](https://teachers.yale.edu/download/units/12_01_05.pdf) 作为灵感来源，适配到 [歌曲视觉导演](song-visual-direction.md)。资料为 Andrea F. Kulas 于 2012 年发布的教学单元；第 8 页提出概念、表演、叙事三类，第 8–10 页讨论场面分析，第 10–12 页讨论观众推断与关键片段。它不是行业强制标准，也不提供本 Skill 的完整声画制作流程。歌曲意象判断、风格检索、音乐卡点和审片是本 Skill 的扩展，实际效果须逐片观看与听审验证。文档访问、点赞与评论指标未知。

## 音乐镜头与运动编排

2026-10-29，用户确认补入 [声画事件六层模型](music-event-model.md) 和 [事件卡](../templates/music-direction.md)：将多层音乐锚点、关系变化、注意力与运镜、峰值、空间材质、正常播放验收接入已有制作流程。研究出处、实际阅读范围和证据限制集中见 [模型来源](music-event-model.md#来源与证据边界)，包括 TikTok 官方广告指导、电影事件分段实验、声画切点同步实验、艺术声画审美实验及专业剪辑资料。六层模型为本库设计推导，尚无新成片或观众实验验证，不继承参考来源的效果结论；原有耶鲁灵感署名保留。

2026-10-28 用户反馈《阴天》候选片缺少随音乐可辨的镜头、运镜和动效；已确认 [音乐镜头与运动编排](music-shot-choreography.md) 的音乐事件、镜头事件、运动设计与声画审片。参考 [Motion Engineering](https://x.com/beamnxw/status/2108616740846420354) 的事件分解与局部修正、[工具清单](https://x.com/e1genqq/status/2114445900131013003) 的职责分类、[Motion Lab](https://x.com/flxrnc/status/2105311836190978392) 的动作阶段和逐帧返修；来源为文章和推荐清单，不是音乐卡点行业标准。参考视频只查看了部分画面状态，未独立完成音轨听审；文章案例参数、效果与作者反馈不继承为本 Skill 的验证。工具清单未全量研究；Remotion、HyperFrames、Anime.js 经项目结构问答及文档核对，其他为候选，具体工程仍需验证。用户案例支持定位缺口，不单独证明修改后能改善实际作品。访问与互动数据随平台变化，采集时未统一统计口径。


## 匹配剪辑与音乐转场（2026-10-29）

灵感来源于 [Sac-Y/match-cut](https://github.com/Sac-Y/match-cut/tree/b51c98f5c795b046ceb1c69396368dbabd88d5d9)，研究固定提交 `b51c98f5c795b046ceb1c69396368dbabd88d5d9`。读取规划、后期与检查文档，核对音乐分析、帧选择、几何／旋转／甩镜、声音放置与检查源码，并解析 iPhone Duo、Big Mac 两份实际配置及作者返修记录。DeepWiki 未收录，问答接口返回限流，结论由仓库原始文件支撑；Chrome 样片页超时，本轮未连续观看、真实听审或运行上游管线。

切口前后状态、动作接力、跨镜共享运动、有效选段及切口对照用于指导 [匹配剪辑与音乐转场](match-cut-relay.md)。[iPhone 案例](https://github.com/Sac-Y/match-cut/blob/b51c98f5c795b046ceb1c69396368dbabd88d5d9/examples/iphone-duo/README.md) 记录了动作碎片化、镜头过密、方向反转和停帧的返修；[Big Mac 案例](https://github.com/Sac-Y/match-cut/blob/b51c98f5c795b046ceb1c69396368dbabd88d5d9/examples/big-mac/README.md) 明确指出部分物件仅形状相似、人物关系未兑现。上述是作者复盘，未独立复验其实际效果。

上游 music.py 采用单一 BPM 与四拍小节假设，render.py 主要处理已有视频／图片的选帧和后期，qc.py 的对齐与亮度测量不能证明语义、动作连续性或听感。本库保留真实歌曲的多层锚点、代码构建动态主体、空间双语字幕及实际看听边界；不继承固定参数、模型服务、广告结构或案例通过状态。方法适配尚待具体新作品验证，仓库互动量不作为传播或留存证据。

上游采用 MIT，Copyright (c) 2026 Sac-Y。本次只沉淀方法及公开来源链接，未导入上游脚本、样片、音乐或品牌素材；若后续复用实质源码，保留版权和许可证，并分别核素材条件。

## 空间字幕与视线编排

2026-10-29，经用户确认，将字幕从固定阅读层扩展为可参与场景、运镜和注意力交接的表达，落实到 [字幕导演](subtitle-direction.md)、[声画事件模型](music-event-model.md) 与现有 [编排笔记](../templates/music-direction.md)。意象关联需通过画面建立，词组拆分需保留完整语义；七类编排方向为本库归纳，可自由扩展，不是来源方的官方分类。

| 来源 | 实际观察与可借鉴内容 | 证据边界 |
| --- | --- | --- |
| [开拍网感模板](https://www.kaipai.com/one-packaging) | 官方说明、正在播放的原片与包装对照及行业模板画面；标题／短语／强调词层级、句内分块、多位置布局与图形配合 | 主要为口播宣传示例，未安装 App 或测试自动剪辑，未完整听审；厂商效率及模板数量宣传不作效果证明 |
| [李华Liha 的歌词运镜动画教学](https://www.douyin.com/video/7672956366545292550) | 核对作者、页面章节、开头示范与结尾展示片段；文字空间层次、相机运动与入场动画协同 | 页面标注参考 @Shake9.，不将示范视觉归为教程作者原创；未完整观看约八分钟教程或听审，不能据此宣称完整复现 |
| [TikTok Creative Codes](https://ads.tiktok.com/business/en/creative-codes) | 官方正文的开场／主体／收束、运动、转场、文字与声音组织 | 广告指导，嵌入视频未播放成功；不证明自然流量、抖音效果或通用前三秒阈值 |

相关性按文字编排、音乐镜头与视线组织判断。抖音教学于 2026-08-12 发布，2026-10-29 页面显示 2761 赞、89 评论、1874 收藏、303 分享；这些是该时点互动数，不是播放、留存或方法因果证据。其他来源的访问与互动指标未知，不跨平台比较。未读取正文的课程目录不作为结论来源。方法尚待新作品实际观看、听审和观众反馈检验，不称“爆款公式”；私有候选工程、对话与原歌词不纳入分发。

## 产品宣传：两种入口与极简左右讲解（2026-10-29）

来源为用户提供的 Kimi Code 产品宣传创作对话及其对应参考片、迭代工程和结果抽帧。研究区分了初版参考中的品牌承诺首尾、后续用户明确要求的成果开场与品牌收束，以及左右主结构中的全屏、近景、对比和多图变奏。用户于 2026-10-29 确认将方法加入本库，并要求以一句话提示词开展独立 Agent 实作。

本库只收录通用编排、命名入口、声画规则和验收问题；不分发私有会话、原始素材、个人声音、项目绝对路径或参考片音乐。参考片与抽帧研究不等于完整播放或听审。新场景和配方初始为 authored／guidance，preview、exported 为 not_run；后续具体项目的实作与检查记录留在项目内，不自动继承为跨产品验证。来源素材与工具的使用许可需在具体制作中分别核实。

## 产品宣传：源码入口与选题侧重点（2026-11-05）

来源为用户于 2026-11-05 指向的 Kimi Code 产品说明片创作会话（一支图片类 App 的介绍视频）及其迭代产物：调研记录、故事线候选、规格单和验收记录。用户要求检查这套规范是否已沉淀，并把“传入任意产品源码、由用户给出选题侧重点、复刻这类说明类产品宣传片”作为产品宣传的一种模板规范；已有方法不覆盖的部分，由 Agent 全权归纳沉淀，不再逐项确认。检查结论：视觉语法与前两种入口已在 2026-10-29 收录，源码入口与相应的调研、取证和检查方法此前没有。

从该会话归纳进本库的是做法，不是素材：先读源码并给每条事实记出处；把限制与权益单列为不对外说的边界；真实界面取自当前版本的实际运行，只有标签的静态截图被判为不足，需要连续状态与局部放大；旁白整稿一次合成，字幕与镜头由同一份词级时间排程派生；字幕展示层去掉独立短句的末尾标点，同时保留原文做覆盖校验；不把分句音频按字节拼接；转写回听只作辅助，听审单独登记。账本字段、证据阶梯、取证路线与检查脚本是本库在此基础上的原创整理，浏览器扩展取证中的持久上下文与扩展参数写法以 Playwright 官方仓库的扩展测试为依据。

本库不分发该会话、参考片、产品素材、个人声音或项目路径，会话成片的检查状态也不继承到新配方。新配方初始为 authored／guidance，preview、exported 为 not_run；具体产品的实作与检查记录留在项目内。

## 场景、视觉角度、代码构建与动效表达（2026-10-29）

研究入口为 [Zara Zhang 分享的动画](https://x.com/zarazhangrui/status/2115336629770707254)。页面显示发布于 2026-10-28；研究文件为约 5.588 秒、2480×1514、313 帧的视频，未含音轨。实际查看了按每秒两帧采样得到的 11 张画面：菜单当前项、局部强调与光照方向存在对应变化，线描与纹理参与视觉风格。未完成连续播放核验，不能据抽帧认定精确缓动、响应延迟或完整节奏；原作者身份、原始源码、实际渲染技术与素材许可未核实，评论中的实现猜测不作为技术事实。访问与互动指标未作统一记录。

用户要求提炼场景、视觉角度、代码方式与动效表达之间的推导关系，并于 2026-10-29 确认归入现有框架。方法写入 [从内容到画面](design-method.md)，实现映射写入 [表达实现](expression-method.md)，后续取样规则写入 [参考片研究](reference-film-study.md)。这些是基于案例观察与用户要求形成的通用设计指导；示例中的代码机制为本库提出的构建方案，不归为原作实现，不固化案例形象、配色或引擎，也不新增风格包和目录 ID。尚无本轮新成片或观众效果验证，不分发原视频、原画或私有研究材料。
