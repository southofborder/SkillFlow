# 030 源包预读（助手，不执行 Skill）

已从冻结 dataset/skills/030-transcribe.zip 读取 SKILL.md、agents/openai.yaml、references/api.md 和完整 scripts/transcribe_diarize.py；许可证及图标只作来源/展示背景。等待末轮图和结果再判断，以下不是模型标注结论。

- 用户路径、输出格式、语言和 speaker references；OPENAI_API_KEY 检查缺失时只让用户本地设置，明确禁止要求粘贴完整密钥。
- 默认 mini/text，用户要 diarization 时 diarize/diarized_json；长音频 chunk auto；diarize 不支持 prompt。Skill 文档要求质量/labels/segment 校验并单项定向调整重跑，以及 repo 输出目录和 evaluation job-id 目录。
- 脚本还支持 dry-run/stdout/out/out-dir；stdin 不是输入来源。参数组合不合法会退出；key dry-run 可缺；普通请求必须有 key。
- 音频不存在 fatal，但超过 25MB 只是 warning，不拒绝。known-speaker NAME=PATH 校验存在后读取所有 reference 字节并 base64；超过 4 人的 fatal 在读取循环之后。非 diarize 模型带 speaker references 只警告，payload 仍包含 extra_body。
- payload 含 model/response_format/chunking_strategy，语言、prompt、speaker_names/references 条件加入。_run_one 打开主音频字节并远程 transcriptions.create。
- dry-run 会打印完整 payload（可含编码 speaker reference 音频）；不执行远程调用，但不代表未读本地文件/没有模型可见 stdout。该行为对下一步传播有用，不能根据“dry-run”名字忽略。
- 正常文件模式 write_text 转录内容后只 stdout 打印 Wrote <path>；只有 --stdout 直接输出转录内容。路径回传不等于已将整个转录文件内容回传控制 LLM。远程转录模型收到音频与控制 LLM 看到脚本 stdout 是不同观察通道。
- 程序 main CLI 默认未指定 out/out-dir 时写当前目录，而 Skill 建议调用层使用 output/transcribe/；需按调用层与脚本层分别解释，不能强行把脚本默认改写为始终符合 Skill 目录。
- default_prompt 额外说 clean summary；若未图示，需判断是当前激活接口要求还是通用背景，不能只靠内部结果叫 transcript 推出 summary 已存在。
