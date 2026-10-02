# 030 transcribe｜语义评审

样例：**R06**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/030-transcribe.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/030-transcribe.png)。

模型/格式选择、首次校验与密钥保密限制保留，但无密钥 dry-run 被外层流程阻断，输出约定被收窄，调整后的结果也缺少再次验证。

## 需修改或注意的问题

1. **确定错转：外层密钥门控阻断合法 dry-run。** 源文脚本的 dry-run 在构造并打印请求后直接返回，不建立 API 客户端；见下方 R06-F07 的原文定位。实际 `ir_007` 后缺 key 必到 `block_005/ir_009/ir_010` 提示并结束，既未读 dry_run，也无无密钥预演旁路。建议区分真实调用与本地 dry-run，保留后者不要求 key 的路径；不能因脚本源码仍在 metadata 中就忽略外层阻断。

2. **关键步骤遗漏：调整后未再次验证。** [SKILL.md:15](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/SKILL.md:15)要求校验质量、说话人标签和分段，必要时每次作一项针对改动。实际 `ir_015` 只校验初次输出，调整后 `ir_019` 重跑，经 `block_010 → block_012` 直接 `ir_022` 返回。建议新输出重新进入验证，并保留是否继续调整的判断。原文的 single targeted change 不是最多重跑一次，不能擅自固定次数。

3. **输出位置和用户参数被固定值替代。** [SKILL.md:16](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/SKILL.md:16)有“在此仓库”条件，[SKILL.md:25](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/SKILL.md:25)要求评测 job-id 子目录，[SKILL.md:26](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/SKILL.md:26)要求多文件避免覆盖。两次 CLI 都直接传 output/transcribe/，没有 job-id、用户 --out/--stdout 或目录选择来源。建议绑定当前请求及运行场景，不能用缺少 job-id 的理由直接忽略层级约定。

4. **CLI 约束与主流程边界应分别检查。** [SKILL.md:20](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/SKILL.md:20)至第 22 行及 references/api.md 的格式/大小/说话人限制已保留在调用约束和完整脚本。图隐藏脚本并不构成遗漏；但需同时确认外层的模型、格式、输出参数不会覆盖合法 CLI 选择。音频时长与 auto 的适用条件应保留，不扩充原文没有的错误码或重试策略。

## 已保留的关键内容

`ir_003` 从请求取得音频、格式、语言和说话人信息；`ir_005` 保留默认转写与按请求 diarization 的选择，后续调用引用这些实际结果。缺 key 提示不要求在聊天中粘贴密钥；无提示词的 diarization 限制及已知说话人上限仍可核查。

## 逐项核对

以下对照[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/R06.json)的全部 11 项，仅判断当前选定轮次。新增问题另列在上文，不把事实表当作真实 Skill 的全部语义。

- **R06-F01｜部分保留**：收集音频文件路径、输出格式、可选语言提示和已知说话人参考，调用 bundled CLI；随后检查转录质量、说话人标签和分段边界，必要时做单一针对性调整；在此仓库工作时，将输出保存到 output/transcribe/。 原文：[SKILL.md:11](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/SKILL.md:11)；CFG：`ir_001`、`ir_003`、`ir_013`、`ir_015`、`ir_017`、`ir_019`、`ir_022`、`edge_8`、`edge_9`。

- **R06-F02｜保留**：实时 API 调用前要求本地 OPENAI_API_KEY；缺失则让用户在本地设置，绝不要求把完整密钥粘贴到聊天。 原文：[SKILL.md:13](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/SKILL.md:13)、[SKILL.md:39](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/SKILL.md:39)；CFG：`skill.constraints`、`ir_007`、`ir_009`、`edge_4`、`edge_5`。

- **R06-F03｜保留**：默认 gpt-4o-mini-transcribe 与 text；用户要求说话人标签或分离时选择 gpt-4o-transcribe-diarize 与 diarized_json，超过约 30 秒保持 auto 分块。 原文：[SKILL.md:18](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/SKILL.md:18)；CFG：`ir_005`、`ir_005.constraints`、`ir_013`、`ir_013.constraints`。

- **R06-F04｜保留**：diarize 模型不支持 prompt；脚本对该组合直接终止，并对非 diarize 模型请求 diarized_json 直接终止，不能静默忽略或改变请求参数。 原文：[SKILL.md:22](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/SKILL.md:22)、[SKILL.md:14](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/SKILL.md:14)、[scripts/transcribe_diarize.py:241](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/scripts/transcribe_diarize.py:241)；CFG：`ir_013`、`ir_019`、`ir_005.constraints`。

- **R06-F05｜保留**：已知说话人按 NAME=PATH 解析、读取参考音频并编码 data URL；姓名与参考列表一起传入 extra_body。参考最多 4 个，缺文件、格式不符或超量均终止。 原文：[SKILL.md:61](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/SKILL.md:61)、[SKILL.md:80](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/SKILL.md:80)、[references/api.md:7](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/references/api.md:7)、[scripts/transcribe_diarize.py:74](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/scripts/transcribe_diarize.py:74)、[scripts/transcribe_diarize.py:169](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/scripts/transcribe_diarize.py:169)；CFG：`ir_003`、`ir_013`、`ir_019`。

- **R06-F06｜保留**：CLI payload 始终含 model、response_format、chunking_strategy；language/prompt 仅有值才加入，speaker names 非空才加入 extra_body。音频以二进制文件对象连同 payload 传给 audio.transcriptions.create。 原文：[SKILL.md:14](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/SKILL.md:14)、[scripts/transcribe_diarize.py:155](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/scripts/transcribe_diarize.py:155)；CFG：`ir_013`、`ir_019`。

- **R06-F07｜错转**：dry-run 在验证与 payload 组装后只打印 JSON 并返回，允许没有 API key；正常分支才创建客户端和调用 API。不能因源码出现 API 调用而为 dry-run 增加网络行为。 原文：[SKILL.md:14](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/SKILL.md:14)、[scripts/transcribe_diarize.py:33](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/scripts/transcribe_diarize.py:33)、[scripts/transcribe_diarize.py:246](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/scripts/transcribe_diarize.py:246)；CFG：`ir_007`、`ir_009`、`ir_010`、`ir_013`、`edge_4`、`edge_5`。

- **R06-F08｜部分保留**：文档要求评估运行使用 output/transcribe/<job-id>/，多文件使用 --out-dir；--out 和 --stdout 仅支持单音频，--stdout 与 --out/--out-dir 不能同时使用。正常写文件分支优先采用 --out：若指向现有目录，则在其下按音频 stem 生成文件名；无后缀则补格式后缀，否则保留显式文件路径。未提供 --out 时，使用 --out-dir 或当前目录，文件名为 <stem>.transcript.txt（text）或 <stem>.transcript.json（其他格式），随后写出 UTF-8。--out-dir 本身不保证避免同 stem 输入覆盖同名输出；脚本未检测这类冲突，也未自动重命名。 原文：[SKILL.md:24](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/SKILL.md:24)、[SKILL.md:14](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/SKILL.md:14)、[scripts/transcribe_diarize.py:234](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/scripts/transcribe_diarize.py:234)、[scripts/transcribe_diarize.py:101](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/scripts/transcribe_diarize.py:101)、[scripts/transcribe_diarize.py:263](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/scripts/transcribe_diarize.py:263)；CFG：`ir_013`、`ir_019`、`skill.constraints`、`diagnostics`。

- **R06-F09｜保留**：参考文档把单次请求最大文件大小写为 25 MB，但脚本超过 25*1024*1024 bytes 仅警告，不停止、不裁切；不能将限制说明自动扩展为音频压缩、转码或客户端强制拒绝。 原文：[SKILL.md:80](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/SKILL.md:80)、[references/api.md:3](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/references/api.md:3)、[scripts/transcribe_diarize.py:18](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/scripts/transcribe_diarize.py:18)、[scripts/transcribe_diarize.py:145](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/scripts/transcribe_diarize.py:145)；CFG：`ir_013`、`ir_013.constraints`、`ir_019`、`ir_019.constraints`。

- **R06-F10｜保留**：Quick start 的 Alice/Bob 参考路径和 meeting.m4a 是示例实参，不是每次用户任务的固定输入；流程必须消费实际收集到的文件和参考。 原文：[SKILL.md:12](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/SKILL.md:12)、[SKILL.md:53](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/SKILL.md:53)；CFG：`ir_001`、`ir_003`、`ir_013`、`ir_019`。

- **R06-F11｜保留**：在前置验证通过且已知说话人姓名非空时，若 model 不含 transcribe-diarize，脚本发出仅支持 diarize 的警告，但仍将姓名和参考 data URLs 放入 extra_body，不会因该警告停止或删除参数。dry-run 只打印 payload 并返回；正常分支继续向 audio.transcriptions.create 传入该 payload。SDK/API 是否接受、拒绝或如何处理该组合属于包外未知，不能据此补写成功结果、服务端错误或自动回退。 原文：[SKILL.md:14](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/SKILL.md:14)、[scripts/transcribe_diarize.py:169](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/scripts/transcribe_diarize.py:169)、[scripts/transcribe_diarize.py:252](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/transcribe/scripts/transcribe_diarize.py:252)；CFG：`ir_013`、`ir_019`。

## 复核边界

dry-run 是否联网以脚本实际分支和外层可达路径为依据，不凭源码出现 API 名称推断。没有进行转写、联网或执行输入脚本；建议仅针对本轮选定图，保留原文未定义的失败与输出重名策略。

本次同时核对了[选定 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/R06/deepseek-v4-flash-max/1/analysis.json)中的 CFG、diagnostics 与相关 metadata。PNG 按既定范围不显示脚本全文和诊断；不能把展示省略直接判为提取遗漏，也不能仅凭结构校验成功判语义正确。

这些文件是外置语义评审意见（由 Codex 复核），供对照讨论，不代表已经由用户逐项确认，也不是改写后的标准答案。本次未修改 Skill 输入、ZIP、PNG 或生产流程，未运行 Skill 脚本和远端 API。
