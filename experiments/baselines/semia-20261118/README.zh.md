# Semia 同模型对照复刻：环境与离线验收

2026-11-18（Asia/Shanghai）。用户选择优先同模型、同一批 Skill 的公平对照。本目录独立于封存 GA4 和 SkillFlow 生产实现。这里记录环境建立及离线验收；**真实模型状态以各运行目录终止回执及[批次汇总](analysis/cohort-summary.zh.md)的观察时间为准**，不能把本文件的离线零调用计数当成整个目录的模型调用总数。

## 真实运行结果（2026-11-19）

本轮四例全部终止，后续没有待启动样本。合计65次原生调用、63份候选、1份有效表示；公开input+output已知2,840,131 tokens，另有GA4一次超时请求及provider内部未披露用量未知。完整结论见[四样本结果](../../../docs/research/semia-cohort-results-20261119.zh.md)。这只是固定开发样本的工程完成情况，不是准确率。

001 已于 2026-11-18 17:38（中国时间）结束：原版5轮共20候选全部被校验拒绝，管线exit 2，检测/报告/推荐均未运行。耗时5533.148秒，公开input+output用量376263 tokens；内部未披露用量未知。20原生请求正常返回，源码、输入及适配器未变，22个记录PID均已退出。详见[首例分析](analysis/001-failure-audit.zh.md)、[独立审阅](analysis/001-independent-review.json)及[root结案回执](analysis/001-closeout.json)。

首例分析完成后，010、013已于17:41各启动一次。010于17:47正常结束，4次调用（3次合成+1次推荐）、61957公开tokens、379.664秒；检测为零告警，语义覆盖边界见[010分析](analysis/010-analysis.zh.md)。013于19:09结束，20候选均被校验拒绝、391811公开tokens、5267.002秒；检测/报告/推荐未运行，详见[013分析](analysis/013-analysis.zh.md)及[root结案](analysis/013-closeout.json)。原21进程身份均有退出证据，终态后的数值PID复用另列，没有据旧PID停止其他进程。

GA4于11月18日17:48接续启动，11月19日00:43结束：21次原生调用（含一次超时后自动重试）、20候选全部无效、2,010,100已知公开tokens、24,869.019秒；检测/报告/推荐未运行。详见[GA4终态分析](analysis/ga4-analysis.zh.md)、[续接状态](continuation-state.json)与[批次汇总](analysis/cohort-summary.zh.md)。运行时最多两个独立样本并发；原版提示/校验/合成机制保留，采用明确命名的`controlled-complete-source-v1`输入适配：GA4完整16文件均送模，原版过滤结果另存不覆盖。001、013、GA4的检测未运行不能记为零告警；010的零告警也不是安全证明。

## 已完成

- 官方源码固定为 `berabuddies/Semia@379bc25fe99833eb185efe56a38fe15f0235799c`。本次 GitHub API、`git ls-remote` 与 tags 显示：当前 main、`v0.1.3` tag 和 9 月 20 日旧核查固定版本相同。latest-release API 曾 25 秒超时；`latest-release.json` 保留空结果，不用它证明 release 页面。
- 固定 SHA 的官方 codeload ZIP 已提取到 `source/`，360 个原始文件全部与归档逐字节一致；未改上游代码。见 `main-commit.json`、`tags.json`、`source-manifest.json`。
- 在 `.venv/` 用 Python 3.13.17 安装 `semia-audit==0.1.3`。安装禁用索引、依赖下载和构建隔离；上游运行时依赖列表为空。没有全局安装或改动 SkillFlow/CLI/用户配置。
- 官方纯 Python Datalog `builtin` 后端可用。7 个上游 core 模块共 292 项：289 通过、3 跳过、0 失败。两项需要未安装的 Soufflé，一项是默认关闭的语料统计打印。这不是上游全部测试，也不是论文指标复现。
- 对 001、010、013、GA4 的封存来源副本执行官方 `prepare`，全部 exit 0。本离线 setup 批次模型调用 0、Skill 执行 0。

## 输入可见性

| 输入 | 副本文件 | Semia 内联文件 | 语义单元 | 差异 |
|---|---:|---:|---:|---|
| 001 | 1 | 1 | 12 | 无 |
| 010 | 3 | 3 | 23 | 无 |
| 013 | 1 | 1 | 12 | 无 |
| GA4 | 16 | 14 | 623 | 原版忽略 `scripts/package.json`、`scripts/package-lock.json` |

全部 21 个输入文件均匹配 `input-manifest.json` 的封存来源 SHA-256；上表是最初官方默认prepare的离线结果，实际内联19/21。GA4两项遗漏来自上游`prepare.py`的`_SKIP_FILES_ALWAYS`默认策略，因此原版默认下“同一源包”成立，但“同一模型可见材料”不成立。原始过滤结果保留；后续另列的[完整输入适配](analysis/full-source-preflight/manifest.json)已离线验证21/21文件正文及实际提示完整纳入，GA4语义单元从623增至3155，运行成本和覆盖率分母随之变化。不能把默认过滤文件当作已审计，也不能将适配后的结果称作上游默认行为。

## 复现入口

以下 PowerShell 命令从仓库根目录运行；安装和 prepare 适用于新环境、新输出目录，已有原始产物不覆盖。

```powershell
$semiaRoot = Join-Path (Get-Location) 'experiments/baselines/semia-20261118'
python -m venv "$semiaRoot/.venv"
& "$semiaRoot/.venv/Scripts/python.exe" -m pip install --no-index --no-deps --no-build-isolation "$semiaRoot/source"
$env:PYTHONUTF8 = '1'
$env:SEMIA_DETECTOR_BACKEND = 'builtin'
& "$semiaRoot/.venv/Scripts/semia.exe" prepare "$semiaRoot/inputs/001" --out "$semiaRoot/prepared/001"
```

源码归档：<https://codeload.github.com/berabuddies/Semia/zip/379bc25fe99833eb185efe56a38fe15f0235799c>。按 `source-manifest.json` 的归档与文件 SHA-256 校验后提取到 `source/`。`source/`、`.venv/`、`downloads/` 是可恢复目录，由本目录 `.gitignore` 排除。

测试使用上述 venv Python，在 `source/` 工作目录，设置 `SEMIA_DETECTOR_BACKEND=builtin` 和 `PYTHONUTF8=1`：

```text
python -m unittest -v tests.core.test_datalog_eval tests.core.test_detector_report tests.core.test_prepare
python -m unittest -v tests.core.test_facts_checker_evidence tests.core.test_pipeline tests.core.test_repair tests.core.test_skill_corpus
```

日志：`logs/upstream-core-tests.log`（195 项）、`logs/upstream-pipeline-tests.log`（97 项）、`logs/install.log`、`logs/prepare-<id>.log`。`audit_setup.py` 只核对源码归档、输入哈希、prepare 清单、已完成测试日志与安装清单，写入 setup/source 清单；不重新运行模型、测试或 Skill。

## 模型与比较边界

上游默认 provider 为 `responses`、模型 `gpt-5.5`；Codex provider 未指定模型时继承 CLI 默认。synthesis 默认 5 轮、结构重试 3、provider retry 2、每次 timeout 600 秒。不能沿用这些默认值却称同模型同预算。

`llm_providers.py::_run_codex` 原版传 `--model` 和 `--sandbox read-only`，没有 reasoning-effort 选项，也没有禁用工具调用；其余配置可能从宿主继承。首例模型、high effort、预算和适配器差异由独立运行协议及实际 receipts 记录，不能只凭模型名证明一致。

本机没有可用 Soufflé、Docker 或已安装 WSL Linux；builtin 是上游正式支持的后端，但其与 Soufflé 的等价性未在本机重验。离线测试不证明论文准确率、任务必要性判断、未知输入可删性或 SkillFlow 优势。这四个已有调试样本是工程 pilot，未经人工标注，不是论文数据集，也不是代表性评测集。

机器可读证据见 `setup-report.json`，来源见 `input-manifest.json`，协议及真实首例结果以 root 另写文件为准。
