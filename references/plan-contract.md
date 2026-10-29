# 可编辑计划与交付合同

代码路线可按 [执行合同](execution-contract.md) 用 execution.json 引用本计划原始字节哈希及既有 ID，派生引擎可消费的帧范围、通道与依赖快照；不改变 schema v1，不增加第二份独立时间线。全部计划 motions 必须绑定，额外必要源由 required_source_ids 指定。实际状态与文字框由工程回传，旧 bundle 的观测不能用于新版本；该层不自动渲染，也不把状态采样当作像素／听审证据。

schema_version 为 1。路径相对计划文件所在目录；允许显式绝对路径，不把本机个人目录写成模板默认值。所有时间均为从整片开始计算的秒数，数值必须有限。机器检查保证结构与一致性；语义、实际画面、声音与理解另验。

## 计划最小结构

```json
{
  "schema_version": 1,
  "project_id": "sample",
  "revision": 1,
  "goal": "观众看完能够说清的事情",
  "audience": "目标观众",
  "scenario_id": "knowledge-explainer",
  "mode": "recipe",
  "output": {"width": 1080, "height": 1920, "fps": 30, "duration_seconds": 8, "language": "zh-CN", "audio": "silent"},
  "design": {"style_id": "paper-editorial", "rationale": "为什么这种表达适合这段内容", "preserve": []},
  "runtime": {"adapter": "existing-project", "capabilities": []},
  "assets": [],
  "scenes": [{
    "id": "scene-01", "purpose": "理解一个变化", "start": 0, "end": 8,
    "layout": "relation-diagram",
    "elements": [{"id": "object-01", "role": "subject", "content": "内容主体"}],
    "beats": [{"id": "beat-01", "time": 1, "meaning": "主体出现"}],
    "motions": [{"id": "motion-01", "pattern_id": "reveal", "target_id": "object-01", "start": 1, "end": 2, "parameters": {}, "beat_id": "beat-01"}],
    "narration": [], "audio_cues": [], "hold_seconds": 2
  }]
}
```

必需 schema_version、project_id、revision、goal、audience、scenario_id、mode、output、design、runtime、scenes。assets 可省略为空；scene 中 elements 必需，beats/motions/narration/audio_cues 可省略为空。场景需要 id/purpose/start/end；elements 每项需要 id/role，content/asset_id/continuity_key 可选。简单单镜头直接使用同一合同，不强制额外写四五份文档。

mode 为 recipe、compose 或 free。内置 scenario_id 见场景目录；自定义场景用 custom 并提供 scenario_description。自定义视觉风格用 design.style_id=custom，附 design.tokens 与 rationale。runtime.adapter 是已选执行路线的名字，并非“已安装/已可渲染”证明。runtime.status 为 unresolved 或 ready，省略视为 unresolved；capabilities 只登记已经探测的特性，待实现能力写 required_capabilities。通用动效使用 time-control、opacity、position、stroke 等语义能力，DOM/SVG/Canvas或某个引擎只是实现选择，不是所有动效的硬前提。unresolved 产生可行动警告，不声称可以导出；ready 下必需能力缺失是错误。结构样例采用 unresolved，不能以示例字段冒充执行探测。

输出 width/height/fps/duration_seconds 为正数，宽高与fps为整数，audio 为 silent/optional/required。新视频未指定画幅默认 9:16（1080×1920），明确比例优先；局部修改沿用当前工程真实规格。分镜前确定宽高，重新安排主体、字幕与保护区域，不把改宽高视为完成重排。历史案例与标注轨道示例可保留其原始横版坐标，不将其当作新片默认值。scenes 按起点排序，从0覆盖至总时长，无空洞；跨镜重叠需要在后一个镜头写 overlap_reason。hold_seconds 为镜头内稳定阅读的预算，不自动等价于全部文字的有效阅读时间。

## 对象、动作与声音

- 各类别 ID 在整份计划内唯一，持久保存；不要因改颜色重排所有ID。跨镜同一主体使用不同 element.id 与相同 continuity_key。motion 只控制所在镜头的 element；容器/相机也作为显式 element。
- beats 包含 id/time/meaning，可加 narration_id。narration 包含 id/display/spoken/start/duration_seconds/timing；timing 为 measured 或 estimated，可加 asset_id。display 是字幕，spoken 是读法。没有实际音频时只能 estimated，最终有旁白的同步验收不能据估时通过。
- motion 需要 id/pattern_id/target_id/start/end。内置 pattern_id 见动效目录，可加 parameters/beat_id。自由实现用 pattern_id=custom、custom=true、channels 和 implementation，明确控制的属性及实现位置。channels 使用诸如 opacity、position、scale、color、stroke、camera、mask、value 的属性名；同一目标同一时段控制同一属性时，必须明确分层或合成理由 composition_reason，否则视为冲突。
- 所有镜头内元素时间须落在镜头范围内；beat 引用、素材引用、旁白引用必须能解析。beat_id 是关联，不声称词级自动对齐；实际峰值需要试听/波形或运行证据。
- audio_cues 包含 id/asset_id/time/role，可加 beat_id/gain_db/sync_offset_seconds；role 为 music、voice、sfx。素材 kind 为 image/video/audio/font/product/data；asset 需要 id/kind/path/source/rights/status，status 为 ready 或 missing，可加 sha256。ready 的本地文件应存在；引用远程URL也不等于已下载可用。纯代码生成的文件写 source="procedural"，path 指实际生成文件，可加 implementation 指生成代码、parameters 保存参数。直接绘制的DOM/Canvas对象不伪造图片素材行，在 element.implementation 或运行工程中保留实现。

音乐原曲的截取与落点按 [音乐导演](music-direction.md) 写独立music-cue-sheet.json；source_in/out属于原曲，timeline_start/end属于整片，不能混用。实际裁剪/混音文件仍走上述assets/audio_cues合同，不把候选cue ID当成已经存在的音频文件。

知识科普可用可选 [声画任务表](../templates/knowledge-music-score.json) 与 `explainer_timing_audit.py`：按当前计划哈希引用已有scene/element/beat/claim/layer和audio cue，不新增主计划必填字段；direct/staged只记录用户要求的交付节奏。音乐源锚点按cue sheet派生到整片，正向偏移表示声音较晚，阅读窗从文字完整可读的beat到退出beat。此检查只覆盖声明的排程，不能证明实测拍点、像素可读或听感；字段见 [科普编排](knowledge-music-direction.md)。

动态标注可直接使用原elements/motions；复杂的截图裁切、相机跟随或多段强调可另存annotation-track.json，详见 [视觉强调](visual-emphasis.md) 与 [轨道模板](../templates/annotation-track.json)。它记录源坐标、屏幕坐标、完整目标/排除区域、保护区和绝对时间，可用独立工具检查。`--plan`可另核scene/element引用；原计划不新增必填字段，轨道也不自动驱动执行器或升高视觉验收状态。

## 交付清单

```json
{
  "schema_version": 1,
  "project_id": "sample",
  "plan_sha256": "计划文件当前原始字节的SHA256",
  "producer": {"tool": "实际执行工具", "model": "实际模型或unknown", "run_id": "可核验的运行标识或unknown"},
  "outputs": [{"kind": "video", "path": "final.mp4", "sha256": "文件当前SHA256"}],
  "checks": {
    "structure": {"status": "not_run", "evidence": []},
    "semantic": {"status": "not_run", "evidence": []},
    "visual": {"status": "not_run", "evidence": []},
    "playback": {"status": "not_run", "evidence": []},
    "audio": {"status": "not_run", "evidence": []},
    "comprehension": {"status": "not_run", "evidence": []}
  }
}
```

输出 kind 为 video/source/preview/audio。outputs 的 path 相对交付清单，不是计划文件；plan中的素材路径相对计划文件。检查状态为 passed/partial/failed/not_run/not_applicable，passed 要写可核验证据路径或观察记录。silent 可将 audio 写 not_applicable，但用户要求声音时不能擅自改 silent。未做读者实验，comprehension 写 not_run。视频属性探测不等于连续播放；图片存在不等于已经观看。

修改计划或必需素材后旧检查不能继续代表新成片。保存 revision、变更范围与依赖关系，重建对应预览/音轨/视频，更新 plan_sha256 与产物sha256。哈希只证明字节对应，不证明好看、正确或听感。

## 目录合同

catalog/scenarios.json、styles.json、motions.json 均为 {"schema_version":1,"items":[...]}。每项 id/name/intent/constraints/fallback/verification 必需。verification 结构为 {"design":{"status":"authored","evidence":[]},"preview":{"status":"not_run","evidence":[]},"exported":{"status":"not_run","evidence":[]}}。design 状态可为 authored/reviewed；preview/exported 为 not_run/passed/partial/failed。发生过验证时补 environment、scope 和具体 artifact；仅某参数/某引擎通过，不能把整类或其他环境写为通过。不把来源演示记成当前环境验证。

场景项再含 required_inputs、narrative_options、layouts、style_ids、motion_ids；风格项再含 tokens、motion_character、avoid；动效项再含 channels、required_capabilities、parameters。查询工具输出稳定ID与用途，允许Agent自由实现未收录项，但仍遵守计划与验收合同。目录用于有边界的选择，不做所有风格与动效任意排列的承诺。

## 导演扩展（保持 schema_version=1）

旧计划继续适用。简单片在 design.rationale 写观众变化、贯穿线和声画职责即可；复杂片在同一计划使用可选 director，参考 [导演模板](../templates/director.json)。这些字段是意图记录与引用检查，不是审美、叙事或观众理解证明。

- director 如出现，包含非空 intent/viewer_end/throughline、structure:{kind,rationale}、entities 和 beats。viewer_start 可选。entities 每项 id/kind/role 为非空字符串，identity_constraints 为字符串数组；beats 每项 id/function/before/change/after 为非空字符串。两类ID分别唯一，按职责保留，不因调色重排。
- structure.kind 是内容适合的结构名，可自由命名；不强制三幕。人物目标等按需附加，产品／知识／音乐可以没有人物。未知事实不得编造来填表。
- sound_arc 可选，每项 id/beat_id/role/onset_anchor/energy/visual_relation 为非空字符串，beat_id 引用 director.beats。它记录声画关系，不是可播放音频。实际声音仍写 assets/audio_cues。
- iteration 可选，max_passes 是正整数，stop_rule 是非空字符串；它是本任务探索上限，不授权费用或无限资源。tech_language 可选，choices/avoid 为字符串数组，写为什么相关，不只贴“科技感”标签。
- scene.intent 可选，如出现，viewer_change 必需且非空。beat_ids 引 director.beats，focus_entity_ids 引 director.entities；reveal_order 引本镜 element.id，均为字符串数组。camera 如出现，framing/movement/purpose 为非空字符串。handoff/acceptance 如出现为非空字符串。
- design.expression_ids 可选，为目录中 expression ID 数组；design.recipe_id 可选，为一个 recipe ID。自由创作可省略。引用只说明选择，不能自动调用效果、排时钟、创建素材或提升验证状态。

catalog/expressions.json 和 recipes.json 使用同样 schema_version/items 与通用项字段。expression 另带 layer/tier/status、inputs、parameters、composition、required_capabilities、existing_motion_ids、verification_questions、source_relation；status=guidance，设计控制不冒充执行API。recipe 另带 scenario_ids/style_ids/motion_ids/expression_ids 与 story_steps。scenario_ids 是推荐场景，不是排他的引擎支持清单；跨场景借用时解释适配并重查事实与能力，脚本给提醒而不阻断。场景可附 expression_ids/recipe_ids；脚本验证这些引用。配方与表达是指导，不把来源视频登记为本机通过。

recipe可选`music_policy`：`candidate_track_ids`为非空无重复曲目ID数组，`default_track_id`须属于该池，`planning_mode`为music_first/content_first/adaptive，`default_requires_confirmation`为布尔值。目录检查其结构与音乐库引用，旧配方省略该字段仍适用。`music_library.py select --recipe ID`按用户指定、项目已选、配方默认解析；`--track`允许显式选择池外库内曲目，`--source-file`允许项目内新音源，两者均不修改默认与候选。所选源缺失或哈希／时长不符时阻断，不静默替换；时长与哈希检查不能证明听感或使用范围。

## 知识包扩展（保持 schema_version=1）

旧计划继续适用。讲解抽象知识或资讯时，可在计划顶层加可选 `knowledge`；字段、检查码与填写顺序见 [知识包合同](knowledge-pack.md)，模板见 [知识包模板](../templates/knowledge-pack.json)。

- `knowledge` 如出现，`validate_plan.py` 会校验它，核对 `layers[].scene_ids`、`focus_element_id`、`claim_ids` 与 `carrier.mappings[].element_id` 是否指向本计划里真实存在的镜头与元素，并对旁白与元素文字做受控表达检查。错误并入计划错误，警告并入计划警告；`--strict-knowledge` 把知识类警告升为错误。
- `design.expression_ids` 含任一 `knowledge.*` 却没有 `plan.knowledge`，给 `knowledge_pack_missing` 警告；有 `plan.knowledge` 却没有记录任何 `knowledge.*` 表达，给 `knowledge_expression_unrecorded` 警告。
- 层不要求与镜头一一对应，但每个镜头至少服务一个层，否则给 `scene_without_layer` 警告。
- 不新增必填字段，没有 `knowledge` 的计划行为不变。结果里的 `knowledge.scope` 为 `knowledge-pack-contract-only`，只表示合同检查，不代表画面、声音或理解已验证。

## 产品表达注记与媒体时钟（保持旧合同）

按需读 [产品表达](product-expression.md) 和 [单镜笔记](../templates/product-shot.md)。镜头主张、input/intermediate/result角色、状态依据、语义槽、接缝关系、声音职责及内嵌媒体映射属于设计注记，可写进现有purpose/intent或项目笔记；不新增计划必填字段。原脚本不校验这些语义、状态真实性、音色、剪辑源入出点或A/B控制，不把结构通过当上述验收通过。

现有scenes.start/end、beats.time、motions.start/end、audio_cues.time仍为整片秒；内嵌媒体源时间单独记录入出点、整片起止、速率和重放。音效的实际起音相对文件起点有偏移，按原audio_cues/beat与实际素材校准。参考混音不能自动登记成独立SFX；实际裁剪/混音文件仍需assets来源/使用范围/哈希。

两份新结构示例保留runtime=unresolved及missing音频，只有结构可查，不能直接导出或通过strict-assets。实际项目替换素材、实现、审看后再生成自己的delivery，不继承示例状态。

## 风格包扩展（旧计划继续适用）

内置风格和显式外置集合统一解析。可选 design.style_overrides 与 design.style_lock 的字段、继承、能力与哈希检查见 [风格包合同](style-pack-contract.md)。来源风格需要的 time-control、graphics-2d、graphics-3d 或 media-composite 是实际实现能力，不能仅凭包存在登记 ready。
