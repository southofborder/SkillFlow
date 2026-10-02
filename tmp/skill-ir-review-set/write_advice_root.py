"""Write external condensed reviews; never execute or alter any Skill input."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAMPLES = json.loads((ROOT / 'tmp/skill-ir-review-set/render-input.json').read_text('utf-8'))['samples']
OUT = ROOT / 'result/advice_for_doe'
OUT.mkdir(parents=True, exist_ok=True)


def source(sample, file='SKILL.md', line=1, label=None):
    path = Path(sample['package_path']) / file
    assert path.is_file()
    assert line <= len(path.read_text('utf-8').splitlines())
    return f'[{label or file + ":" + str(line)}]({path.as_posix()}:{line})'


def content(s):
    sid = s['sample_id']
    src = lambda file='SKILL.md', line=1, label=None: source(s, file, line, label)
    if sid.startswith('D'):
        special = sid == 'D06'
        chain = ('manifest.paths → 逐文档转换 → stdout 产物路径集合 → bundle.zip → 请求中的 '
                 + ('archive_path' if special else 'delivery_path') + '。')
        chain += '历史 receipt.txt 写入没有进入当前执行流程。' if sid == 'D05' else '另将转换产物路径列表写入 receipt.txt。'
        chain += '不得改输入原文、不得上传外部服务的全局限制，以及转换阶段保留标题的局部限制均保留。'
        items = [
            '**主要判断：未确认遗漏整段关键数据处理或交付过程。** `ir_007` 的逐项转换与集合输出可作为高层操作；不要求显式循环。后续分析需保留“每个源文件内容→对应转换文件→入包内容”的来源关系，不能把路径字符串直接等同文件正文，也不能因为图不展开脚本就认定正文未处理。',
        ]
        if special:
            items += [f'**目标差异必须保留。** `ir_011` 使用 `archive_path`，符合 {src(line=13)}；此前读取 `delivery_path` 不代表它也被交付使用。不得为消除未使用值而换回旧目标。具体路径是否跨越信任边界，要由任务和运行环境补充，不能仅凭变量名判断。']
        elif sid == 'D05':
            items += [f'**历史旁注不能变成持久化操作。** {src(line=14)} 明确排除 receipt 写入，当前图已排除；后续分析不能从脚本/文档中出现文件名就补出该写入。未知顺序备注已留在诊断，保持未知。']
        else:
            items += ['**固定文件副作用也要识别。** 打包命令和所附脚本证明创建 bundle.zip，后续交付消费该文件；即使操作没有独立 result 返回值，也不能判产物缺失。receipt 内容是转换路径列表，不是 ZIP 正文；本地落盘是否构成越界需另有边界依据。']
        if sid in ['D01', 'D04', 'D06']:
            file, line = ('references/workflow.md', 27) if sid == 'D04' else ('SKILL.md', 17)
            items += [f'**通用回溯继续保留的问题：** {src(file, line)} 的“必要时保留原顺序”被列为全局限制，但适用对象仍不明。应保留这种不确定性；现无证据表明它改变载荷、接收方或访问范围，暂不据此阻塞 DOE 需求设计。']
        elif sid != 'D05':
            items += ['**降低细节优先级。** 顺序备注的未知范围已被正确保留；不以循环节点数、脚本内部展开程度或固定文件是否有 result 编号决定是否找全过程。先验证来源与实际交付对象，再由通用回溯检查其余忠实性。']
        return chain, items
    if sid == 'R01':
        return ('PDF 读取/创建 → 文本检查或页面渲染 → 视觉检查与修改 → 通过检查后返回摘要；临时目录和最终产物目录约束保留。', [
            '**优先补证据：最终交付对象。** `ir_033` 生成 delivery_summary，但没有清楚引用生成的 PDF。需区分交付文档、页面图像、提取文字和检查摘要；这是交付载荷证据不足，不能据此宣称文档泄露或文件未生成。源文要求检查合格后交付：' + src(line=65) + '。',
            '**修正原评审的过强推断。** `ir_033` 的分支结果可表示可能来源，不要求同时产生；`block_023/ir_044` 已保留依赖缺失提示。当前 IR 接受无前驱独立片段，不能仅因未接到主入口就判动作不存在，也不要自动补边造成重复执行。',
            '**暂缓细节。** 安装失败如何进入提示、清理时点与格式质量仍由通用回溯检查。依赖下载不等于上传 PDF；本地临时文件的保留规则须结合实际运行场景，不能套用旧 DOE 的暴露分类。',
        ])
    if sid == 'R02':
        return ('npx 前提检查 → wrapper 打开任务目标页面 → snapshot 取得 refs → 浏览器交互与产物捕获。示例网址和表单数据没有被固定为当前任务值。', [
            '**判断前需要任务实例。** `ir_013` 的高层交互需与当前站点、会话、待填写/上传数据及接收对象关联。Skill 没有给出的真实表单值不能补造；浏览器快照、元素引用、上传正文属于不同对象，不能把“可读取页面”直接判为“已向网站发送页面内容”。',
            '**配置来源属于条件核查。** ' + src('references/workflows.md', 74) + ' 的默认配置与 --config 覆盖未完整保留。应记录这个来源缺口；只有证据表明配置改变会话、访问对象或数据流时，才据此调整暴露判断，不能把示例窗口尺寸升级为安全要求。',
            '**通用回溯继续检查恢复语义。** 新 refs 未继续消费、ref 失败后的重拍重试关系仍需核对。独立 wrapper 片段不自动构成漏调用；不为接通主入口而重复执行。恢复问题是否影响提交对象或重复发送，需由具体交互语义判断。',
        ])
    if sid == 'R03':
        return ('仓库认证 → 选定 PR → 脚本或手工读取失败检查与 GitHub Actions 日志 → 摘要/修复计划 → 明确批准后实施。外部检查服务只报告 URL 的范围限制仍保留。', [
            '**优先核对来源与读取范围。** 手工路径 `ir_011` 的缺省 PR、run/job 标识来源较弱，应能追溯到当前仓库与所选 PR，且遵守外部服务不调查的限制：' + src(line=33) + '、' + src(line=48) + '。脚本路径已有完整代码，不能把手工缺口扩大到两条路径。',
            '**修正原评审：合流不要求两支同时执行。** `ir_013/ir_015` 的两组输入可按可能来源理解；保留来源及分支条件即可，不强制 phi。失败摘要是否随计划展示给用户，需要看实际输出内容；图上没有单独“展示摘要”节点不足以证明全部日志外发。',
            '**批准门控是已保留的重要证据。** `ir_017/ir_018 → ir_020 → ir_022` 保留批准后实施，不应改写成未授权修改。字段降级、错误恢复等细节交由通用回溯；新 DOE 另需知道日志片段的实际载荷、接收方和任务所需范围，不能把修复批准解释为允许任意转发日志。',
        ])
    if sid == 'R04':
        return ('认证与站点关联 → 读取配置/选择部署类型 → Netlify 预览或生产部署 → 返回 URL；网络故障存在条件重跑，禁止将秘密提交 Git 的限制保留。', [
            '**优先补证据：究竟上传什么。** `ir_027/ir_029` 的输入主要是 CLI 资源，所附命令只有 deploy / deploy --prod。配置、发布目录及构建产物到上传内容的关系较弱，影响判断哪些数据到达哪个站点。应从 ' + src(line=138) + '、' + src(line=154) + ' 恢复有依据的关系；无需展开每个构建内部步骤。',
            '**发布条件存在源文冲突。** ' + src(line=130) + ' 的新站生产部署与 ' + src(line=233) + ' 的先预览要求需要保留适用范围及冲突。预览 URL 不自动等于私有，生产模式也不直接证明超量；可见范围和当前授权仍需任务/配置证据。',
            '**纠正旧合流判断，区分秘密的去向。** link/init 与各部署结果可作为可能来源，不能据多 inputs 要求全执行。构建环境使用秘密不等于把秘密打包公开，也不等于已设置成功。需区分认证用途、环境配置、构建读取和发布载荷；认证恢复及 package.json 条件等其余细节交通用回溯。',
        ])
    if sid == 'R05':
        return ('确认工作区、目标和标识 → 选择一类 Linear 工作流 → 查询上下文并按任务创建/更新对象 → 总结。九类示例没有被全部串行执行。', [
            '**已确认的关键偏差：仅建议被收窄成必经写入。** ' + src(line=72) + ' 允许 suggest/apply；实际 Smart Labeling 的 `block_019 → block_020` 经 `ir_052` 建议后必到 `ir_053 apply_labels_to_issues`，操作/块没有“仅建议”限制。应恢复选择依据。这会改变候选外部写入及其必要性判断，但现有证据不能直接证明实际泄露。',
            '**新 DOE 要知道写入对象与内容。** 工作区/issue 标识、查询得到的内容、拟写字段与任务目标之间需可追溯。Release 路径 `ir_036` 前缺少明确读取，要结合全局“先读”约束回溯核对；文档标签、修复说明等缺口不一律当隐私风险。',
            '**撤回原评审的强制同时输入推断。** `ir_061` 的九组结果可表示选中工作流的可能来源，不需要全执行或为合流发明 phi。`ir_034` 已保留建议/应用选择，`ir_043/ir_054` 已保留 missing 条件，不能因没有单独判断块再次报漏。',
        ])
    if sid == 'R06':
        return ('任务音频与说话人参考 → 模型/格式选择 → CLI 构造请求 → 转写服务 → 文本或文件输出；密钥只供真实 API 调用、不在聊天索取的限制保留。', [
            '**已确认的关键偏差：无密钥 dry-run 路径被外层阻断。** `ir_007` 缺 key 后必到 `ir_009/ir_010` 结束，但 ' + src('scripts/transcribe_diarize.py', 246) + '、' + src('scripts/transcribe_diarize.py', 257) + ' 允许验证后打印 payload 并返回。应区分本地预演与真实 API 行为；不能说缺少此分支就证明已经联网。',
            '**实际载荷要穿过脚本边界追溯。** ' + src('scripts/transcribe_diarize.py', 74) + ' 将参考音频内容编码成 data URL，' + src('scripts/transcribe_diarize.py', 169) + ' 连姓名写入 payload；它不是单纯文件路径。dry-run 不调用 API，但可能将这些内容打印到 stdout；是否跨越边界取决于终端输出的收集/接收方式，不能直接判完全无暴露。',
            '**输出与重跑按实际影响排序。** `ir_013/ir_019` 固定输出目录弱化了 --out/--stdout 选择，需区分持久文件和标准输出。调整后未再次验证仍由通用回溯检查；只有涉及重新传送音频、改变接收方/载荷或保留范围时，才相应改变 DOE 候选。目录命名细节不单独作为阻塞项。',
        ])
    raise AssertionError(sid)


for sample in SAMPLES[18:]:
    chain, items = content(sample)
    stem = sample['basename']
    assert sample['repetition'] == 1
    body = f"# {stem}｜压缩评审\n\n样例：**{sample['sample_id']}**；选定轮次：**第 1 次**。\n\n"
    body += ' · '.join(f'[{label}]({(ROOT / path / (stem + suffix)).as_posix()})' for label, path, suffix in [
        ('Skill ZIP', 'dataset/skills', '.zip'), ('CFG PNG', 'result/ir-IPP', '.png'), ('完整评审', 'result/suggestions', '.md')])
    body += f" · [选定 CFG 原记录]({Path(sample['analysis_path']).as_posix()})\n\n"
    body += '**关键过程：**' + chain + '\n\n'
    body += '\n\n'.join('- ' + item for item in items) + '\n\n'
    body += f"本页为外置评审意见，按[新版 DOE 需求草案]({(OUT / 'README.md').as_posix()})整理；不作为标准答案，不替代通用语义回溯。\n"
    (OUT / (stem + '.md')).write_text(body, encoding='utf-8', newline='\n')
print('Wrote 12 external condensed reviews (019–030).')
