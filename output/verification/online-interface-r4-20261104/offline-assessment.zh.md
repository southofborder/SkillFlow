# 接口衔接 r4 离线验收

本轮四项修复已经完成，按最新 XML 回执去重后的 591 个范围内用例通过，未解决失败为零。生产修改仅在五个接口与提示文件；没有新增模型字段、模型阶段或传播机制。正常路径仍为七调用，两个 worker，原有 Task／任务对应／敏感性隔离与纠正／修复预算保持。

这不是一次全仓库全绿运行。初次集成执行为 583 passed / 8 failed，耗时 1,088.84 秒，原回执保留。其后针对性重跑修正了两个维护样例同步问题和六个旧快照断言；没有重写初次失败记录。

| 修复 | 实际验证结果 | 仍保留的界限 |
|---|---|---|
| GA4 可选 case body | 合法省略 `segments` 与显式空数组通过展开、编译、拆分及组装；真实 `ir_027` 来源夹具保留 | 不把这一修复宣称为旧整份 processing 已语义完整 |
| 013 写入输出 | 独立修正候选处理 27/27 IR，四条 append 与四条 return 均保留；编译、传播、保存、读取与 DOE 路径通过 | 原有任务缺口仍为 partial，不把无完整 DOE 判定解释为安全 |
| 任务对应表达式引用 | 010/013 原始错误引用仍精确报错；测试副本显式复制程序展示的真实 target 后可组装和计算约束 | 010 的两项 only_if 仍为 potential_violation；013 只改引用的副本仍有写入阻断 |
| 审查归属 | 实际 001 缺失接收方禁止要求定位到 realization 后，路由到任务对应；注入工作流只重建 mapping 和复审，原独立材料复用 | 程序不从审查解释文字猜 owner，模型仍需定位到应改变的对象 |

表达式视图只显示 accepted processing 已有的 target 与表达式，不新增谓词或自动改写错误引用。010 为 2 条／453 字符，013 为 1 条／187 字符；连同指引和标题，新增提示分别约 1,263 和 997 字符。模型填写规模不变，文本长度不冒称 tokens 或任意 Skill 的容量保证。

## 集成失败的处理

两个 delivered-sample 失败来自当前合成示例的旧提示和契约文本。仅刷新九个生成文件：六份 prompt、两处运行时契约文字及一处对应哈希。其余 22 个文件逐字节不变，包括 CFG、Task、三份片段和编译 annotation。重跑两个用例通过。

六个 013 用例要求相邻 IR 的整份状态相等，与已接受的 record v16 精简快照不符。返回入口会裁去不再活跃的 `status.txt`，写入记录仍保留自身前后状态。测试改为检查真实返回操作数和版本、实际 response/body 或异常来源、写入 before/after 证据以及文件绑定的合法裁剪。整份小 Skill 回归模块加本轮 storage 回归共 28 个用例通过，未改传播代码。

初次失败和后续回执均见同目录 `offline-test-receipts.json`、`integrated-regression.xml`、`delivered-sample-diagnosis.xml`、`013-old-fixture-diagnosis.xml` 及相应刷新后的 XML。离线新真实模型调用、模型 tokens、Skill 执行和历史运行 replay 均为零；注入 fake client 的新临时用例重放属于离线验收。

## 接受版本与下一步

- Python source SHA: `b2d1966997e43b78f3a12c3afceb8e81e560137d619596af015238ee75333376`
- Broader implementation SHA: `889d202b5e65dcd3bbee478580ac2dd46af0da278cf19b32cee7803733a5932f`
- 接受回执：`offline-acceptance.json`；代码副本：`implementation-accepted/`。

接下来仅启动用户授权的一批全新 GA4 → 001 → 010 → 013。四例使用同一冻结实现、High 和逐字相同源包；各自重新生成全部分析材料，并由控制器执行一次零模型调用重放。只有真实结果关闭后，才报告完整传播、源码边界覆盖、DOE 有用性、未决问题及包括纠正／修复在内的实际 calls、tokens 和耗时。离线修正候选的结果不充当线上模型能力证据。
