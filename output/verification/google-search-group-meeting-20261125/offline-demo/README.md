# Google Search 离线教学切片

本目录是手写语义的算法演示，不是在线模型输出，不是36块恢复CFG的完整标注，也不是完整Skill的DOE结论。没有模型调用、Skill执行或HTTP请求；输入只读取相邻的两个冻结原始源文件。

脚本实际调用当前生产代码的 `compile_response`、`propagate`、`materials_from_result` 与 `DemandEngine.solve`。6条手写IR表示三个独立输入读取、请求对象构造、配对的网络发送/响应获取和返回。所有值均是公开教学占位值；没有读取真实环境凭据。

`R_search`、`q/key/cx` 的接收边界需求及凭据敏感声明由本示例手写。敏感声明只指向 `ir_key` 获取的凭据值；查询和搜索引擎ID不因此继承凭据标签。`online-R6-reference-only.json` 独立保存真实在线提取的R6及其原任务身份，仅供来源对照，不能将R6直接冒充请求字段必要性证明。

主要证据：

- `scope.json`：来源身份、手写性质和遗漏范围。
- `propagation.json`：真实前向记录及Data注册表。
- `compiled-annotation.json`：编译后语义和局部凭据敏感声明。
- `authored-boundary-goals.json`：手工绑定到实际网络交付输入的三个字段保持目标。
- `backward-demands.json`：真实后向推导和接收边界上的需求范围。
- `summary.json`：精确字段Data绑定、仅G_key的有序推导链和规则计数。
- `checks.json`：执行中的断言结果。

请求中的 `key` 与原 `GOOGLE_API_KEY` 保持同一Data身份；后向需求由网络交付的 `params.key` 经构造算子传至对应凭据值。`num=5` 已传播，但不在本示例的三个需求种子中；其余范围明确未建立必要性，不能据此宣布num可删。响应保持为符号获取结果，不表示收到过真实Google响应。

未建模输入校验退出、HTTP异常构造与stdout，不建立错误输出泄露或可缩减结论；没有伪造独立语义审查或最终DOE结论。

在项目根目录执行：

```powershell
& 'C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' output/verification/google-search-group-meeting-20261125/offline-demo/run_demo.py
```

脚本只向本目录写入教学证据，不修改冻结在线运行、原始源包或图文件。
