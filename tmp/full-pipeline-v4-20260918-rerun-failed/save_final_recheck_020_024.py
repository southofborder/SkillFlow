import json
from pathlib import Path

root=Path(__file__).resolve().parent
r=json.loads((root/'final-visual-recheck-020-024-statistics.json').read_text(encoding='utf8'))
for c in r['cases']:
    c.update(reviewer='assistant',human_confirmed=False,outcome='no_visible_layout_defect',
      method='view_image: final staging full PNG plus every changed-pixel region in original-resolution context crops; identical SVG hash and RGBA comparison',
      observations=[
        f"实际查看最终完整图片 {c['width']}×{c['height']} 及所有差异区域裁切。标题编号、中文和英文、全部节点、控制边与终态布局没有可见缺陷。",
        f"与已查看预览的 SVG 字节摘要完全相同；RGBA 只有 {c['rgba_changed_pixels']} 个像素、{c['rgba_changed_channels']} 个颜色通道变化，最大通道差为 {c['maximum_channel_delta']}，alpha 没有变化。",
        '差异全部位于控制箭头末端的微小栅格化像素；实际细看箭头方向、终点和周围文字没有变化。结合完全相同的 SVG，未发现内容或布局改变。',
        '细节裁切为检查箭头而截取节点局部，裁切边沿不代表完整 PNG 被裁切；正式 PNG 已另行全图查看。',
        '本记录绑定最终 staging PNG 的实际 SHA-256；仅为助手静态视觉复核，非人工确认或语义正确证明。'])
(root/'final-visual-recheck-020-024.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('saved',[(c['case_id'],c['rgba_changed_pixels'],c['maximum_channel_delta']) for c in r['cases']])
