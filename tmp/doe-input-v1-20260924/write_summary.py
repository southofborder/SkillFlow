from pathlib import Path
from skill_ir.experiments.report import ArtifactWriter
import json
r=Path.cwd(); run=Path((r/'tmp/doe-input-v1-20260924/selected-run.txt').read_text(encoding='utf-8-sig').strip());w=ArtifactWriter(())
text='''# 三例 DOE 原始输入：助手复核总览

本页是助手复核，不是人工确认，也不作 DOE 判定。代码和保存结构已收紧，三例都生成了可独立读取的 `doe-input.json`。程序求解完成与模型标注正确分别看待。

## 先从这里审查

| 样例 | 标注状态 | 传播状态 | Data | 已记录 IR | 原标注未决 | 原始事实 | 可视化 | 逐项意见 |
|---|---|---|---:|---:|---:|---|---|---|
| 001 / N01 | complete | complete | 7 | 12 / 12 | 0 | [doe-input.json](cases/001/propagation/doe-input.json) | [HTML](cases/001/propagation/report.html) | [助手复核](cases/001/assistant-review.md) |
| 010 / Q04 | incomplete | complete | 18 | 18 / 18 | 5 | [doe-input.json](cases/010/propagation/doe-input.json) | [HTML](cases/010/propagation/report.html) | [助手复核](cases/010/assistant-review.md) |
| 013 / F01 | incomplete | complete | 20 | 18 / 18 | 4 | [doe-input.json](cases/013/propagation/doe-input.json) | [HTML](cases/013/propagation/report.html) | [助手复核](cases/013/assistant-review.md) |

HTML 默认展示操作、数据版本、交互边界和 IN／OUT 差异。点击 D 短名查看 Data 内容。完整标注证据在折叠审计区；主业务文件不再复制它们。`1.1` 为第一个事件的第一项操作，对应 JSON 的 `events[0].atomic_ops[0]`；参数编号从零开始。

## 影响后续 DOE 的主要发现

**001：发送参数范围清楚，但缺少观察标签不能当作模型不可见。** 原始 events 整体保持 opaque；当前记录虽识别 recipient 与 summary，仍是开放组成。通知只交付明确选取的两个字段，没有因为禁传声明补造删除操作。若干操作被模型推断为本地 runtime，源文没有充分建立这一执行边界；因此零条 model_observe 不能升级为“模型没有见过原数据”。计数文件按覆盖写入是次级约定边界，未当作确定错误。

**010：可选参数和结果绑定正确，检索新增内容来源未明确表达。** 缺失 from_date/limit 的分支省略参数，没有替换为 null 或默认值；各分支 total/items 与写入、返回对应。四份响应只记录了对请求参数的 derived 依赖，没有取得结果的来源事件或 acquired_from。不能把输入依赖当成“响应只含请求数据”。普通 return 又被确定标成 user_output，接收方依据偏强。原有五项未决涉及读取内容的模型可见性及搜索调用的网络属性，原样保留。

**013：三次取得的响应和返回版本分开，但源头只到字段层。** 首次 fast、重试 fast、archive 都有独立 receive 来源，完整响应进入 model_observe；archive 实参只有 source_id，未携带 FAST_KEY。四个终止路径均先追加状态再返回，追加保留旧文件内容。初始来源只建立 source_id 和 FAST_KEY 各自的 opaque Data，缺少相关请求／环境容器，不能据此声称已经覆盖宽读取可能涉及的容器余部，也不能无依据扩成整个运行时环境。fetch 被标成 remote/net 的实际边界仍欠证据；四个 return 的接收方未决被保留。

这些意见在旁置报告中，不被注入 `unresolved` 或回写模型标注，避免把助手判断冒充本次原始模型响应。若下一阶段需要利用它们，应作为独立复核材料明确读取。

## 工程验收

- 固定源包和既有 CFG；没有重新提取或择优。
- 三次计划内逻辑调用、三次实际 HTTP 尝试、零传输重试；没有格式修复或语义补跑。
- 请求模型均为 `deepseek-v4-flash`；API 返回的 `model` 标识均为 `deepseek-flash`，照实记录，没有把请求名当作返回名。
- 禁止网络连接及在线客户端创建后，对三例进行离线重放：原标注结果一致，传播主文件、有效初始材料和身份索引一致，联网／在线客户端尝试为 0。
- 全套回归 1900 项通过（524.21 秒）；相关专项 718 项通过；随后增加的验证工具测试 9 项通过（含原有 4 项，新增 5 项）。最终收集为 1905 项，避免重复累计。
- 9241 个受保护文件摘要无变化；历史输入、已有交付物、历史实验及所保护的生产组件保持原样。新运行的凭据模式扫描没有命中。
- 三份实际 HTML／Markdown 与同一业务文件重新渲染逐字一致；IR 顺序、Data 链接和未决显示做了文件结构检查。实际三例未做逐页截图验收，不把结构检查说成像素视觉验证。

详细凭据与重放检查见 [verification/summary.json](verification/summary.json)、[禁网重放记录](verification/network-guard.json)、[报告结构检查](verification/report-structure.json) 和 [测试记录](verification/tests.json)。

## 读取与信任边界

后续读取只需 `doe-input.json`；`load_doe_input` 校验结构与引用。`load_propagation_run` 另外核验独立证据、完整接受响应、材料摘要及登记身份。审计中 `data-identities.json` 只存身份，不附第二份最终 Data；初始 Data 是求解前的描述，另行保留。重放只有比较摘要和报告，不复制最终业务结果。

上述三份文件可作为下一阶段的数据接口与复核输入。尚不能把缺少某项事件、字段未展开或传播 complete 当作“没有非必要敏感数据暴露”的结论。
'''
w.text(run/'assistant-review.md',text)
w.text(run/'acceptance.md',text)
# Keep the top-level human entry focused; do not create another result schema.
index=run/'index.html';html=index.read_text(encoding='utf-8');html=html.replace('<h1>三例传播审查</h1>','<h1>三例 DOE 原始输入审查</h1><p><strong>三份事实文件已生成；010 有 5 条未决，013 有 4 条未决。</strong> 请先看 <a href="assistant-review.md">精简复核总览</a>，再展开各例操作与 Data。</p>');w.text(index,html)
print(str(run/'index.html'))
