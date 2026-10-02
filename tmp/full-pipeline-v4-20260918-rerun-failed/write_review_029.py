import json
from pathlib import Path

root = Path(__file__).resolve().parent
row = json.loads((root / 'preview-029/review-data.json').read_text(encoding='utf-8'))['cases'][0]
review = {
    'run_id': row['run_id'], 'case_id': '029',
    'reviews': [{
        'revision': row['selected_revision'], 'graph_sha256': row['graph_sha256'],
        'assessment': '已复核完整可读源包、两轮图与反馈，以及末图的完整 PNG。第 1 轮图结构与回述保真通过，但本轮核对响应遗漏 4 个受控单元而被拒绝；安全标注因响应流中断失败，没有可用 profiles。不能将末图称为核对器通过图，也不能据空 profiles 得出没有安全效果。',
        'observations': [
            '执行失败归因要分开：feedback=audit_error 是 ResponseValidationError（漏引 fact:/blocks/6/instructions/0/constraints/0、fact:/constraints/14、15、18），并非 CFG 结构不合法或已发现 4 项语义错误；annotation=execution_error 是 IncompleteRead(0 bytes read)，validation=not_run、0/33 profiles。两者均不作为语义通过或未决项处理。',
            'r0→r1 有可定位的改进：入口先检查是否已配置（block_002）；config.toml/CLI 启用改为分支（block_004→005/006）；登录成功边才进入重启告知返回（007→008）；bulk 分支先说明 grouping logic 再写入（012→013→014）；末态显式返回 summary、gaps/blockers、next actions。读、写因未连接失败仍返回设置流程。',
            'Practical Workflows 的 9 个选择和 Available Tools 清单现在完整保留在 ir_018/ir_019 字面值。这样可核对选择对象，但这些自然语言候选并没有逐条编译为各自操作；后续传播不能把菜单里的 create cycle、comments 等都当成本次必执行，也不能宣称其内部行为已展开验证。',
            '遗漏边界仍需人工确认：SKILL.md 第 77–80 行生产力建议与第 84–87 行故障处理（清 cookie、重跑 OAuth、刷新 token、确认权限、拆分复杂请求等）没有进入末图。r0 核对器将其归为 context，因为不属于 Required Workflow；但建议/条件流程也可能带来读取或写入效果，不能由“非强制”直接推导为对安全分析无意义。可保留为条件语义，避免一律转成必执行主链。',
            '原文存在抽象边界：描述允许 read/create/update，Required Workflow 却统一写 create or update next；末图读成功后总进入 block_014。是否需要只读任务绕过写调用，应根据所选 workflow 的含义确认，不能仅凭这张图断言一定发生无依据写入。图级访问确认及 WSL 回退只是声明，没有额外操作保证。',
            '部分 r0 反馈有过度收紧倾向：并列 config_toml/codex_cli 候选输入加明确 or 约束，不足以证明旧图必同时执行两种方式；r1 分开后更易分析，但不等于已证实旧抽象错误。图标/展示元数据被补为图级约束，也不能与关键控制语义遗漏混为同等优先级。',
            '本次安全标注没有完整响应，因此未能审查 actor/roles/effects/evidences 的真实模型判断。现有图明确含远程 MCP transport/url、read/write 调用与 OAuth 等动作，未来应以这些内容和执行模型作证据；资源标识、调度主体或空数组本身不证明网络发送或模型观察。',
            '视觉复核实际查看 2161×11678 全图和 7 个连续重叠细节：029/R05/r1、失败状态、中文、33 个 IR、18 条边及长字面值均可读，未见遮挡或边界裁切。长图需放大滚动；显示的 metadata 边界与源码另行核对。此意见由助手复核，不是人工确认或语义等价证明。'
        ]
    }]
}
(root / 'assistant-reviews/029.json').write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
