"""Bind completed visual observations and pixel evidence to the final PDF."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf/skill-ir-semantics-baseline-deepseek'
OLD = ROOT / 'tmp/pdfs/skill-ir-baseline-deepseek-final'
NEW = ROOT / 'tmp/pdfs/skill-ir-baseline-deepseek-final-v3'

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

build = read(OUT / 'build_manifest.json')
comparison = read(NEW / 'pixel_comparison.json')
render = read(NEW / 'verification.json')
content = read(OUT / 'content_qa.json')
digest = hashlib.sha256((OUT / build['pdf']).read_bytes()).hexdigest()
assert digest == build['pdf_sha256'] == comparison['new_pdf_sha256'] == content['pdf_sha256']
old_evidence = [read(OLD / name) for name in (
    'qa-segment-001-180.json', 'qa-segment-181-366.json',
    'qa-segment-367-546.json', 'qa-segment-547-728.json')]
old_pages = set()
for item in old_evidence:
    assert item['reviewed_pdf_sha256'] == comparison['old_pdf_sha256']
    old_pages.update(item['reviewed_pages'])
assert old_pages == set(range(1, 729))
root_final = {'reviewer': 'root', 'reviewed_pdf_sha256': digest,
              'reviewed_pages': [1,2,3,4,5,117,153,163,167,170,171,172,173,179,426,427],
              'full_size_pages': [1,2,3,4,5,117,153,163,167,170,171,172,173,179,426,427],
              'checks': ['Chinese glyphs, dense fact tables, command-like fields and identifiers legible',
                         'provider provenance fits on page 3; directory headers correct',
                         'trial directory page numbers updated',
                         'F05/R2 final return block and all fields kept together on page 427',
                         'no clipping, overlap, empty page, or orphan single metadata line'],
              'blocking_issues': []}
write(NEW / 'qa-changed-root.json', root_final)
new_evidence = [root_final, read(NEW / 'qa-changed-runner.json'), read(NEW / 'qa-changed-boundary.json')]
direct_pages = set()
for item in new_evidence:
    assert item['reviewed_pdf_sha256'] == digest
    direct_pages.update(item['reviewed_pages'])
changed = set(comparison['changed_final_pages'])
assert changed <= direct_pages
matched = set(map(int, comparison['matched_final_to_old_pages']))
for old_candidates in comparison['matched_final_to_old_pages'].values():
    assert set(old_candidates) <= old_pages
assert matched | changed == set(range(1, 731))
assert not matched & changed
qa = {'schema_version': 1, 'status': 'passed', 'pdf_sha256': digest, 'pages': 730,
      'render_dpi': 110, 'rendered_pages': 730, 'contact_sheets': 122,
      'all_final_pages_covered': True,
      'coverage_method': 'All 728 original rendered pages visually reviewed; 704 final pages have identical pixels except page-number digits; all 26 changed final pages re-inspected at full size. Every final page number and 90 trial headers checked separately from PDF text.',
      'pixel_comparison': comparison, 'prior_visual_evidence': old_evidence,
      'final_direct_visual_evidence': new_evidence,
      'directly_reinspected_final_pages': sorted(direct_pages),
      'content_qa': content,
      'fixed_layout_issues': ['provider provenance split with a three-line orphan',
                             'directory inherited previous running header',
                             'short first return split left a single draft_instruction_id on its continuation page'],
      'nonblocking_observations': ['Some trial tail pages are sparse but contain complete operations.',
                                   'Long operations may span pages; their fields remain continuous and source-verified.',
                                   'Full script_content is retained in analysis.json; the PDF labels the representation used for script hashes.'],
      'semantic_approval': 'pending_user_joint_review'}
write(OUT / 'visual_qa.json', qa)
render['visual_review'] = 'passed'
render['visual_qa_sha256'] = hashlib.sha256((OUT / 'visual_qa.json').read_bytes()).hexdigest()
render['coverage'] = {'pages': 730, 'identical_pixel_transfers': 704, 'changed_pages_reinspected': 26}
write(OUT / 'verification.json', render)
print(json.dumps({'pdf_sha256': digest, 'pages': 730, 'matched': len(matched),
                  'changed_reinspected': len(changed), 'status': 'passed'}, ensure_ascii=False))
