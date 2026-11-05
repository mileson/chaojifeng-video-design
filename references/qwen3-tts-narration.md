# Qwen3-TTS：按需下载与参考音色旁白

用于产品宣传、产品演示、知识讲解、资讯、图片叙事、故事和品牌片中需要新配音的部分。已有获准旁白先复用；无旁白、保留原声或只需背景音乐的任务不加载 TTS。用户指定的声音与引擎优先；需要本地参考音色配音时，优先检查本路线。声音安排见 [讲解导演](explainer-narration.md)，其他音频能力独立走 [按需安装](audio-capability-setup.md)。

## 1. 按机器选择模型

| 路线 | 模型与下载页 | 2026-10-29 核对的完整模型大小 | 选择依据 |
| --- | --- | --- | --- |
| Apple Silicon Mac，MLX Audio | [`mlx-community/Qwen3-TTS-12Hz-1.7B-Base-4bit`](https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-Base-4bit/tree/main) | 约 2.34 GB（2.18 GiB） | 本次实际生成旁白的路线；这是 MLX 社区转换版 |
| Qwen 官方实现 | [`Qwen/Qwen3-TTS-12Hz-1.7B-Base`](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base/tree/main) | 约 4.54 GB | 按 [官方 Quickstart](https://github.com/QwenLM/Qwen3-TTS#quickstart) 核 Python、PyTorch、设备与精度；官方示例使用 CUDA，不把 Mac 实测外推为其他平台已通过 |

容量包括主权重、配置、文本 tokenizer 和 `speech_tokenizer/`。MLX 版本的主权重约 1.65 GB，语音 tokenizer 权重约 0.682 GB，不能只下载主权重。模型容量不等于运行内存；Python、后端依赖、可选 ASR、下载缓存和音频产物另计，执行时按所选版本重新估算。

参考音色复刻选择 **Base**。CustomVoice 是预设声音路线，VoiceDesign 是描述生成声音路线，不因名字含 voice 就替换。Base 没有内置男声／女声名；不同声音共用同一 Base 模型，分别保存参考录音和对应逐字稿。新增一个声音无需再下载同一套权重。

## 2. 检测、下载与复用由 Agent 完成

1. 静态核对系统／架构、已配置 Python 的包版本、模型目录与文件完整性、FFmpeg、磁盘和可用内存，以及现有重任务。不要通过启动模型或服务来探测缺项。MLX 路线只在适配的 Apple Silicon 环境使用；其他机器先核官方后端，不能照抄 Mac 路径。
2. 把环境与模型位置登记在使用者本机或当前项目，复用已验证环境、缓存和已完成下载。文件存在仅是 `detected`；能加载、生成、听感合格分别记录。环境可用时不升级或重建，模型已齐全时不重复下载。
3. 确实缺失时，向用户简短说明所需能力、所选仓库／版本、预计下载量与磁盘／内存条件。在已授权制作／安装范围内，由 Agent 执行下载和补齐依赖，再继续制作；不要只给链接让用户手动配置，也不重复索要同范围授权。仅咨询或仅检测不自动安装；宿主权限、费用和外部上传边界继续适用。
4. 新环境使用独立虚拟环境。MLX 路线的包为 `mlx-audio`，模型卡给出安装入口；本次已运行组合为 `mlx-audio 0.6.0`、`mlx 0.32.4`、`huggingface-hub 2.2.0`。这是一组实测版本，不是所有机器的永久最低版本。按包元信息与平台选择兼容版本；官方路线沿 Quickstart 安装，不同时安装两套后端。
5. 只补本次需要的依赖。纯 TTS 不默认附带 Whisper、ACE-Step 或 Demucs；参考文本已准确提供时不强制安装 ASR。下载、TTS、ASR和视频编码串行，设置单任务资源上限。不要占满机器或结束用户原有进程。

### 下载例子

由 Agent 将下列变量设为实际选定的解释器、模型目录和仓库修订。路径属于使用者，不放在 Skill 目录内。已有配置直接复用；只有缺少下载包时才在该环境补齐 `huggingface-hub`。下面是**会联网下载**的执行步骤，不是检测命令。

```sh
TTS_PYTHON="/absolute/path/to/tts-environment/bin/python"
export TTS_MODEL_DIR="/absolute/path/to/models/Qwen3-TTS-12Hz-1.7B-Base-4bit"
export TTS_REPO_ID="mlx-community/Qwen3-TTS-12Hz-1.7B-Base-4bit"
export TTS_REVISION="37e955a1deb861c088ae5f3a67043185f3d1a60c"
"$TTS_PYTHON" - <<'PY'
import os
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id=os.environ["TTS_REPO_ID"],
    revision=os.environ["TTS_REVISION"],
    local_dir=os.environ["TTS_MODEL_DIR"],
    max_workers=1,
)
PY
```

上例修订来自核对当日 MLX 模型页。官方版选择对应仓库和独立目录；当日官方页修订为 `fd4b254389122332181a7c3db7f27e918eec64e3`。记录实际采用的修订，不把 `main` 的后续变化悄悄带入历史项目。执行前核当前下载库支持的参数；完整快照保留 `speech_tokenizer/`，不要只取顶层 `*.safetensors`。失败先读日志，继续原目录和缓存，不循环重装或复制整套模型。

下载后核模型索引引用的所有权重、配置和 tokenizer 文件齐全，并与来源的大小／摘要核对。检查后以本地路径、离线模式运行短样，避免漏文件时隐式再下载。离线加载失败时回到缺项处理，不换随机镜像、关闭校验或静默改用云端接口。

## 3. 音色配置与短样

每个声音单独记录稳定 ID、参考录音路径及 SHA256、原音／处理版关系、准确参考文本、来源及使用范围、试读结果、语速和所用模型版本。可以在项目现有声音清单中维护，无需新增固定 schema 或修改主计划合同。

- 使用清楚、完整、单一说话人的获准参考，先核实际格式和解码，再按所选实现准备输入。保留原件；降噪原则见 [讲解导演](explainer-narration.md)。
- `ref_text` 必须对应参考录音实际说的内容；它不是本次待配的新稿。ASR 可给候选，仍要核对，不把识别结果自动标成准确逐字稿。
- 男声、女声或本人声音各自试读，不能通过变调冒充另一身份，也不能把某一声音的语速设置复制给所有声音。没有参考且用户只需通用声音时，在现有可用路线中选择并说明；Base 本身没有可直接填写的预设 speaker。
- 原始参考、生成候选、最终旁白分别保存。公开 Skill 提供方法和模型入口；个人录音及音色包只在其明确获准的范围内使用和交付，不随通用安装自动传播。

MLX 路线复用已实测的调用方式：先在受控进程中设置 `HF_HUB_OFFLINE=1` 与 `TRANSFORMERS_OFFLINE=1`，加载完整的本地模型；模型、内存上限和输入路径由本机配置提供。核心调用如下，变量均由项目输入提供：

```python
from pathlib import Path
from mlx_audio.tts.utils import load_model

model = load_model(Path(model_dir))
results = model.generate(
    text=narration_text,
    ref_audio=str(reference_audio),
    ref_text=reference_text,
    lang_code="Chinese",
    temperature=0.45, top_p=0.9, top_k=50, repetition_penalty=1.5,
    max_tokens=1500, stream=False, verbose=False,
)
# 消费全部 results，按每项实际 sample_rate 收集 audio，保存原速 WAV。
```

这些采样参数是已使用的短样起点；长稿按完整意思分段，检查截断与重复，不把 `max_tokens=1500` 当任意长稿都能完成。官方实现使用 `Qwen3TTSModel.generate_voice_clone(text=..., language=..., ref_audio=..., ref_text=...)`，参数名称与 MLX 不同，按官方示例和实际版本调用，不混用两套接口。

短样优先包含本任务的专名、数字、标点停顿与完整句尾。分别核对：文件可解码且非静音、漏字加词与读音、身份相似度、自然度、速度、首尾和接缝。ASR只辅助校字，波形与生成成功不证明听感；未能听审就记录未检查。用户要求短样时交付试听；用户要求完整成片时内部验证后继续，沿用既有 direct／staged 边界，不额外增加统一试听确认门禁。

## 4. 语速校准与声画时间

先保留原速 `1.0`，把实际采用的倍率作为当前音色／项目配置。用户觉得慢时可先试 `1.2`；同一原音频变速便于单独比较速度，不同时更换参考、改稿和重合成。本机已核对的 MLX 实现虽然暴露 `speed` 参数，但注明尚不直接支持；不要只传 `speed=1.2` 就认定输出已经加速。

沿已验证的课件后处理方式，使用 FFmpeg `atempo` 保留音高调整速度，例如：

```sh
ffmpeg -n -v error -threads 1 -filter_threads 1 -i narration-original.wav \
  -af "atempo=1.2" -c:a pcm_s16le narration-1.2x.wav
```

输出独立文件，检查实际时长、解码、峰值、首尾与音质。理论时长是原时长除以倍率，滤镜边界可能有小偏差，以最终文件实测为准；需要严格时长时只处理已核实的静音余量，不为凑秒数裁掉词尾。生成语气不合适或停顿过长时，再按完整语义段调整输入和重生成，不能只靠不断加速修复全部问题。

稳定倍率只适用于本次校准的音色、参考与语气范围，后续仍按文本与用途调整；不要把 `1.2` 写成全局默认。均匀变速后，同一音轨时间标注可按倍率变换作为候选，必须再对照最终音频；字幕、镜头、音效、人物口型和尾幕停留随真实旁白重排，不能沿用旧版的已通过状态。

## 5. 交付与验证边界

项目保留环境版本、模型仓库／修订／本地位置、参考指纹与使用范围、输入稿、生成参数、原速与最终音轨、倍率和检查范围。能力状态沿用 `missing / detected / test_failed / ready_for_task`；音色、文本与最终旁白验收沿用 [讲解导演](explainer-narration.md) 的分项状态。运行完成释放任务所属进程，保留可复用模型和环境，不新建长期服务。

## 6. 没有参考音色的通用旁白与整稿电平

用户没有指定声音、又没有可用的授权声音时，用通用合成声，不借用任何真人的录音。超级峰自己的作品不走这条：同一条说明片先用通用声做出第一版，用户反馈“音色单调、语速慢”，第二版改用他的本人声音，见 [讲解配音的声音方向](narration-voice-direction.md)。2026-11-05 在一条约 96 秒的说明片旁白上跑通，做法：

1. **先试几个种子，选一个再固定。** 不传参考音频，用同一段含专名和数字的短稿试 3 个种子，各自 ASR 回读，挑读得准、音色稳的一个；把这条样本和它核对过的文字当作 `ref_audio` 与 `ref_text`，整稿都用它，长稿的音色才不会逐句漂移。样本来自模型自己的输出，没有真人声音参与；仍要在音色记录里写明来源。
2. **整稿一次合成，句尾留牺牲尾。** 模型常吃掉最后一个音节，稿子末尾多加一小句垫尾，对齐词级时间戳后裁掉。长稿需要把 `max_tokens` 提到约 2600，并检查有没有截断与重复。
3. **逐分句拉平电平。** 同一次合成里后半段会明显变响（实测约 +7 dB）。按分句测 RMS，向同一目标拉平，单句调整上限约 ±6 dB；之后再做 75 Hz 高通、压缩、限幅，最后才进混音。
4. **响度按声道数记账。** 单声道旁白复制成左右两声道后，立体声读数会比单声道文件高约 3 dB。想让立体声混音落在约 −14.5 LUFS，单声道旁白文件先按约 −17.5 LUFS 定。成片实测：整合响度 −14.5 LUFS，响度范围 1.2 LU，真峰值 −3.5 dBFS。
5. **ASR 回读只管字。** 同音字（如“再／在”“地／递”）造成的差异不算读错，字错率要把这类差异单独说明；自然度、停顿和音色仍须人耳听，没听过就写 `not_checked`。

来源与实测：2026-10-29核对以上两个模型文件页、[Qwen 官方说明](https://github.com/QwenLM/Qwen3-TTS)、MLX 模型卡和本机 MLX Audio／Hugging Face Hub 实现；本地 MLX Base 参考音色短样及 `atempo=1.2` 已运行。模型容量是该版本文件量，不含完整环境；其他操作系统、官方后端、新机器首次安装与每个使用者的声音仍需分别验证。方法吸收既有课件配音实践，但无需安装课件 Skill，也不依赖维护者的私人路径和录音。
