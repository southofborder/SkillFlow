# Tool Dependency Validation Prompt Template

## Function A (Upstream)
- **Name**: {{func_a_name}}
- **Description**: {{func_a_description}}
- **Return Type**: {{func_a_output_type}}
- **Return Example**: {{func_a_output_example}}

## Function B (Downstream)
- **Name**: {{func_b_name}}
- **Description**: {{func_b_description}}
- **Input Parameters**: {{func_b_input_params}}
- **Input Type**: {{func_b_input_type}}

## Question
Can the output of Function A be used as input for Function B?

Please consider:
1. Type compatibility
2. Semantic relevance (should A's output logically be passed to B?)
3. Common tool usage patterns

## Response Format
```json
{
  "is_compatible": true/false,
  "confidence": 0.0-1.0,
  "reason": "Brief explanation",
  "data_flow_description": "Describe how data flows from A to B"
}
```
