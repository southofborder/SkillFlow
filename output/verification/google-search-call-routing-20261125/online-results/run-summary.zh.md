# google-search 线上全流程结果

本轮从 ClawHub 原始发行包的两个源文件重新提取 Task 和工作流，生成 CFG 和标注，并运行传播与 DOE。最终状态为 `partial`。本页及两张图使用同一轮选定的 CFG 和修订标注。[可浏览结果](index.html) · [全图 SVG](annotated-cfg.svg) · [逐条 IR 的标注](annotations.html)

## 调用方与控制流

自动生成的 CFG 首次通过结构校验，共 40 个基本块、75 条 IR、54 条控制边、103 处结果引用。两个入口分别进入各自的函数体。CLI 的 GET 位于 `ir_057`，成功后走向 `ir_065` 的结果打印，失败路径通向 `ir_071` 的错误打印。独立函数的 GET 位于 `ir_020`，正常返回和异常分别走向函数出口，从该入口无法到达 CLI 的 stdout。[控制路径逐项核验](entry-verification.json)

源码复审仍发现一个与异常类型有关的控制流缺口。CLI 源码通过 `except Exception` 选择要处理的异常，自动图把受保护区域的失败边直接连到处理器，遗漏了不匹配类型继续向外传播的路径。两个入口已经分开，处理器的匹配条件仍不完整。

## 标注与 DOE

图中列出全部 75 条 IR。最终选定的标注有 36 条 IR 具备操作语义，39 条保留为未建模。前向传播实际处理 6 条，在模块入口的 `ir_003`（导入 `sys`）和独立函数的 `ir_020`（发出 GET）停下，另有 67 条受阻。

这两处指令各有正常值和异常值两个互斥输出。CFG 通过边上的文字描述区分成功与失败，处理标注没有建立可供求解器执行的完成判定。正常值本身也不足以判断是否成功，例如正常返回的 JSON 可以是 `false`。

本轮解析了两项敏感性声明，选定标注中的边界声明数为 0。后端运行到了 DOE，实际边界比较数为 0，删减建议数为 0。本次结果不能判断请求或错误输出中的密钥是否过量暴露。[DOE 结果](results.json) · [后端原始 JSON](../../../../experiments/doe/runs/document-guided-google-search-call-routing-high-20261125-194132/doe/doe-result.json)

本次线上运行耗时约 31 分 56 秒，启动 13 次模型请求，记录到 622,178 个 token。调用方路由和兼容性离线验证共通过 281 项测试。[线上运行报告](../../../../experiments/doe/runs/document-guided-google-search-call-routing-high-20261125-194132/report.md)
