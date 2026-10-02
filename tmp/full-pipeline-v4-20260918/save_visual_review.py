"""Record only PNGs actually inspected by the assistant; bind pixel files."""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
entries = []
for number in range(1, 9):
    preview = ROOT / ('preview-001' if number == 1 else 'preview-002-008')
    name = 'conditional-notification' if number <= 6 else 'catalog-query'
    png = preview / 'ir-IPP' / f'{number:03}-{name}.png'
    with Image.open(png) as image:
        width, height = image.size
    entries.append({
        'case_id': f'{number:03}', 'png': str(png),
        'sha256': hashlib.sha256(png.read_bytes()).hexdigest(),
        'width': width, 'height': height,
        'reviewer': 'assistant', 'human_confirmed': False,
        'method': 'view_image: full static PNG overview; renderer text/bounds audit checked separately',
        'checks': ['编号与修复轮次/状态可见', '中文未见缺字方框', '节点与文字边界无明显裁切',
                   '分支/循环箭头及完整条件标签可辨', '逐操作输入输出和约束排版正常'],
        'detail_review': ['008-top.png', '008-search.png'] if number == 8 else [],
        'outcome': 'no_visible_layout_defect',
        'notice': '静态视觉复核，不是图语义等价或安全标注正确性证明；最终同字节交付才可复用。',
    })
out = ROOT / 'visual-review.json'
out.write_text(json.dumps({'run_id': 'full-pipeline-v4-20260918',
    'reviewed_count': len(entries), 'cases': entries,
    'interactive_review_boundary': 'CUA 拒绝 file://，未绕过；既有离线UI测试与截图另存。'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
