"""Generate a partial static preview of explicitly reused terminal cases."""
from pathlib import Path

root = Path(__file__).resolve().parents[2]
source = root / 'tmp/full-pipeline-v4-20260918/render_partial_012_014.py'
text = source.read_text(encoding='utf-8')
text = text.replace('full-pipeline-v4-20260918', 'full-pipeline-v4-20260918-rerun-failed')
text = text.replace('012-014', 'reused-15').replace('012–014', '15 个复用样例')
text = text.replace('manifest["cases"][11:14]', '[case for case in manifest["cases"] if case["case_id"] in exporter.read_json(run / "rerun-provenance.json")["reused_cases"]]')
exec(compile(text, str(source), 'exec'), {'__file__': str(__file__), '__name__': '__main__'})
