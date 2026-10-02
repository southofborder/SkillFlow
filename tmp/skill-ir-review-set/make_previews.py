"""Create temporary overview and native-pixel detail views for the 30 PNG QA."""
from pathlib import Path
from PIL import Image
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'tmp/skill-ir-review-set'
DEST = WORK / 'previews'
DEST.mkdir(exist_ok=True)
audit = json.loads((WORK / 'export-audit.json').read_text(encoding='utf-8'))
manifest = []
for sample in audit['render_audit']['samples']:
    stem = sample['basename']
    source = ROOT / 'result/ir-IPP' / (stem + '.png')
    with Image.open(source) as raw:
        image = raw.convert('RGB')
    overview = image.copy()
    overview.thumbnail((1500, 1900))
    overview_path = DEST / (stem + '-overview.jpg')
    overview.save(overview_path, quality=92)
    boxes = [box for box in sample['bounds_checks'] if box['kind'] == 'card_on_canvas']
    header = next(box for box in boxes if box['id'] == 'header')
    nodes = [box for box in boxes if box['id'].startswith('node_')]
    first = next(box for box in nodes if box['id'] == 'node_0')
    dense = max(nodes, key=lambda box: box['height'])
    regions = [('header', header), ('first', first)]
    if dense['id'] != first['id']:
        regions.append(('dense', dense))
    details = []
    for label, box in regions:
        left = max(0, math.floor(box['x']) - 15)
        right = min(image.width, math.ceil(box['x'] + box['width']) + 15)
        top = max(0, math.floor(box['y']) - 15)
        bottom = min(image.height, math.ceil(box['y'] + box['height']) + 15)
        offset = top
        part = 1
        while offset < bottom:
            end = min(offset + 1500, bottom)
            destination = DEST / f'{stem}-{label}-{part}.png'
            image.crop((left, offset, right, end)).save(destination)
            details.append({'name': destination.name, 'box': [left, offset, right, end]})
            if end == bottom:
                break
            offset = end - 80
            part += 1
    manifest.append({'basename': stem, 'sample_id': sample['sample_id'],
                     'png_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                     'size': list(image.size), 'overview': overview_path.name, 'details': details})
(DEST / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'samples': len(manifest), 'preview_images': len(list(DEST.glob('*.png'))) + len(list(DEST.glob('*.jpg')))}))
