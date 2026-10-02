"""Transcribe source-grounded manual D04-D06 review notes; no API calls."""
from pathlib import Path
import importlib.util
import json
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'packages/skill-ir/experiments/semantics_baseline'
RUN = BASE / 'runs/baseline-deepseek-v4-flash-max-20260910'
spec = importlib.util.spec_from_file_location('review_results', BASE / 'tools/review_results.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
snapshot = review.read(RUN / 'operation_checkpoints/20260910T142626Z/report.json')
review.trials_for = lambda run, sid: sorted((t for t in snapshot['trials'] if t['case'] == sid), key=lambda t: t['repetition'])
samples = {s['id']: s for s in review.read(BASE / 'frozen/corpus/corpus.json')['samples']}

def a(rep, verdict, reason, *refs):
    return dict(repetition=rep, verdict=verdict, reason=reason, references=list(refs))

def save(sid, comparison, overall, rows):
    packet = review.read(RUN / 'review_packets' / f'{sid}.json')
    value = dict(schema_version=1, sample_id=sid, reviewer='Codex：对冻结原文、完整脚本及三轮实际 CFG 的逐项人工初审',
                 run_comparison=comparison, overall=overall,
                 analysis_sha256={str(r['repetition']): r['analysis_sha256'] for r in packet['runs']},
                 record_sha256={str(r['repetition']): r['record_sha256'] for r in packet['runs']},
                 facts=[dict(fact_id=f'{sid}-F{i:02d}', assessments=row) for i, row in enumerate(rows, 1)],
                 additional_findings=[])
    counts = review.validate_review(value, samples[sid], RUN)
    review.write(RUN / 'reviews' / f'{sid}.json', value)
    print(sid, dict(counts), sum(counts.values()))
    return counts

totals = Counter()
rows = [[] for _ in range(10)]
for rep in (1, 2, 3):
    request_id = 'ir_003' if rep == 1 else 'ir_005'
    scope_ref = 'block_004.constraints' if rep == 2 else 'ir_007.constraints'
    rows[0].append(a(rep, 'preserved', '实际读取 manifest.json、提取 paths，并从请求读取 output_dir 与 delivery_path；转换与交付分别使用这些读取结果，跨文件流程引用已进入当前 CFG。', 'ir_001', 'ir_003', 'ir_005'))
    rows[1].append(a(rep, 'partial', '转换指令的逐文档名称、单文档命令及完整 convert.py 保留了逐个意图、UTF-8 读取、创建目录、写入主名.txt 与 stdout 路径。但指令实际消费整份路径集合并一次产出转换列表，没有明确每个 path 与每次 stdout 的结构绑定。这是可验证表达粒度边界，待共同复核；不要求固定 loop opcode，也不判定逐个意图完全丢失。', 'ir_007'))
    rows[2].append(a(rep, 'preserved', '原文标题保留规则及“仅限转换、不限制汇总标题”的范围限制均保留在转换操作上。' if rep != 2 else '标题规则位于 block_004，该块只有转换调用和分派，实际范围仍仅限转换；原文明确排除汇总标题，未被提升到全局。', 'ir_007', scope_ref))
    rows[3].append(a(rep, 'preserved', 'convert.py 为一次黑盒脚本调用，metadata.script_content 与冻结完整脚本文本一致；内部读写没有拆成额外流程操作。黑盒约束落在转换所属范围。', 'ir_007', scope_ref))
    rows[4].append(a(rep, 'preserved', '被当前流程明确采用的打包示例已成为 package.py 调用，消费转换列表、输出 bundle.zip；完整脚本保留按文件 basename 写入 ZIP 的逻辑。', 'ir_007', 'ir_009'))
    rows[5].append(a(rep, 'preserved', '打包生成的 bundle.zip 结果与先前请求读取的 delivery_path 一起进入交付指令，交付目的地有实际数据引用。', request_id, 'ir_009', 'ir_011'))
    rows[6].append(a(rep, 'preserved', '额外回执步骤属于当前流程并独立执行；回执操作消费转换产物列表，写入 receipt.txt，未被打包或交付步骤吞掉。', 'ir_007', 'ir_013'))
    rows[7].append(a(rep, 'preserved', '不得修改输入文件的原文禁止事项保留为整份 Skill 的约束，未被缩小到某个操作。', 'skill.constraints'))
    rows[8].append(a(rep, 'preserved', '不得上传到外部服务的原文禁止事项保留为整份 Skill 的约束；本地交付不被凭空改写为外部上传。', 'skill.constraints', 'ir_011'))
    if rep == 2:
        rows[9].append(a(rep, 'contradicted', '原文未说明“必要时保留原顺序”约束谁；结果直接将其放入转换块 block_004.constraints，擅自确定了转换范围。未提升为全局仍不符合保留未知作用范围的约定。', 'block_004.constraints'))
    else:
        rows[9].append(a(rep, 'contradicted', '原文的原顺序备注作用范围未知，结果却将其放入 skill.constraints，擅自提升为全局规则。' + ('转换块名称还增加了 in order 表述。' if rep == 3 else '现有诊断讨论循环和回执顺序，未消除这一全局落点。'), 'skill.constraints', 'ir_007'))
totals.update(save('D04', '三轮均为 7 块、6 边，实际主流程均采用跨文件要求。第 1 轮先读请求再取 paths，后两轮相反，不影响数据来源；标题规则第 2 轮放在仅含转换调用的块内。原顺序未知范围三轮都被确定：第 1、3 轮全局，第 2 轮转换块。逐项转换的集合粒度问题三轮一致。', '主要读取、黑盒、打包、交付与回执行为保留。三轮转换逐项绑定均为待共同复核的部分保留；三轮未知范围备注均发生无依据的范围赋值。结构有效不等于本样例语义全部正确。', rows))

rows = [[] for _ in range(10)]
for rep in (1, 2, 3):
    scope_ref = 'block_004.constraints' if rep == 1 else 'ir_007.constraints'
    rows[0].append(a(rep, 'preserved', '读取 manifest.json、提取 paths，并读取请求中的 output_dir 和 delivery_path；转换及交付消费相应结果，数据来源明确。', 'ir_001', 'ir_003', 'ir_005'))
    rows[1].append(a(rep, 'partial', '逐文档转换意图、单文档命令和原始 convert.py 全文均保留，包括 UTF-8 读取、按需建目录、写入主名.txt 和打印路径。但实际指令仍以整份 paths 为输入、转换列表为输出，每个文档与每次 stdout 的绑定未在结构中明确。这是表达粒度的待共同复核点，不以缺少固定循环 opcode 作为判断理由。', 'ir_007'))
    rows[2].append(a(rep, 'preserved', '保留原文标题且仅约束转换、不限制汇总标题的原文要求落在转换范围内。' + ('第 1 轮使用只有转换调用与分派的 block_004，实际范围等价。' if rep == 1 else '未扩展为 Skill 全局规则。'), 'ir_007', scope_ref))
    rows[3].append(a(rep, 'preserved', '转换作为一次黑盒脚本调用，完整脚本与冻结来源逐字一致；内部读取、建目录、写入及打印没有膨胀成主流程子步骤。', 'ir_007', scope_ref))
    rows[4].append(a(rep, 'preserved', '打包示例被明确采用，实际 package.py 调用消费转换列表并生成 bundle.zip；保留完整打包脚本与 archive basename 逻辑。', 'ir_007', 'ir_009'))
    rows[5].append(a(rep, 'preserved', '交付操作实际消费 bundle.zip 结果及请求读取的 delivery_path，打包到交付的数据关系可追踪。', 'ir_005', 'ir_009', 'ir_011'))
    rows[6].append(a(rep, 'preserved', '本版本把回执改为历史示例。诊断明确说明排除历史回执，实际 CFG 在交付后结束，没有创建 receipt.txt 的操作，识别了文本用途的最小差异。', 'diagnostics', 'ir_011', 'ir_012'))
    rows[7].append(a(rep, 'preserved', '不得修改输入文件保持为 Skill 全局原文约束，作用范围与来源一致。', 'skill.constraints'))
    rows[8].append(a(rep, 'preserved', '不得向外部服务上传保持为 Skill 全局原文约束，未据此制造新的调用或上传行为。', 'skill.constraints'))
    rows[9].append(a(rep, 'preserved', '原顺序备注在 diagnostics 中保留，明确作用范围未确定；未擅自加入全局、基本块或操作约束。冻结约定要求未知范围留在诊断，因此这里采用诊断证据。', 'diagnostics'))
totals.update(save('D05', '三轮均为 6 块、5 边，历史回执均未进入执行路径；读取、转换、打包和交付保持一致。第 1 轮标题规则位于转换块，后两轮位于转换操作，实际范围一致。原顺序备注三轮均保留未知范围；逐文档转换仍采用集合输入的抽象。', '历史说明与当前指令的最小差异三轮均识别；未知作用范围三轮均妥善保留。唯一逐项部分保留点是转换的逐文档输入与 stdout 绑定表达粒度，需共同确认其可接受程度。', rows))

rows = [[] for _ in range(10)]
for rep in (1, 2, 3):
    conv, pack, archive, deliver, receipt = (('ir_005', 'ir_007', 'ir_009', 'ir_011', 'ir_013') if rep == 2 else ('ir_007', 'ir_009', 'ir_011', 'ir_013', 'ir_015'))
    request_id = 'ir_005' if rep == 3 else 'ir_003'
    read_refs = ['ir_001', 'ir_003'] if rep == 2 else ['ir_001', 'ir_003', 'ir_005']
    rows[0].append(a(rep, 'preserved', 'manifest.json 的 paths 是文档路径来源，同时实际读取请求的 output_dir 与 delivery_path；即使 delivery_path 在此最小差异版本不再用于交付，该读取行为仍保留。', *read_refs))
    rows[1].append(a(rep, 'partial', '逐文档意图、单文档命令及完整转换脚本保留了 UTF-8 读取、创建目录、写入主名.txt 和 stdout 路径。实际转换操作消费路径集合并产出列表，每个输入 path 与各次 stdout 的绑定未明确。此项为可验证表达粒度的部分保留，待共同复核；不要求某个固定循环 opcode。', conv))
    rows[2].append(a(rep, 'preserved', '标题保留及其仅作用于转换、不限制汇总标题的原文要求关联到转换调用，没有扩展到汇总或整份 Skill。', conv, conv + '.constraints'))
    rows[3].append(a(rep, 'preserved', '转换保持黑盒调用并附完整原始 convert.py，脚本文本已与冻结来源核对一致；未展开其内部读取和写入步骤。', conv, conv + '.constraints'))
    rows[4].append(a(rep, 'preserved', '实际采用 package.py 示例打包转换列表，输出文件为 bundle.zip；完整脚本保留按 basename 归档的行为。' + ('这里以文件写入副作用表达产物，未强制新增结果值。' if rep != 3 else '打包另有显式产物结果。'), conv, pack))
    rows[5].append(a(rep, 'preserved', '交付前单独读取请求的 archive_path，并把这一读取结果用作 bundle.zip 的交付目的地；先前 delivery_path 读取仍存在但不再使用。' + ('bundle.zip 的路径与前序黑盒写出的同一文件一致，文件副作用衔接成立。' if rep != 3 else '交付同时引用打包生成的产物结果。') + '数据改动已进入实际操作数，而非仅写在诊断中。', request_id, pack, archive, deliver))
    rows[6].append(a(rep, 'preserved', '回执仍是当前独立行为，消费转换产物列表并写入 receipt.txt；更改交付目的地未删除这一行为或改用打包内容作为输入。', conv, receipt))
    rows[7].append(a(rep, 'preserved', '不得修改输入文件的原文要求保持 Skill 全局范围。', 'skill.constraints'))
    rows[8].append(a(rep, 'preserved', '不得上传外部服务的原文要求保持 Skill 全局范围，交付仍对应本地请求路径。', 'skill.constraints', deliver))
    if rep == 1:
        rows[9].append(a(rep, 'contradicted', '未知范围的“必要时保留原顺序”被直接放进 skill.constraints，擅自提升为全局规则；关于 archive_path 和未使用 delivery_path 的诊断没有解决这一范围错误。', 'skill.constraints'))
    else:
        rows[9].append(a(rep, 'preserved', 'diagnostics 明确保留原顺序备注的作用范围不明，未把它分配给全局或某个操作。这与冻结约定中未知范围留待共同确认的表达一致。', 'diagnostics'))
totals.update(save('D06', '第 1、3 轮为 8 块、7 边，第 2 轮合并读取 manifest.paths 而为 7 块、6 边；三轮都额外读取 archive_path 并实际用于交付，仍保留未使用的 delivery_path 读取。前两轮用 bundle.zip 文件副作用衔接交付，第 3 轮使用显式打包结果，两者均有可追踪文件与目的地。第 1 轮错误将原顺序备注全局化，后两轮保持未知范围。', '交付目的地变化三轮均识别，黑盒、打包与独立回执行为保留。逐项转换绑定三轮均记为待共同复核的部分保留；第 1 轮另外存在未知范围被全局化的语义偏差。', rows))
print('TOTAL', dict(totals), sum(totals.values()))
