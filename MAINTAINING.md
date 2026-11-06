# 维护与扩展

普通制作在用户项目内完成。新增或修改库本身的规范、能力和默认行为，先遵守宿主授权；单片的临时选择不自动成为长期规则。

## 新增或派生一个风格

先查当前目录能否参数化。稳定变体使用新 ID 和外置集合：

```sh
python3 scripts/stylepacks.py init brand-ink --into /project/video/styles --extends opuscar-ink-wash
python3 scripts/stylepacks.py resolve brand-ink --style-root /project/video/styles
python3 scripts/stylepacks.py validate --style-root /project/video/styles
python3 scripts/catalog.py --kind style list --style-root /project/video/styles
python3 scripts/validate_plan.py /project/video/plan.json --style-root /project/video/styles
```

init 只建立起点，不覆盖现有包。写清本包的材质、色彩、字形、运动、相机、声音、原生动作、避用和回退，核实际品牌、中文、画幅与阅读窗。改版保持本包身份和调用方稳定；改变核心媒介时采用新 ID。

有可复用实现时，登记实际文件、参数、依赖与可运行命令，将小素材来源写清。关键帧、短片、完整导出、观看和听审按实际状态登记。没有可运行实现仍可作为 guidance 收录，不填占位视频或继承来源证据。

## 生成与检查

```sh
python3 scripts/stylepacks.py build
python3 scripts/stylepacks.py build --check
python3 scripts/stylepacks.py validate --sources
python3 scripts/build_gallery.py
python3 scripts/build_gallery.py --check
python3 -m unittest discover -s scripts -p 'test_*.py'
```

style.json 是风格元数据唯一来源；catalog/styles.json 与 styles/README.md 由 build 生成，图册再由 catalog 构建。不手改生成区。生成内置目录始终排除外置项目与个人集合，防止其内容混入分发包。

风格画廊为 assets/gallery/index.html，动效与配方目录保留在 expressions.html。前者从 styles-template.html 生成，后者从 template.html 生成。风格图像嵌入 HTML，单独复制 index.html 仍可浏览画面、筛选和比较；播放样片需保留完整目录。59 条内置视频位于对应风格包的 sample.mp4，画廊使用相对路径，明确点击后才加载；一个详情页只保留一个播放器，关闭详情时停止并释放。

风格包可选 gallery.poster（包内图片）、poster_sha256、video（包内视频或 HTTPS）和 video_sha256；可选 attribution.name／url 用于详情内的简短署名。旧 source_url 元数据仍可读取，画廊不生成外部播放入口。新增包及素材后重新生成即可进入画廊，无需手改页面列表；缺少图片时使用当前颜色和图形参数。gallery 不从基底继承，案例素材与新包的实际效果分别记账。Lemo-Opuscar 的 59 种风格仅在详情内显示一行简短署名，基础风格不加此标注。

59 张代表帧由 import_gallery.py 从固定提交的已核实本地 checkout 导入；只取 styleboard/img/<slug>_0.jpg，并保留已集成的视频绑定。样片由 import_samples.py 根据审查后的 web Release 资产清单串行导入：先核对 GitHub 发布的大小与 SHA-256，再探测视频轨、时长和尺寸。game-show、paper-lantern、news-package 的音轨不纳入分发，移除音轨时核对视频包内容哈希保持一致。断点与临时下载留在忽略目录 Output/gallery-downloads，已验证文件可复用。

代表帧清单为 assets/gallery/reference-frames.json；样片清单为 assets/gallery/samples.json，记录资产版本、原文件哈希、分发文件哈希、媒体信息和变更。导入后运行 stylepacks.py build 与 build_gallery.py；完整性检查使用 stylepacks.py validate --sources。更新来源包后重新导入素材，避免元数据刷新恢复外链或遗漏本地绑定。

```sh
python3 scripts/import_gallery.py --source /path/to/inspected-checkout
python3 scripts/import_samples.py --release-manifest /path/to/reviewed-release-assets.json
python3 -m unittest discover -s scripts -p test_gallery.py
```

交互逻辑检查是隔离测试，不替代实际浏览器布局、播放和移动端验收；网站操作继续使用宿主要求的 Chrome 路由，安全策略阻断时保留未验证范围，不改用其他浏览器绕过。

## 新增成片案例

成片案例写在 README 的“创作案例”里，按表达方式分类，现有音乐视觉作品、说唱知识解说、音乐产品解说、产品宣传片。现有分类说不清再加新类，README 与 examples/showcase/README.md 同步建同名标题。

根 README 里每个类目是一张 HTML 表格，每行最多 4 格。每格自上而下三段：单独成行的播放器链接、`**标题**`、一句话指令，段与段之间空一行，链接才会变成播放器。类目满 4 条时用 `<table width="100%">`，格子写 `<td width="25%" valign="top">`；不足 4 条时表格不设宽度，格子写 `<td width="209" valign="top">`（约为桌面端 README 宽度的四分之一），靠左排列、不补空格，避免单个格子被拉满整行；超过 4 条另起一行 `<tr>`。examples/showcase/README.md 保持“标题、播放器、说明”的纵向版式，在播放器下方加一行“一句话指令：…”。

一句话指令是写给读者的示例，不是当时的原始提问：以 `用 $chaojifeng-video-design` 开头，一个句号收尾，不超过 100 字；用【】标出读者要换成自己素材的位置，再写这条视频的主线动作。整段只放一个 `$`，出现两个时 GitHub 可能把中间的文字当作公式。

1. 压缩：竖屏 720 × 1280 或横屏 1280 × 720，H.264 High、AAC，加 faststart，保留原声。从 `-preset slow -crf 24`、音频 96 kbps 起步，每条不超过 8 MB；GitHub 原生播放器对免费账号的附件上限是 10 MB，超出无法上传。小字看不清时降 CRF，不放大尺寸。第一帧就是播放器里的封面，要选有内容的画面。
2. 入库：视频放进 examples/showcase/，在 manifest.json 登记来源文件名与哈希、输出文件、字节数、时长、尺寸、编码和检查状态；没有人完整看过或听过的，如实写 not_run。一句话指令写进 manifest 的 prompt_examples，键是作品 id；音乐视觉作品的指令也放在这里，不改动会被打进在线画廊的数据文件。
3. 上传：在议题或评论编辑框里上传同一个文件，取得 `https://github.com/user-attachments/assets/…` 链接，单独成行写进根 README 的格子和案例页，并记入 manifest 的 github_video_attachment；与句子混排时只显示为链接。下载附件，核对哈希与入库文件一致。
   - 浏览器没有登录 GitHub 时，用 gh：先看 `gh issue create --help` 里有没有 `--attach`（2.92.0 没有，2.103.3 实测可用），再建一个临时议题 `gh issue create --repo <owner/repo> --title upload --body-file body.md --attach film.mp4`，从议题正文取出链接。
   - 临时议题可以删除（`gh issue delete <编号> --yes`，需要仓库管理权限）；2026-11-06 实测，议题删除后附件仍可下载，删除前后各下载一次核对哈希即可。
4. 检查：`python3 -m unittest discover -s scripts -p test_showcase.py` 核对体积预算、清单哈希、链接、分类标题、每行不超过 4 格，以及两处 README 的指令与 manifest 一致；推送后打开 GitHub 页面，确认每格的播放器、标题和指令都出现。窄屏下 HTML 表格不会自动折行，只验证到桌面宽度，手机宽度如实标注未验证。

```sh
ffmpeg -i film.mp4 -vf "scale=720:1280:flags=lanczos,format=yuv420p" -c:v libx264 -preset slow -crf 24 -profile:v high -r 25 -c:a aac -b:a 96k -ar 48000 -movflags +faststart examples/showcase/new-case.mp4
```

## 导入或更新上游

当前锁定 lemomo-ai/lemo-opuscar 的 `413a6bd6d78ebd3bdd5abaec9538a26867f890df`。先研究版本增量、许可证、兼容性与工作流差异，再修改导入器的固定版本与适配规则；不在普通制作时自动拉取 latest。

import_opuscar.py 从已核实的本地 Git checkout 导入，检查 HEAD 与已跟踪文件是否被改动；使用 checkout 中的 styleboard/catalog.json。它不安装、不联网、不执行上游代码。稀疏 checkout 支持只取所需文本源码；传入的 checkout 必须包含要收录的文件。

```sh
python3 scripts/import_opuscar.py --source /path/to/inspected-checkout
```

已有来源包必须在审查变更后显式 `--replace`。导入器保留本库旧包；写入上游完整 STYLE、DEMO、源元数据、可用文本源码与 CREDITS，字体、音源、图片、视频、模型和数据集留在使用项目按授权准备。共享 core 也只是源码，不承诺直接运行上游 build.sh。manifest.json 记录逐文件哈希，validate --sources 核完整性。

上游 AGENTS 保存为 AGENTS.upstream.md，避免作为本工程代理规则加载。第三方源码保持原样，实际适配写在本包 STYLE.md 和项目中，许可证随包保留。新增上游代码后按它的依赖、资源和素材声明检查缺口。

## 其他能力

新增场景、动效、表达与配方沿用 [扩展合同](references/extension.md) 和 [计划合同](references/plan-contract.md) 的现有数据接口；复用稳定 ID、参数单位、能力、冲突、回退及证据字段。它们与风格按语义组合，不为一次参考效果新增近义目录或强制引擎。

修改接口后回归旧计划、外置风格加载、名称冲突、依赖循环、路径边界和证据隔离；实际引擎和导出测试按变更风险选择，资源密集任务串行。

## 物体形象构建配方

按 [构建方法合同](references/object-construction.md) 扩展，复用 recipes 目录与查询入口。每项说明元素、表现重点、尺度、形态边界、工程选择、参数联动、演化路径与验收；方法在对象目录，镜头构建卡在 templates。配方正文围绕构建动作、决策依据与验收展开。新方法不改变旧计划必填字段，概念推导与实际实现分别验证。
