"""Render the completed result PDF using the existing shared Poppler helper."""
from pathlib import Path
import argparse
import importlib.util
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--render-dir', type=Path, default=ROOT / 'tmp/pdfs/skill-ir-baseline-deepseek-final')
args = parser.parse_args()
pdf_dir = ROOT / 'output/pdf/skill-ir-semantics-baseline-deepseek'
spec = importlib.util.spec_from_file_location('review_pdf_verifier', ROOT / 'packages/skill-ir/experiments/semantics_review/tools/verify_pdfs.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
build = json.loads((pdf_dir / 'build_manifest.json').read_text(encoding='utf-8'))
pdf = pdf_dir / build['pdf']
assert build['report_kind'] == 'full_results' and build['fact_assessments'] == 891
assert m.sha(pdf) == build['pdf_sha256']
assert shutil.which('pdftoppm')
report = {'schema_version': 1, 'dpi': 110, 'content_verification': build['content_verification'],
          'visual_review': 'requires_manual_inspection',
          'pdfs': {pdf.name: {'pages': build['pages'], 'sha256': build['pdf_sha256']}}}
m.render(pdf_dir, args.render_dir, report, shutil.which('pdftoppm'), 110)
(args.render_dir / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Verification:', args.render_dir / 'verification.json')
