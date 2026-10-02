import importlib.util
import sys
from pathlib import Path

ROOT = Path('D:/projects/SkillFlow')
RUN = ROOT / 'packages/skill-ir/experiments/propagation/runs/abstract-runtime-v1-20260928-143306'
sys.path.insert(0, str(ROOT / 'packages/skill-ir/src'))
from skill_ir.experiments.report import ArtifactWriter
from skill_ir.propagation.handoff import load_doe_input
spec = importlib.util.spec_from_file_location('runtime_pilot', ROOT / 'packages/skill-ir/experiments/propagation/tools/run_runtime_pilot.py')
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)
pilot.summarize(RUN, ArtifactWriter(()))
pilot.summarize(RUN, ArtifactWriter(()), replay=True)
for directory, prefix in ((RUN, ''), (RUN / 'replay', '../')):
    report = directory / 'report.md'
    report.write_text(report.read_text(encoding='utf-8') + '\n## 工程验收与助手复核\n\n'
        + '001 完成；010、013 在 DNS 解析阶段失败，每例首次加两次传输重试均未收到响应。三例离线重放零 API，状态一致。\n\n'
        + f'[查看完整工程验收和三例助手复核]({prefix}assistant-review.md)。该报告分别列出模型表现、证据不足和未证明的运行事实。\n', encoding='utf-8')
    page = directory / 'index.html'
    content = page.read_text(encoding='utf-8')
    block = '<aside style="padding:16px;border:1px solid #ccc;background:#f6f8fa"><strong>实际结果：001 完成；010、013 DNS 解析失败。</strong><p>失败案例各尝试连接 3 次，没有模型响应，没有生成 DOE 文件。三例离线重放均未调用网络。</p>'
    block += f'<p><a href="{prefix}assistant-review.md">工程验收与逐例助手复核</a>：001 保留了契约下的整体可能观察；字段配对精度、网络和执行主体依据仍需区分。</p></aside>'
    page.write_text(content.replace('</body>', block + '</body>'), encoding='utf-8')

# Independently read the actual business file without adjacent audit artifacts.
detached = ROOT / 'tmp/abstract-runtime-v1-verification/detached'
detached.mkdir(exist_ok=True)
target = detached / 'doe-input.json'
target.write_bytes((RUN / 'cases/001/propagation/doe-input.json').read_bytes())
value = load_doe_input(target)
assert value['schema_version'] == 'skillflow-doe-input-v3'
assert set(value['execution_model']) == {'version', 'sha256'}
print('Refreshed overview and review links; detached DOE validation passed.')
