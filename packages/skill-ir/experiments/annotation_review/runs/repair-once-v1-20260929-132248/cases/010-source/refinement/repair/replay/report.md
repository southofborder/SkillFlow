# 安全语义标注：repair

状态：**调用执行错误**（`execution_error`）

本页记录统一契约下的静态可能性，不是执行轨迹。默认读取与观察不表示真实运行必然如此；明确局部获取、返回或隔离机制约束默认范围。

统一抽象运行时契约：`skillflow-abstract-runtime-v3`；摘要：`26cd7f0d607b13377dc5d93546b9844b02f37db89b8dd8554613ea60e5b878ce`。

IncompleteRead(0 bytes read)

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`cdce0c44bb6531ac4058788c2510029e079e628fec77e691e7b54d24d2e59144`

[四字段标注](profiles.json) · [位置声明](locations.json) · [位置证据表](audit/location-evidences.json) · [符号传播说明](transfer-specs.json) · [校验记录](validation.json) · [完整结果](result.json)

## 执行问题与能力边界

错误类别：`execution`。

请求身份核验（不表示标注语义正确）：

```json
{
  "schema_version": "skill-ir-request-validation-v1",
  "config_sha256": "73ed56afcaa421a1448e0cd0058ab5192403256fe534ef248351578383426cb0",
  "prompt_sha256": "b7716a8970f0d83f7d109771fdaa93b20bcc2c09b9896f54d6de32d2b3dff8ea",
  "observed": true,
  "requests": [
    {
      "request_parameters": {
        "model": "deepseek-v4-flash",
        "reasoning_effort": "max",
        "response_format": {
          "type": "json_object"
        },
        "stream": true,
        "stream_options": {
          "include_usage": true
        }
      },
      "request_body_sha256": "e02501cc32789998fe19716b4d70d15ff9a596dc51603750ed031387d6e501de"
    }
  ],
  "transport": "http"
}
```

- IncompleteRead(0 bytes read)

## 按块查看

### block_001 · Read the user-supplied request.json

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_001 | read_request_json | 未接受 | 未接受 | 未接受 |
| ir_002 | dispatch | 未接受 | 未接受 | 未接受 |

### block_002 · Extract request.term and optional from_date and limit

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_003 | extract_query_term | 未接受 | 未接受 | 未接受 |
| ir_004 | extract_optional_from_date | 未接受 | 未接受 | 未接受 |
| ir_005 | extract_optional_limit | 未接受 | 未接受 | 未接受 |
| ir_006 | dispatch | 未接受 | 未接受 | 未接受 |

### block_003 · Call index.search once with the request term and optional arguments

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_007 | index.search | 未接受 | 未接受 | 未接受 |
| ir_008 | dispatch | 未接受 | 未接受 | 未接受 |

### block_004 · Write the response total to count.txt and return the response items

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_009 | extract_response_total | 未接受 | 未接受 | 未接受 |
| ir_010 | write_count_file | 未接受 | 未接受 | 未接受 |
| ir_011 | extract_response_items | 未接受 | 未接受 | 未接受 |
| ir_012 | return | 未接受 | 未接受 | 未接受 |

## 符号传播说明

以下为程序编译后的符号操作。处理段来自模型标注，model_observe 由程序依据处理方式与运行时契约生成；编译不证明处理方式的语义判断正确。尚未执行数据传播，符号引用不是 Data ID。

[原始处理段](audit/raw-annotation.json) · [编译后完整响应](audit/compiled-response.json) · [编译位置映射](audit/compilation-map.json)


## 标注依据

## 分析边界

这里只列举动作属性并声明符号传播操作。未执行 Skill，没有实际数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是统一抽象运行时契约中的保守默认。工具内部读取、工具返回和进入模型请求是不同边界；引文匹配只核验证据存在，不证明推断成立。
effects 保留逐次效果位置；order=partial 时，按约束计算可能安排，数组不是唯一执行次序。程序不证明模型推断正确。
context_write 表示后续可读的运行时上下文内容或绑定发生修改；它不自动等于 transform、fs_write 或 model_observe，普通 IR 结果绑定也不自动构成上下文写入。
空 effects 不等于空操作，也不能推出入口与出口状态相同；无法形成必要关系时明确记录任务失败。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
