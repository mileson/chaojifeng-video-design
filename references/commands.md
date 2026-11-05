# 常用查询与检查

将 SKILL_ROOT 替换为本 Skill 根目录。选项以脚本 --help 为准；检查不代替实际制作、观看和试听。

执行绑定、观测与返修范围按 [执行合同](execution-contract.md) 补齐本项目实现与依赖。这些命令不安装软件、不执行项目代码、不渲染视频：

```sh
python3 SKILL_ROOT/scripts/execution_contract.py compile /project/video/plan.json /project/video/execution.json --out /project/video/execution.bundle.json
python3 SKILL_ROOT/scripts/execution_contract.py audit /project/video/execution.bundle.json /project/video/observed.json --out /project/video/execution-audit.json
python3 SKILL_ROOT/scripts/execution_contract.py impact /project/video/previous.bundle.json /project/video/execution.bundle.json --out /project/video/rebuild.json
```

```text
python3 SKILL_ROOT/scripts/catalog.py --kind scenario list
python3 SKILL_ROOT/scripts/catalog.py --kind style list
python3 SKILL_ROOT/scripts/catalog.py --kind motion get reveal
python3 SKILL_ROOT/scripts/catalog.py --kind expression list --scenario brand-film
python3 SKILL_ROOT/scripts/catalog.py --kind expression get visual.target-callout
python3 SKILL_ROOT/scripts/catalog.py --kind recipe list --scenario music-visual
python3 SKILL_ROOT/scripts/catalog.py --kind recipe get product-task-proof
python3 SKILL_ROOT/scripts/catalog.py --kind recipe list --scenario product-promo
python3 SKILL_ROOT/scripts/catalog.py --kind recipe get 极简左右讲解 --json
python3 SKILL_ROOT/scripts/catalog.py --kind recipe get 源码说明片 --json
python3 SKILL_ROOT/scripts/product_ledger.py init /path/to/product-source --out /project/video/ledger.json
python3 SKILL_ROOT/scripts/product_ledger.py check /project/video/ledger.json --source /path/to/product-source --evidence-root /project/video --script /project/video/narration.txt
python3 SKILL_ROOT/scripts/production_tools.py list --task environment
python3 SKILL_ROOT/scripts/production_tools.py probe
python3 SKILL_ROOT/scripts/production_tools.py polyhaven-search --query studio --type hdris --limit 5 --cache-dir /project/video/cache/polyhaven
python3 SKILL_ROOT/scripts/production_tools.py aivis-speakers
python3 SKILL_ROOT/scripts/production_tools.py check /project/video/production-job.json --require-reviewed
python3 SKILL_ROOT/scripts/music_library.py search --scenario product-demo --emotion curious --role establish --avoid-bright --limit 5
python3 SKILL_ROOT/scripts/music_library.py select --recipe knowledge-music-explainer
python3 SKILL_ROOT/scripts/music_library.py select --recipe knowledge-music-explainer --source-file /project/music/chosen.wav
python3 SKILL_ROOT/scripts/validate_plan.py /project/video/plan.json
python3 SKILL_ROOT/scripts/knowledge_pack.py /project/video/plan.json
python3 SKILL_ROOT/scripts/controlled_lint.py --text-file /project/video/script.txt --profile ste-zh-spoken --glossary /project/video/plan.json
python3 SKILL_ROOT/scripts/check_delivery.py /project/video/plan.json /project/video/delivery.json --probe --require-video
python3 SKILL_ROOT/scripts/film_probe.py /path/to/film.mp4 --out /project/video/probe.json --frames-dir /project/video/probe-frames
python3 SKILL_ROOT/scripts/audio_event_audit.py /project/video/audio-event-map.json /project/video/sfx-stem.wav --out /project/video/audit.json
python3 SKILL_ROOT/scripts/explainer_timing_audit.py /project/video/knowledge-music-score.json --plan /project/video/plan.json --music-sheet /project/video/music-cue-sheet.json
```

## 音乐、主题与风格

`music_world.py init --music FILE --theme THEME --style 水墨|烟雨|理论概念 --into PROJECT` 创建不覆盖的项目，`analyse --project PROJECT` 保存候选分析并保留已编排事件，`validate --project PROJECT` 检查当前音轨身份和事件阶段。完整方法、路线与继续制作见 [音乐驱动三维世界](music-driven-world.md)。

## 产品宣传模板

`recipe get` 支持稳定 ID、精确中文名称和登记别名；英文忽略大小写，前后空白忽略。名称冲突时返回候选 ID，未知名称报错，不做模糊套用。`product-promo` 下首个模板为“极简左右讲解”（`product-split-explainer`），源码入口模板为“源码说明片”（`product-source-explainer`）；加载返回的模板与方法路径，再开始制作。

`product_ledger.py` 只读源码目录，不执行项目代码、不联网：`init` 调研名称、版本及出处、平台、文档、视觉资产与限制线索，写出账本骨架（线索只是候选，需回原文核对）；`check` 检查事实、侧重点、证据、章节与口播主张是否闭合，来源文件与行号是否存在，稿件有没有出现边界禁用词；可选的 `framings`（开场里替观众说话的句子）检查类型、章节与边界引用，顾虑必须写明由哪条边界收住，稿件里找不到原句时给出提醒。退出码 0 为闭合，1 为有未闭合项，2 为输入错误。检查不能判断事实是否正确，也不替代真实运行取证。

## 物体形象构建配方

```sh
python3 SKILL_ROOT/scripts/catalog.py --kind recipe get 水与液体构建
python3 SKILL_ROOT/scripts/catalog.py --kind recipe list --query 咖啡
```

元素级配方按对象、表现重点与镜头尺度匹配，不覆盖整片叙事配方。读取返回的 method_path、engineering_path 和 template_path；是否可运行、是否符合画面要求由项目实际验证。

开放海面已提供参数化实现入口，按 [开放海面构建配方](../objects/water-liquid/OCEAN.md) 核实环境、构建、渲染代表帧和连续片段。它执行本地 Blender，与本页只读目录查询不同；串行运行并在输出目录保存实际参数及测量。
