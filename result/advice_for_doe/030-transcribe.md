# 030-transcribe｜压缩评审

样例：**R06**；选定轮次：**第 1 次**。

[Skill ZIP](D:/projects/SkillFlow/dataset/skills/030-transcribe.zip) · [CFG PNG](D:/projects/SkillFlow/result/ir-IPP/030-transcribe.png) · [完整评审](D:/projects/SkillFlow/result/suggestions/030-transcribe.md) · [选定 CFG 原记录](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/R06/deepseek-v4-flash-max/1/analysis.json)

**关键过程：**任务音频与说话人参考 → 模型/格式选择 → CLI 构造请求 → 转写服务 → 文本或文件输出；密钥只供真实 API 调用、不在聊天索取的限制保留。

- **已确认的关键偏差：无密钥 dry-run 路径被外层阻断。** `ir_007` 缺 key 后必到 `ir_009/ir_010` 结束，但 [scripts/transcribe_diarize.py:246](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/scripts/transcribe_diarize.py:246)、[scripts/transcribe_diarize.py:257](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/scripts/transcribe_diarize.py:257) 允许验证后打印 payload 并返回。应区分本地预演与真实 API 行为；不能说缺少此分支就证明已经联网。

- **实际载荷要穿过脚本边界追溯。** [scripts/transcribe_diarize.py:74](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/scripts/transcribe_diarize.py:74) 将参考音频内容编码成 data URL，[scripts/transcribe_diarize.py:169](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/scripts/transcribe_diarize.py:169) 连姓名写入 payload；它不是单纯文件路径。dry-run 不调用 API，但可能将这些内容打印到 stdout；是否跨越边界取决于终端输出的收集/接收方式，不能直接判完全无暴露。

- **输出与重跑按实际影响排序。** `ir_013/ir_019` 固定输出目录弱化了 --out/--stdout 选择，需区分持久文件和标准输出。调整后未再次验证仍由通用回溯检查；只有涉及重新传送音频、改变接收方/载荷或保留范围时，才相应改变 DOE 候选。目录命名细节不单独作为阻塞项。

本页为外置评审意见，按[新版 DOE 需求草案](D:/projects/SkillFlow/result/advice_for_doe/README.md)整理；不作为标准答案，不替代通用语义回溯。
