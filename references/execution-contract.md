# 从导演计划到可检查的执行

用于代码主导的视频制作与局部返修。保留现有 `plan.json`、稳定 ID、风格包和引擎；本合同连接计划、对象实现、实际状态及受影响范围。简单任务可在已有工程记录等价信息，不要求新装引擎或另写第二套时间线。旧计划 schema v1 与原校验器继续有效。

## 1. 分阶段形成依据，直接出片连续推进

| 阶段 | 本片必须形成的依据 | 进入下一阶段前核对 |
| --- | --- | --- |
| 意图与事实 | 观众变化、真实依据、固定项与创作空间 | 必需素材和事实缺口是否真的阻断 |
| 参考与风格 | 本片配色、字体层级、构图、动作手感 | 参考观察、测量与推断分开 |
| 声画排程 | 分镜起止状态、歌词／旁白、多层声音锚点 | 音乐视频先处理指定音轨与歌词，再完成镜头编排 |
| 执行绑定 | 相机、主体、字幕、转场和声音对应的源 ID 与实现 | 每个必要动作有实际实现，不能只填写动作名称 |
| 难段验证 | 前三秒、关键乐句或最难关系、关键切口 | 连续片段兑现设计；未通过则内部返修 |
| 导出与复验 | 本次产物、版本、看听范围与余项 | 实际成片与当前计划、源、字体、素材一致 |

这些是内部工作依据，可放进已有项目文档。direct 模式由 Agent 连续完成；只有用户选择 staged 才在指定节点等待。延续项目时先对照当前输入与版本，旧项目只用于明确的技术参考，不继承题材、字幕省略或验收结果。

## 2. 执行绑定与唯一排程

先运行 `validate_plan.py`。使用 [执行绑定模板](../templates/execution.json) 时，文件放在项目根目录，`plan_sha256` 取本次计划原始字节 SHA256，`inputs`、`implementation` 都相对此目录。现有工程也可提供同等适配。

```sh
python3 SKILL_ROOT/scripts/execution_contract.py compile plan.json execution.json --out execution.bundle.json
```

| 字段 | 约定 |
| --- | --- |
| `deterministic` | 声明是否按绝对时间求状态；填写 true 不等于已通过 seek 检验 |
| 顶层 `inputs` | 全片共享执行依赖，包括实际加载的运行模块、公共样式、字体、锁文件；内容变化使全片重建 |
| `required_source_ids` | 额外必要源 ID；计划中的所有 motions 自动要求绑定 |
| `bindings[].id` | 执行绑定的稳定 ID；观测与返修使用同一个 ID |
| `source_id / target_id` | 引用现有 scene／motion／beat／narration／audio cue 与同镜元素；motion 的目标必须一致 |
| `kind` | camera、subject、caption、transition、audio；摄像机可登记为计划中的虚拟元素 |
| `implementation / inputs` | 实际实现文件与其局部依赖，必须存在；只记录、计算哈希，不执行这些文件 |
| `uses` | 依赖的其他 binding ID；转场需登记出镜、入镜及相关字幕／声音，不遗漏跨镜关系 |
| `peak_id` | 可选声音或视觉事件 ID，引用已有 time，不另手写峰值时间；必须落在本绑定内 |
| `channels` | 可选通道起止数值／等长向量及 linear、smooth、hold；复杂曲线、接触和材质由项目实现 |
| `must_change` | 必需可辨变化的对象设 true；采样状态不变会报错，变化存在仍需像素／连续片段确认 |
| `handles_frames` | 局部重做时向两侧扩展的帧数，默认 2；有运动模糊、长尾或跨镜作用时据实增加 |

编译器从主计划派生帧范围，使用半开区间 `[start_frame,end_frame)`；不接受手写独立的执行时间表。简单数值通道从首个有效帧到最后一个有效帧插值，峰值引用按最近帧映射并保留在区间内。人物动作、相机路径和动画曲线仍由 Agent 按题材设计，不能把基础插值当作导演完成。

现有音乐 score／cue sheet 已是实际时间来源时，由其生成主计划所需事件，再编译绑定；选定一个权威时间来源，禁止相互回写或维护两份独立秒数。改声音片段、速率或帧率后重新派生。声音起音、动作峰值、切口与落定分开核对，不把所有动作起始机械吸附到节拍。

## 3. 由时间驱动画面，由引擎回传实际状态

[runtime.mjs](../assets/execution/runtime.mjs) 是无依赖的时间采样与观测连接器，不是渲染引擎。项目适配器实现三个职责：

- `ready()`：等待本项目真实字体、纹理、素材与场景就绪。
- `render(sample)`：将采样通道应用到实际相机、对象和文字组，再等待当前帧渲染完成。复杂动作可使用 sample 的 frame、time、progress 和 peak_frame 求值；初态、终态都必须能独立恢复，不依赖上一次播放。
- `observe()`：从应用后的引擎对象、投影或 DOM 获取状态与文字框。禁止把传入的 sample 原封不动写回作为实际证据；时间计数器、随机噪声或无关粒子变化不能代替主体／相机变化。

```js
import {createRuntime, captureSamples} from './runtime.mjs';
const runtime = createRuntime(bundle);
// 宿主每帧用相同入口，预览和导出不维护两套动作逻辑。
await adapter.ready();
await adapter.render(runtime.at(frame));
// 内部采样可顺序、倒序、随机后再回到同帧；不要逐帧重复初始化引擎。
const frames = runtime.sampleFrames;
const trace = await captureSamples(bundle, adapter, [...frames, ...frames.slice().reverse()]);
```

Remotion／Three.js 可按宿主帧驱动并从应用后的对象与投影取状态；Blender 可从求值后的场景取得相机与物体状态、投影文字框；HTML／Canvas 使用同一绝对帧入口与实际布局。具体 API 先核本地版本和官方文档。该工具不声称这些引擎已经自动接入；只有项目适配并实测后才登记能力。

观测记录格式：`{schema_version:1,bundle_sha256,adapter,observation:"rendered-state",frames:[{frame,states:{bindingId:{...实际状态}},texts:{elementId:{text,visible,box:[x0,y0,x1,y1]}}}]}`。相机状态记录姿态、投影／焦距及主体屏幕位置，主体记录动作属性，转场记录参与对象和覆盖状态；像素证据及连续片段另附到 delivery 检查记录。仅相机数值变化不足以证明观众感到运镜。

## 4. 双语字幕、难段和实际检查

字幕 binding 可登记 `caption_pair:{zh_id,en_id,max_gap_px}`。这两个 ID 都引用同镜元素，英文紧贴对应中文下方；按本片字号和画幅确定最大间距，不套用统一像素值。拆词／词组仍以中英成组参与空间动线，进退场和移动期间都核对，英文不能落回独立的底部字幕条。

```sh
python3 SKILL_ROOT/scripts/execution_contract.py audit execution.bundle.json observed.json --out execution-audit.json
```

检查当前 bundle 身份、必要采样覆盖、状态变化、重复帧一致，以及所有提供的活动字幕样本是否成对、在画内、上下相邻且水平范围相交。默认关键帧样本不覆盖整个运动；字幕移动／切换、相机极值、切口、动作峰值前后应按风险加密采样，并连续观看。

`valid:true` 仅表示所给样本未发现这些机械问题，结果仍为 `partial`。遮挡、实际字形、阅读时间、对比度、文字意义、真正运镜、声音起音与情绪需要实际片段／听审；没有观测时不能制造记录。使用现有 film_probe、audio_event_audit 辅助，分别记录声明、状态、像素、连续播放与听审。观众留存与理解需要真实反馈。

前三秒要求由本片内容决定：相机揭示了什么、主体发生什么、首个声音落点对应哪次可见变化、字幕如何接住视线。失败时定位帧与对象，修正后复验；不靠新增随机粒子、过快切镜或放大单张整图冒充完成。

## 5. 局部重建与多画幅

修改前保留当前 bundle，修改后重新编译并计算影响：

```sh
python3 SKILL_ROOT/scripts/execution_contract.py impact previous.bundle.json execution.bundle.json --out rebuild.json
```

输出变化绑定、沿旧／新依赖图传播的受影响项、半开帧区间及可复用候选。删除绑定也纳入旧范围；镜头内容变化保守重做该镜；全片共享输入、音乐／素材身份、画幅或时间规格变化，以及非确定性实现，采用全片重建建议。工具只给建议，不运行渲染命令、删除缓存或自动把旧验收迁到新版本。

Agent 核依赖完整性后，用已有引擎的区间渲染能力执行。没有可靠区间导出时可以完整重导，仍保持局部源码修改。带跨帧模拟、累积特效或历史状态的画面需要烘焙／预热，未验证前不可声称局部复现。重做区间与整片同位置必须一致，合并时核视频规格、音频连续性和边界；不可直接假定编码文件能无损拼接。

画面层、字幕层、音频层按真实工程分开缓存；同一文件实现全部层时，文件变化会保守影响所有引用项。只改字幕颜色可以复用已核身份的画面帧，改音轨则重验歌词、动作、转场与同步。缓存可用不等于旧检查仍有效。

用户请求多个画幅时共享题材、素材与声音锚点，每个画幅独立派生布局计划、bundle 和文字框检查，按各自画幅渲染缩略图与关键片段。各规格分别留记录，不默认多生产未请求画幅。

方法启发来自 [Eian 的六步代码视频工作流](https://x.com/eianlu/status/2115761407774118044)；可观测接口参考已收录 Lemo 的 render／events／TEXTS 思路。本合同、编译／审计与依赖工具为本库独立适配，来源文章与样例不能证明本片效果。
