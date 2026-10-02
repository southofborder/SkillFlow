"""Transfer visual evidence only for equal rendered pixels, excluding page digits."""
from pathlib import Path
from collections import defaultdict
from PIL import Image, ImageDraw
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / 'tmp/pdfs/skill-ir-baseline-deepseek-final'
NEW = ROOT / 'tmp/pdfs/skill-ir-baseline-deepseek-final-v3'
STEM = 'skill-ir-baseline-results'

def page_hash(path):
    with Image.open(path) as source:
        image = source.convert('RGB')
    # Only the right-aligned page number at PDF y=22pt is masked.
    # The footer label, footer rule, all body text, and header remain compared.
    w, h = image.size
    rect = (w - 150, h - 46, w - 30, h - 20)
    ImageDraw.Draw(image).rectangle(rect, fill='white')
    return hashlib.sha256(image.tobytes()).hexdigest()

old_by_hash = defaultdict(list)
for path in sorted((OLD / STEM).glob('page-*.png')):
    old_by_hash[page_hash(path)].append(int(path.stem.split('-')[-1]))
matches, changed = {}, []
for path in sorted((NEW / STEM).glob('page-*.png')):
    number = int(path.stem.split('-')[-1])
    candidates = old_by_hash.get(page_hash(path), [])
    if candidates:
        matches[number] = candidates
    else:
        changed.append(number)
assert len(matches) + len(changed) == 730
old_info = json.loads((OLD / 'verification.json').read_text(encoding='utf-8'))['pdfs'][STEM + '.pdf']
new_info = json.loads((NEW / 'verification.json').read_text(encoding='utf-8'))['pdfs'][STEM + '.pdf']
report = {'old_pdf_sha256': old_info['sha256'], 'new_pdf_sha256': new_info['sha256'],
          'method': 'RGB pixel SHA256 with only bottom-right page-number rectangle masked; no rescaling',
          'mask_pixels': [760, 1241, 880, 1267], 'dpi': 110,
          'matched_final_to_old_pages': matches, 'changed_final_pages': changed,
          'matched_pages': len(matches), 'changed_pages': len(changed)}
(NEW / 'pixel_comparison.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k != 'matched_final_to_old_pages'}, ensure_ascii=False))
