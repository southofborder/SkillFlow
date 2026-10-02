from pathlib import Path
import json, hashlib
root = Path(__file__).resolve().parent
stats = json.loads((root/'final-recheck-029-030-stats.json').read_text(encoding='utf-8'))
cases=[]
for s in stats:
    c=s['case_id']
    mask=root/f'final-recheck-{c}'/'pixel-difference-mask.png'
    cases.append({'case_id':c,'png_sha256':s['png_sha256'],'reviewer':'assistant','human_confirmed':False,
        'outcome':'no_visible_layout_defect',
        'method':'view_image: final staging whole PNG, every listed original-resolution difference-region crop, and pixel-difference mask',
        'svg_equal':s['svg_equal'],
        'observations':[
            f"实际复看最终 staging PNG 整图及 {len(s['detail_review'])} 个连续重叠差异区域细节，不以旧预览替代最终图；尺寸仍为 {s['size'][0]}×{s['size'][1]}。",
            f"对应 SVG 字节完全相同；RGBA 比较有 {s['changed_pixels']} 个像素差异，最大通道差 {s['max_channel_difference']}，bbox={s['bbox']}。",
            '实际查看差异掩码和最终细节，差异呈控制线/曲线边缘的光栅化变化，未见文字、节点几何、条件标注或内容改变；箭头连接和长回边仍清楚，无可见遮挡或画布裁切。',
            '细节裁剪的边界会切到邻接节点文字，这是检查用裁剪范围，不是最终整图裁切；最终整图和原预览的完整内容已分别核对。',
            '复核绑定本次最终 PNG 的 SHA-256，仅为助手视觉复核，不改变 audit_error/incomplete/execution_error 等原有状态，不构成语义正确性证明。'],
        'detail_review':s['detail_review']+[{'png':str(mask),'sha256':hashlib.sha256(mask.read_bytes()).hexdigest()}]})
(root/'final-visual-recheck-029-030.json').write_text(json.dumps({'run_id':'full-pipeline-v4-20260918-rerun-failed','cases':cases},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
