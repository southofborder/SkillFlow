"""Render the selected complete SkillFlow bundle as editable English SVG.

Read-only to runs and implementation. No Graphviz or online clients required.
The optional PNGs are QA previews; the SVG keeps every text character/vector.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
import hashlib
import json
from pathlib import Path
import shutil
import textwrap
import xml.etree.ElementTree as ET
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
INK, MUTED = '#172A3A', '#475569'
CTRL, DATA = '#40556B', '#0F766E'
FONT, LINE, BLOCK_W = 16, 21, 1800
COL_GAP, ROW_GAP, LEFT = 150, 180, 240
CFG_W = 660


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),
                                     allow_nan=False).encode('utf-8')).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def reference(run, value):
    path = (run / value['path']).resolve()
    if not path.is_relative_to(run):
        raise ValueError('A selected reference escapes its run directory: ' + str(path))
    if value.get('sha256') and digest(path) != value['sha256']:
        raise ValueError('Selected file digest differs: ' + str(path))
    return path


def load_bundle(run):
    run = run.resolve()
    selection_path = run / 'selection.json'
    if not selection_path.is_file():
        raise ValueError('No selected bundle is saved yet; wait for selection.json rather than guessing a candidate.')
    selection = read(selection_path)
    paths = {name: reference(run, selection[name]) for name in ('task', 'cfg', 'annotation')}
    annotation = paths['annotation'].parent / 'audit/wire-annotation.json'
    if not annotation.is_file():
        raise ValueError('The selected annotation has no saved complete wire-annotation.json')
    graph = read(paths['cfg'])
    cfg = graph.get('cfg', graph)
    status = read(run / 'result.json') if (run / 'result.json').exists() else {}
    return {'run': str(run), 'selection': selection, 'view_kind':'selected', 'selection_committed':True,
            'cfg': cfg, 'task': read(paths['task']),
            'annotation': read(annotation), 'status': status,
            'files': {**{name: {'path': str(path), 'sha256': digest(path)} for name, path in paths.items()},
                      'wire_annotation': {'path': str(annotation), 'sha256': digest(annotation)},
                      'selection': {'path': str(selection_path), 'sha256': digest(selection_path)}}}


def load_diagnostic_bundle(run):
    """Explicit uncommitted view of original accepted stage artifacts only.

    Revision candidates, raw replies, teaching annotations, correspondence and
    sensitivity fragments are never merged by this display-only contingency.
    """
    run=run.resolve()
    if (run/'selection.json').exists():
        raise ValueError('Diagnostic fallback requires NO selection.json; use the normal selected renderer.')
    result=read(run/'result.json')
    if result.get('status') not in {'failed','complete','partial','interrupted','diagnostic_complete'}:
        raise ValueError('Diagnostic fallback requires a saved terminal run status, not a live run.')
    if result.get('selected_annotation') is not None:
        raise ValueError('Terminal result claims a selected annotation; missing selection.json is inconsistent, not an uncommitted fallback.')
    verified={}

    def bound(owner,ref):
        path=(owner/ref['path']).resolve()
        if not path.is_relative_to(run):
            raise ValueError('An original stage dependency escapes the terminal run.')
        return reference(run,{'path':path.relative_to(run).as_posix(),**({'sha256':ref['sha256']} if 'sha256' in ref else {})})

    def manifest(owner, expected=None):
        path=owner/'manifest.json'; value=read(path)
        if canonical({k:v for k,v in value.items() if k!='manifest_sha256'})!=value.get('manifest_sha256'):
            raise ValueError('Unsealed stage manifest: '+str(path))
        producer=value.get('implementation',{})
        if canonical(producer.get('files',{}))!=producer.get('sha256'):
            raise ValueError('Unbound producer identity: '+str(path))
        if expected is not None and producer.get('sha256')!=expected:
            raise ValueError('Original stage belongs to another implementation: '+str(path))
        for name,sha in value.get('files',{}).items():reference(owner,{'path':name,'sha256':sha})
        verified[str(path.relative_to(run))]={'sha256':digest(path),'manifest_sha256':value['manifest_sha256']}
        return value

    main=manifest(run); implementation=main['implementation']['sha256']
    if result.get('identity')!=main.get('identity'):
        raise ValueError('Terminal result belongs to another run protocol.')
    source=manifest(run/'source',implementation)
    if reference(run,main['source'])!=run/'source/manifest.json':
        raise ValueError('Run source reference does not bind its original source manifest.')
    snapshot=read(run/'source/inputs/snapshot.json')
    source_sha=snapshot['source_sha256']

    def source_owner(owner,ref):
        target=(owner/ref['path']).resolve()
        if target!=run/'source' or ref.get('manifest_sha256')!=source['manifest_sha256']:
            raise ValueError('Stage source identity does not match the original frozen source.')

    task_owner=run/'task'; tm=manifest(task_owner,implementation)
    source_owner(task_owner,tm['source_owner'])
    task=read(task_owner/'task.json'); tr=read(task_owner/'result.json')
    task_hash=canonical({k:v for k,v in task.items() if k!='task_sha256'})
    if (tr.get('status')!='complete' or not tr.get('accepted_call')
            or tm.get('identity')!=tr.get('identity') or tm.get('config')!=main.get('config')
            or tm.get('task_schema_version')!=task.get('schema_version')
            or tr.get('task_ref',{}).get('task_schema_version')!=task.get('schema_version')
            or task_hash!=task.get('task_sha256') or tr.get('task_ref',{}).get('task_sha256')!=task_hash
            or task.get('source_sha256')!=source_sha or tm.get('source_sha256')!=source_sha
            or tr.get('source_sha256')!=source_sha):
        raise ValueError('Original Task has no matching complete acceptance and sealed source identity.')
    verified['task/task.json']={'sha256':digest(task_owner/'task.json'),'task_sha256':task_hash}

    def stage(name,kind):
        owner=run/'steps'/name; sm=manifest(owner,implementation); sr=read(owner/'result.json')
        if sm.get('kind')!=kind or sr.get('identity')!=sm.get('identity') or sm.get('config')!=main.get('config'):
            raise ValueError('Original stage kind, protocol or configuration differs: '+name)
        source_owner(owner,sm['context']['source_owner'])
        for dep in sm.get('dependencies',[]):bound(owner,dep)
        chain=read(owner/'calls/chain.json')
        if canonical(chain)!=sr.get('response_chain_sha256') or chain.get('accepted_call')!=sr.get('accepted_call'):
            raise ValueError('Stage acceptance is not bound to its actual response chain: '+name)
        value_path=reference(owner,{'path':sr['value_file']}); value=read(value_path)
        if digest(value_path)!=sr.get('value_sha256'):
            raise ValueError('Accepted stage value digest differs: '+name)
        if sr.get('status','complete') not in {'complete','partial'}:
            raise ValueError('Stage did not publish accepted independently validated records: '+name)
        if sr.get('status','complete')=='complete' and not sr.get('accepted_call'):
            raise ValueError('Complete stage has no accepted call: '+name)
        verified[str(value_path.relative_to(run))]={'sha256':digest(value_path),'value_sha256':sr['value_sha256']}
        return sm,sr,value

    gm,gr,graph=stage('graph','graph_facts_v1')
    graph_path=run/'graph/initial.json'; cfg=read(graph_path).get('cfg')
    if cfg is None or graph.get('cfg')!=cfg:
        raise ValueError('Original graph/initial.json is not the accepted graph stage value.')
    verified['graph/initial.json']={'sha256':digest(graph_path)}
    annotation={'ir_semantics':{},'locations':{},'processing_gaps':[]}
    processing_status='unavailable'
    processing_owner=run/'steps/processing'
    # Absence is shown as absence; an existing purported accepted value must validate.
    if (processing_owner/'value.json').is_file():
        pm,pr,processing=stage('processing','processing_fragment')
        if pm['identity']!=gm['identity'] or bound(processing_owner,pm['context']['cfg_path'])!=graph_path:
            raise ValueError('Processing was not accepted against this exact original graph version.')
        if set(processing)-{'ir_semantics','locations','processing_gaps'}:
            raise ValueError('Expected a processing-only accepted fragment; refusing a merged or candidate view.')
        ids={ir['id'] for block in cfg['blocks'].values() for ir in block['instructions']}
        if not set(processing['ir_semantics'])<=ids:
            raise ValueError('Processing contains instructions from another graph.')
        rejected={g['instruction_id'] for g in pr.get('validation_gaps',[]) if g.get('unmodeled')}
        if rejected & set(processing['ir_semantics']):
            raise ValueError('A quarantined processing record cannot be shown as accepted.')
        annotation.update(processing)
        annotation['_validation_gaps']=pr.get('validation_gaps',[])
        processing_status=pr.get('status','complete')
    elif (processing_owner/'result.json').is_file():
        receipt=read(processing_owner/'result.json')
        if receipt.get('value_file') or receipt.get('value_sha256'):
            raise ValueError('Processing acceptance receipt names a missing value; refusing to hide artifact loss as absent annotations.')
    annotation['_diagnostic_view']={'assembly_commit':'absent; no selection.json',
        'material':'Original independently accepted processing records only; not assembled annotation.',
        'processing_status':processing_status,'task_correspondence':'not combined','sensitivity_fragment':'not combined',
        'excluded':'All revision stages, raw responses, rejected candidates and teaching annotations.'}
    return {'run':str(run),'view_kind':'diagnostic_uncommitted','selection_committed':False,
        'selection':None,'cfg':cfg,'task':task,'annotation':annotation,'status':result,
        'files':verified,'acceptance_note':'Terminal original-stage display only; assembly did not commit.'}


def lines(value, width):
    """Wrap without ellipsis or dropped whitespace/characters."""
    source = json.dumps(value, ensure_ascii=False, indent=2)
    result = []
    for line in source.splitlines():
        result.extend(textwrap.wrap(line, width=width, replace_whitespace=False, drop_whitespace=False,
                                    break_long_words=True, break_on_hyphens=False) or [''])
    return result


class Canvas:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.root = ET.Element(f'{{{NS}}}svg', {'width': str(width), 'height': str(height),
            'viewBox': f'0 0 {width} {height}', 'role': 'img', 'aria-labelledby': 'figure-title figure-desc'})
        ET.SubElement(self.root, f'{{{NS}}}title', {'id': 'figure-title'}).text = 'Complete selected annotated SkillFlow CFG'
        ET.SubElement(self.root, f'{{{NS}}}desc', {'id': 'figure-desc'}).text = (
            'All selected CFG blocks, instructions, control edges and result references, complete wire annotations, '
            'Task and global annotation fields. Plain editable SVG text. Zoom to read the full-size cards.')
        defs = ET.SubElement(self.root, f'{{{NS}}}defs')
        for name, color in [('control-arrow', CTRL), ('data-arrow', DATA)]:
            marker = ET.SubElement(defs, f'{{{NS}}}marker', {'id': name, 'markerWidth': '10', 'markerHeight': '10',
                'refX': '9', 'refY': '5', 'orient': 'auto', 'markerUnits': 'userSpaceOnUse'})
            ET.SubElement(marker, f'{{{NS}}}path', {'d': 'M 0 0 L 10 5 L 0 10 Z', 'fill': color})
        self.preview = []

    def group(self, name, label=None):
        g = ET.SubElement(self.root, f'{{{NS}}}g', {'id': name})
        if label:
            ET.SubElement(g, f'{{{NS}}}title').text = label
        return g

    def rect(self, x, y, w, h, fill='white', stroke='#CBD5E1', radius=10, parent=None):
        ET.SubElement(parent if parent is not None else self.root, f'{{{NS}}}rect', {
            'x': str(x), 'y': str(y), 'width': str(w), 'height': str(h), 'rx': str(radius),
            'fill': fill, 'stroke': stroke, 'stroke-width': '1.5'})
        self.preview.append(('rect', x, y, w, h, fill, stroke))

    def text(self, x, y, text, size=FONT, color=INK, bold=False, mono=False, parent=None):
        ET.SubElement(parent if parent is not None else self.root, f'{{{NS}}}text', {
            'x': str(x), 'y': str(y), 'font-family': 'Consolas, DejaVu Sans Mono, monospace' if mono else 'Segoe UI, Arial, sans-serif',
            'font-size': str(size), 'font-weight': '700' if bold else '400', 'fill': color,
            '{http://www.w3.org/XML/1998/namespace}space': 'preserve'}).text = str(text)
        self.preview.append(('text', x, y, str(text), size, color, bold, mono))

    def path(self, points, color, data=False, parent=None, identity=None, title=None):
        element=ET.SubElement(parent if parent is not None else self.root, f'{{{NS}}}path', {
            'd': 'M ' + ' L '.join(f'{x} {y}' for x, y in points), 'fill': 'none',
            'stroke': color, 'stroke-width': '1.7' if data else '2.7',
            'stroke-opacity': '.43' if data else '.9', 'stroke-dasharray': '7 5' if data else 'none',
            'stroke-linejoin': 'round', 'marker-end': 'url(#data-arrow)' if data else 'url(#control-arrow)'})
        if identity:element.set('id',identity)
        if title:ET.SubElement(element,f'{{{NS}}}title').text=title
        self.preview.append(('path', points, color))

    def text_lines(self, x, y, content, parent=None):
        for n, line in enumerate(content):
            self.text(x, y + n * LINE, line, mono=True, parent=parent)


def ranks(cfg):
    successors = {b: set() for b in cfg['blocks']}
    for edge in cfg.get('edges', []):
        successors[edge['source_block_id']].add(edge['target_block_id'])
    index, stack, active, low, seen, components = {}, [], set(), {}, {}, []

    def visit(v):
        index[v] = low[v] = len(index)
        stack.append(v); active.add(v)
        for w in sorted(successors[v]):
            if w not in index:
                visit(w); low[v] = min(low[v], low[w])
            elif w in active:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            component = []
            while True:
                w = stack.pop(); active.remove(w); component.append(w)
                if w == v: break
            components.append(component)
    for block in successors:
        if block not in index: visit(block)
    owner = {b: i for i, comp in enumerate(components) for b in comp}
    outgoing = {i: set() for i in range(len(components))}
    indegree = Counter()
    for b, dests in successors.items():
        for dest in dests:
            if owner[b] != owner[dest]: outgoing[owner[b]].add(owner[dest])
    for targets in outgoing.values():
        indegree.update(targets)
    q = deque(i for i in outgoing if not indegree[i])
    level = defaultdict(int)
    while q:
        i = q.popleft()
        for j in sorted(outgoing[i]):
            level[j] = max(level[j], level[i] + 1)
            indegree[j] -= 1
            if not indegree[j]: q.append(j)
    return {b: level[owner[b]] for b in successors}


def layout(bundle):
    cfg, annotation = bundle['cfg'], bundle['annotation']
    assignments = ranks(cfg)
    grouped = defaultdict(list)
    for b in cfg['blocks']: grouped[assignments[b]].append(b)
    blocks, instructions, gaps = {}, {}, defaultdict(list)
    for g in [*annotation.get('processing_gaps', []), *annotation.get('_validation_gaps', [])]:
        gaps[g.get('instruction_id')].append(g)
    for b, block in cfg['blocks'].items():
        cursor = 82
        for ir in block['instructions']:
            identifier = ir['id']
            left = lines(ir, 62)
            semantic = annotation.get('ir_semantics', {}).get(identifier)
            right_value = semantic if semantic is not None else {
                'annotation_status': 'No executable annotation selected for this instruction',
                'saved_processing_gaps': gaps.get(identifier, []),
                'note': 'Absence is displayed explicitly, not reconstructed as empty semantics.'}
            right = lines(right_value, 104)
            height = 72 + max(len(left), len(right)) * LINE
            instructions[identifier] = {'block': b, 'offset': cursor, 'height': height,
                'left': left, 'right': right, 'modeled': semantic is not None}
            cursor += height + 20
        blocks[b] = {'height': cursor + 18}
    row_top, row_bottom = {}, {}
    y = 340
    for rank, ids in sorted(grouped.items()):
        row_top[rank] = y
        for col, b in enumerate(ids):
            blocks[b].update(x=LEFT + col*(BLOCK_W+COL_GAP), y=y, rank=rank, col=col)
        row_bottom[rank] = y + max(blocks[b]['height'] for b in ids)
        y = row_bottom[rank] + ROW_GAP
    cols = max(3, max(map(len, grouped.values()), default=1))
    grid_right = LEFT + cols*(BLOCK_W+COL_GAP)
    definitions = {}
    for b, block in cfg['blocks'].items():
        for ir in block['instructions']:
            for index, out in enumerate(ir.get('outputs', [])):
                if out.get('type') == 'result': definitions[out['identifier']] = (b, ir['id'], index)
    uses = []
    for b, block in cfg['blocks'].items():
        for ir in block['instructions']:
            for index, operand in enumerate(ir.get('inputs', [])):
                if operand.get('type') == 'result':
                    uses.append({'result': operand['identifier'], 'source': definitions.get(operand['identifier']),
                                 'target': (b, ir['id'], index)})
    width = int(grid_right + max(450, 130 + len(uses)*5))
    return blocks, instructions, row_top, row_bottom, uses, width, y, grid_right


def render(bundle, fixture_label=''):
    cfg, annotation, task = bundle['cfg'], bundle['annotation'], bundle['task']
    diagnostic=not bundle.get('selection_committed',True)
    blocks, instructions, row_top, row_bottom, uses, width, graph_end, grid_right = layout(bundle)
    globals_ = [('Complete Task', task), ('Complete CFG global fields', {k:v for k,v in cfg.items() if k != 'blocks'}),
                ('Accepted processing globals - NOT assembled annotation' if diagnostic else 'Complete annotation global fields',
                 {k:v for k,v in annotation.items() if k != 'ir_semantics'}),
                ('Complete block fields outside instructions', {b:{k:v for k,v in block.items() if k != 'instructions'}
                                                               for b,block in cfg['blocks'].items()}),
                ('Every control edge', {f'E{i+1:03}': e for i,e in enumerate(cfg.get('edges', []))}),
                ('Every result reference', {f'D{i+1:03}': {'result':u['result'], 'definition':u['source'], 'use':u['target']}
                                            for i,u in enumerate(uses)}),
                ('Selection and provenance', {'run':bundle['run'],'selection':bundle['selection'],'files':bundle['files'],
                    'saved_run_status':bundle['status'],'fixture_label':fixture_label,
                    'renderer': 'Native SVG, SCC-layered fallback; all selected text shown without truncation.'})]
    global_lines = [(label, lines(value, 170)) for label,value in globals_]
    appendix_height = sum(86 + len(content)*LINE for _,content in global_lines) + 160
    height = int(graph_end + appendix_height)
    c = Canvas(width, height)
    ET.SubElement(c.root, f'{{{NS}}}metadata', {'id':'complete-selected-input'}).text = json.dumps(bundle, ensure_ascii=False)
    c.rect(0, 0, width, height, '#F8FAFC', '#F8FAFC', 0)
    if diagnostic:
        c.root.find(f'{{{NS}}}title').text='Diagnostic original CFG and accepted fragments - assembly did not commit'
        c.root.find(f'{{{NS}}}desc').text='Terminal diagnostic display of the accepted original CFG and processing fragments. No assembled annotation or selection committed. Missing records remain explicit.'
    c.text(LEFT, 64, 'SkillFlow | '+('DIAGNOSTIC: assembly did not commit' if diagnostic else 'Complete selected annotated CFG'), 34, bold=True)
    c.text(LEFT, 103, f"{len(blocks)} blocks  /  {len(instructions)} instructions  /  {len(cfg.get('edges',[]))} control edges  /  {len(uses)} result uses", 24)
    c.text(LEFT, 137, ('Accepted original CFG and processing fragments only; no committed annotation, Task bindings or merged sensitivity.'
                     if diagnostic else 'Every instruction and complete wire annotation is visible. Zoom to read; text and paths remain editable.'), 20, MUTED)
    if fixture_label: c.text(LEFT, 172, fixture_label, 23, '#9A3412', True)
    c.text(LEFT, 210, 'Solid slate: control flow (E). Dashed teal: result definition/use (D). Purple: semantics. Amber: missing annotation/gap.', 20, MUTED)
    c.text(LEFT, 243, 'Task, locations, realizations, demands, sensitivity declarations, gaps and exact edge/reference indexes appear after the CFG.', 20, MUTED)
    c.text(LEFT, 276, 'Saved status: ' + str(bundle['status'].get('status','unknown')) + ' | ' + Path(bundle['run']).name, 18, MUTED)
    controls = c.group('control-edges', 'All CFG control edges')
    for i, edge in enumerate(cfg.get('edges', [])):
        a,b = blocks[edge['source_block_id']], blocks[edge['target_block_id']]
        start=(a['x']+BLOCK_W/2,a['y']+a['height']); end=(b['x']+BLOCK_W/2,b['y'])
        sy=row_bottom[a['rank']]+25+(i%12)*7; ty=row_top[b['rank']]-35-(i%8)*8
        if b['rank'] == a['rank']+1:
            middle=(row_bottom[a['rank']]+row_top[b['rank']])/2
            pts=[start,(start[0],middle),(end[0],middle),end]
        else:
            lane=35+i*4
            pts=[start,(start[0],sy),(lane,sy),(lane,ty),(end[0],ty),end]
        c.path(pts, CTRL, parent=controls,identity=f'E{i+1:03}',title=json.dumps(edge,ensure_ascii=False))
        c.text(start[0]+9,start[1]+22,f'E{i+1:03}',14,CTRL,parent=controls)
    data = c.group('data-edges', 'All result definition/use edges; each repeated input slot retained')
    for i,u in enumerate(uses):
        if u['source'] is None: continue
        sb,si,_=u['source']; tb,ti,_=u['target']
        a,b=blocks[sb],blocks[tb]; ia,ib=instructions[si],instructions[ti]
        start=(a['x']+BLOCK_W,a['y']+ia['offset']+30)
        end=(b['x']+BLOCK_W,b['y']+ib['offset']+53)
        sx=a['x']+BLOCK_W+25+(i%6)*8; tx=b['x']+BLOCK_W+25+((i+2)%6)*8
        sy=row_bottom[a['rank']]+27+(i%15)*8; ty=row_top[b['rank']]-25-(i%12)*9
        lane=grid_right+80+i*5
        pts=[start,(sx,start[1]),(sx,sy),(lane,sy),(lane,ty),(tx,ty),(tx,end[1]),end]
        c.path(pts,DATA,True,data,identity=f'D{i+1:03}',title=json.dumps(u,ensure_ascii=False))
        c.text(start[0]+8,start[1]-8,f'D{i+1:03}',13,DATA,parent=data)
    for b, block in cfg['blocks'].items():
        box=blocks[b]; x,y=box['x'],box['y']
        group=c.group('block-'+b, b+' | '+block.get('block_name',''))
        c.rect(x,y,BLOCK_W,box['height'],'#E8EEF4','#64748B',14,group)
        c.text(x+20,y+33,b+'  |  '+block.get('block_name',''),25,bold=True,parent=group)
        c.text(x+20,y+61,'ENTRY' if b==cfg['entry_block_id'] else 'Basic block',17,MUTED,parent=group)
        for ir in block['instructions']:
            entry=instructions[ir['id']]; top=y+entry['offset']; g=c.group('instruction-'+ir['id'],ir['id'])
            ET.SubElement(c.root,f'{{{NS}}}view',{'id':'view-'+ir['id'],
                'viewBox':f'{x-20} {top-20} {BLOCK_W+40} {entry["height"]+40}'})
            c.rect(x+12,top,BLOCK_W-24,entry['height'],'white','#CBD5E1',7,g)
            c.rect(x+CFG_W,top+44,BLOCK_W-CFG_W-12,entry['height']-44,
                   '#F3F0FF' if entry['modeled'] else '#FFF7E7','none',0,g)
            c.text(x+26,top+30,ir['id']+'  |  '+ir['opcode'],22,bold=True,parent=g)
            c.text(x+26,top+61,'INSTRUCTION — all fields',15,MUTED,True,parent=g)
            c.text(x+CFG_W+18,top+61,('ACCEPTED PROCESSING FRAGMENT' if diagnostic else 'WIRE SEMANTICS — complete')
                   if entry['modeled'] else 'NO EXECUTABLE ANNOTATION — saved gaps',15,
                   '#5B3B97' if entry['modeled'] else '#9A3412',True,parent=g)
            c.text_lines(x+26,top+86,entry['left'],g)
            c.text_lines(x+CFG_W+18,top+86,entry['right'],g)
    y=graph_end+50
    c.text(LEFT,y,'Complete supporting objects and relation indexes',32,bold=True); y+=50
    for i,(label,content) in enumerate(global_lines):
        panel_h=72+len(content)*LINE
        g=c.group(f'complete-object-{i}',label)
        c.rect(LEFT,y,min(width-LEFT-100,3000),panel_h,'white','#94A3B8',10,g)
        c.text(LEFT+22,y+34,label,25,bold=True,parent=g)
        c.text_lines(LEFT+22,y+67,content,g)
        ET.SubElement(c.root,f'{{{NS}}}view',{'id':'view-support-'+str(i),
            'viewBox':f'{LEFT-20} {y-20} {min(width-LEFT-100,3000)+40} {panel_h+40}'})
        y+=panel_h+24
    coverage={'block_count':len(blocks),'instruction_count':len(instructions),
        'control_edge_count':len(cfg.get('edges',[])),'result_use_count':len(uses),
        'undefined_result_uses':[u for u in uses if u['source'] is None],
        'modeled_ir_count':sum(entry['modeled'] for entry in instructions.values()),
        'unmodeled_ir_ids':[ir for ir,entry in instructions.items() if not entry['modeled']],
        'annotation_ir_not_in_cfg':sorted(set(annotation.get('ir_semantics',{}))-set(instructions)),
        'svg_dimensions':[width,height],'all_input_text_preserved_in_metadata':True,
        'truncation':False,'layout':'native SCC-layered SVG; no Graphviz dependency',
        'dot_available':shutil.which('dot') is not None,'fixture_label':fixture_label,'files':bundle['files']}
    coverage.update(view_kind=bundle.get('view_kind','selected'),selection_committed=not diagnostic)
    if coverage['undefined_result_uses'] or coverage['annotation_ir_not_in_cfg']:
        raise ValueError('Selected inputs are inconsistent; see result/reference identities')
    return c,coverage,blocks,instructions


def short(value, length=72):
    value=str(value).replace('\n',' ')
    return value if len(value)<=length else value[:length-3]+'...'


def compact_summary(semantic, global_ids):
    operations, modes, requirements, labels=[],set(),set(global_ids),set()
    def visit(value):
        if isinstance(value,dict):
            if isinstance(value.get('op'),str): operations.append(value['op'])
            if isinstance(value.get('mode'),str): modes.add(value['mode'])
            if value.get('requirement_id'): requirements.add(value['requirement_id'])
            for declaration in value.get('sensitivity',[]):
                if isinstance(declaration,dict) and declaration.get('label'): labels.add(declaration['label'])
            for item in value.values():visit(item)
        elif isinstance(value,list):
            for item in value:visit(item)
    visit(semantic or {})
    counts=Counter(operations)
    return (', '.join(f'{name} x{count}' for name,count in counts.items()) or 'no declared operations',
            ','.join(sorted(modes)) or 'no processing segment', ','.join(sorted(requirements)) or 'none',
            ','.join(sorted(labels)))


def render_overview(bundle, detail_name, fixture_label=''):
    """Bounded reading view; every node and relation stays, links open full text."""
    cfg,annotation=bundle['cfg'],bundle['annotation']
    levels=ranks(cfg); grouped=defaultdict(list)
    for b in cfg['blocks']:grouped[levels[b]].append(b)
    bw,gap,left,irh=760,110,200,150
    positions,irs,row_top,row_bottom={}, {}, {}, {}
    y=310
    for rank,names in sorted(grouped.items()):
        row_top[rank]=y
        for col,b in enumerate(names):
            block=cfg['blocks'][b]
            positions[b]={'x':left+col*(bw+gap),'y':y,'h':85+len(block['instructions'])*irh,
                          'rank':rank,'col':col}
            for i,ir in enumerate(block['instructions']):
                irs[ir['id']]={'block':b,'y':y+72+i*irh,'ir':ir}
        row_bottom[rank]=y+max(positions[b]['h'] for b in names)
        y=row_bottom[rank]+160
    definitions={}
    for b,block in cfg['blocks'].items():
        for ir in block['instructions']:
            for i,out in enumerate(ir.get('outputs',[])):
                if out.get('type')=='result':definitions[out['identifier']]=(ir['id'],i)
    uses=[]
    for b,block in cfg['blocks'].items():
        for ir in block['instructions']:
            for i,operand in enumerate(ir.get('inputs',[])):
                if operand.get('type')=='result':uses.append((operand['identifier'],definitions[operand['identifier']],ir['id'],i))
    grid_right=left+max(map(len,grouped.values()))*(bw+gap)
    width=int(grid_right+max(450,len(uses)*5+160)); height=int(y+160)
    c=Canvas(width,height)
    ET.SubElement(c.root,f'{{{NS}}}metadata').text=json.dumps({'kind':'complete_node_overview',
        'run':bundle['run'],'selection':bundle['selection'],'files':bundle['files'],
        'full_detail':detail_name,'bounded_text_only_in_overview':True},ensure_ascii=False)
    c.rect(0,0,width,height,'#F8FAFC','#F8FAFC',0)
    diagnostic=not bundle.get('selection_committed',True)
    c.root.find(f'{{{NS}}}title').text='Diagnostic uncommitted CFG overview' if diagnostic else 'Complete annotated CFG overview'
    if diagnostic:
        c.root.find(f'{{{NS}}}desc').text='Complete original CFG overview with accepted processing fragments only. Assembly did not commit. Links open the explicit diagnostic detail, not selected final annotations.'
    c.text(left,58,'SkillFlow | '+('DIAGNOSTIC - assembly did not commit' if diagnostic else 'Full graph overview'),34,bold=True)
    c.text(left,96,f'{len(positions)} blocks / {len(irs)} instructions / {len(cfg.get("edges",[]))} control edges / {len(uses)} result references',22)
    c.text(left,132,('Original accepted fragments only; missing annotations are marked. Click an instruction for full detail.'
                   if diagnostic else 'Every node is retained. Click an instruction to open its complete editable annotation.'),20,MUTED)
    if fixture_label:c.text(left,168,fixture_label,20,'#9A3412',True)
    link=ET.SubElement(c.root,f'{{{NS}}}a',{'href':quote(detail_name)+'#view-support-0','target':'_blank'})
    c.text(left,205,'Open complete Task / global annotations / exact edge and reference indexes',19,'#4F46A5',True,parent=link)
    c.text(left,245,'Solid slate E: control flow. Dashed teal D: result references. Amber cards: no executable annotation.',18,MUTED)
    controls=c.group('control-edges')
    for i,edge in enumerate(cfg.get('edges',[])):
        a,b=positions[edge['source_block_id']],positions[edge['target_block_id']]
        start=(a['x']+bw/2,a['y']+a['h']);end=(b['x']+bw/2,b['y'])
        if b['rank']==a['rank']+1:
            middle=(row_bottom[a['rank']]+row_top[b['rank']])/2
            points=[start,(start[0],middle),(end[0],middle),end]
        else:
            sy=row_bottom[a['rank']]+20+(i%11)*7;ty=row_top[b['rank']]-25-(i%10)*7;lane=30+i*3
            points=[start,(start[0],sy),(lane,sy),(lane,ty),(end[0],ty),end]
        c.path(points,CTRL,parent=controls,identity=f'E{i+1:03}',title=json.dumps(edge,ensure_ascii=False))
        c.text(start[0]+7,start[1]+20,f'E{i+1:03}',13,CTRL,parent=controls)
    data=c.group('data-edges')
    data.set('opacity','.5')
    for i,(value,(source,_),target,_) in enumerate(uses):
        a,b=positions[irs[source]['block']],positions[irs[target]['block']]
        sy=irs[source]['y']+30;ty=irs[target]['y']+55
        start=(a['x']+bw,sy);end=(b['x']+bw,ty)
        sx=a['x']+bw+20+(i%5)*10;tx=b['x']+bw+20+((i+2)%5)*10
        ay=row_bottom[a['rank']]+25+(i%12)*8;by=row_top[b['rank']]-22-(i%10)*9
        lane=grid_right+70+i*5
        c.path([start,(sx,sy),(sx,ay),(lane,ay),(lane,by),(tx,by),(tx,ty),end],DATA,True,data,
            identity=f'D{i+1:03}',title=f'{value}: {source} -> {target}, input[{uses[i][3]}]')
    task_ids=defaultdict(set)
    for demand in annotation.get('demands',[]):
        target=demand.get('target',{})
        if target.get('instruction_id'):task_ids[target['instruction_id']].add(demand.get('requirement_id','?'))
    gap_ids={g.get('instruction_id') for g in annotation.get('processing_gaps',[])}
    for b,block in cfg['blocks'].items():
        box=positions[b];x,y=box['x'],box['y'];g=c.group('block-'+b,b)
        c.rect(x,y,bw,box['h'],'#E8EEF4','#64748B',12,g)
        c.text(x+17,y+30,short(b+' | '+block.get('block_name',''),62),22,bold=True,parent=g)
        c.text(x+17,y+56,'ENTRY' if b==cfg['entry_block_id'] else 'Basic block',15,MUTED,parent=g)
        for ir in block['instructions']:
            top=irs[ir['id']]['y'];semantic=annotation.get('ir_semantics',{}).get(ir['id'])
            target=ET.SubElement(g,f'{{{NS}}}a',{'href':quote(detail_name)+'#view-'+ir['id'],'target':'_blank',
                'aria-label':'Open complete '+ir['id']+' instruction and annotation'})
            ET.SubElement(target,f'{{{NS}}}title').text=json.dumps(ir,ensure_ascii=False,indent=2)
            c.rect(x+10,top,bw-20,irh-12,'#F3F0FF' if semantic is not None else '#FFF7E7','#CBD5E1',6,target)
            c.text(x+22,top+27,short(ir['id']+' | '+ir['opcode'],58),19,bold=True,parent=target)
            def operands(values):
                return ', '.join(str(v.get('identifier')) if v.get('type')!='literal' else json.dumps(v.get('literal_value'),ensure_ascii=False) for v in values) or '(none)'
            c.text(x+22,top+51,short('IN: '+operands(ir.get('inputs',[])),76),15,mono=True,parent=target)
            c.text(x+22,top+73,short('OUT: '+operands(ir.get('outputs',[])),76),15,mono=True,parent=target)
            ops,modes,requirements,sensitivity=compact_summary(semantic,task_ids[ir['id']])
            if diagnostic:requirements='unassembled'
            c.text(x+22,top+95,short('Ops: '+ops,82) if semantic is not None else 'GAP: no executable annotation selected',15,
                MUTED if semantic is not None else '#9A3412',parent=target)
            c.text(x+22,top+117,short('Mode: '+modes+' | Task: '+requirements+
                (' | Sensitive: '+sensitivity if sensitivity else '')+(' | Scoped gap' if ir['id'] in gap_ids else ''),88),14,MUTED,parent=target)
    return c,{'blocks':len(positions),'instructions':len(irs),'control_edges':len(cfg.get('edges',[])),
              'result_references':len(uses),'dimensions':[width,height],'full_detail':detail_name}


def preview(c, path, crop=None):
    from PIL import Image, ImageDraw, ImageFont
    if crop:
        x0,y0,x1,y1=crop; scale=1
    else:
        x0,y0,x1,y1=0,0,c.width,c.height
        scale=min(1800/c.width,5500/c.height,1)
    image=Image.new('RGB',(max(1,int((x1-x0)*scale)),max(1,int((y1-y0)*scale))),'#F8FAFC')
    d=ImageDraw.Draw(image)
    fonts={}
    def xy(x,y):return ((x-x0)*scale,(y-y0)*scale)
    for item in c.preview:
        if item[0]=='rect':
            _,x,y,w,h,fill,stroke=item
            if y+h<y0 or y>y1 or x+w<x0 or x>x1:continue
            d.rectangle([xy(x,y),xy(x+w,y+h)],fill=fill,outline=None if stroke=='none' else stroke)
        elif item[0]=='path':
            _,points,color=item
            d.line([xy(x,y) for x,y in points],fill=color,width=max(1,int(2*scale)))
        else:
            _,x,y,text,size,color,bold,mono=item
            if y<y0 or y>y1 or x>x1:continue
            key=(max(1,int(size*scale)),bold,mono)
            if key not in fonts:
                filename=('consolab.ttf' if bold else 'consola.ttf') if mono else ('segoeuib.ttf' if bold else 'segoeui.ttf')
                try:fonts[key]=ImageFont.truetype('C:/Windows/Fonts/'+filename,key[0])
                except OSError:fonts[key]=ImageFont.load_default()
            d.text(xy(x,y),text,fill=color,font=fonts[key],anchor='ls')
    image.save(path)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True,help='SVG output, beneath this verification directory')
    p.add_argument('--fixture-label',default='')
    p.add_argument('--diagnostic-uncommitted',action='store_true',
        help='Explicit terminal-only fallback: no selection; verify original Task/CFG and accepted processing records, never revisions')
    p.add_argument('--qa',action='store_true',help='Write coverage JSON, small overview and readable first-block crop')
    args=p.parse_args()
    target=args.out.resolve()
    if not target.is_relative_to(HERE) or target.is_relative_to(args.run.resolve()):
        p.error('Output must stay under the renderer verification directory and outside every run.')
    bundle=load_diagnostic_bundle(args.run) if args.diagnostic_uncommitted else load_bundle(args.run)
    c,coverage,blocks,instructions=render(bundle,args.fixture_label)
    target.parent.mkdir(parents=True,exist_ok=True)
    ET.ElementTree(c.root).write(target,encoding='utf-8',xml_declaration=True)
    parsed=ET.parse(target).getroot()
    ids=[g.get('id') for g in parsed.findall(f'{{{NS}}}g')]
    assert sum(i.startswith('block-') for i in ids)==coverage['block_count']
    assert sum(i.startswith('instruction-') for i in ids)==coverage['instruction_count']
    metadata=json.loads(parsed.find(f'{{{NS}}}metadata').text)
    assert metadata==bundle
    target.with_suffix('.coverage.json').write_text(json.dumps(coverage,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    overview,overview_coverage=render_overview(bundle,target.name,args.fixture_label)
    overview_path=target.with_name(target.stem+'-overview.svg')
    ET.ElementTree(overview.root).write(overview_path,encoding='utf-8',xml_declaration=True)
    overview_path.with_suffix('.coverage.json').write_text(json.dumps(overview_coverage,indent=2)+'\n',encoding='utf-8')
    assert overview_coverage['instructions']==coverage['instruction_count']
    assert overview_coverage['control_edges']==coverage['control_edge_count']
    assert overview_coverage['result_references']==coverage['result_use_count']
    if args.qa:
        preview(c,target.with_name(target.stem+'-overview.png'))
        first=blocks[bundle['cfg']['entry_block_id']]
        preview(c,target.with_name(target.stem+'-detail.png'),(first['x']-25,first['y']-15,
            first['x']+BLOCK_W+110,min(first['y']+1300,c.height)))
        preview(overview,target.with_name(target.stem+'-overview-preview.png'))
        preview(overview,target.with_name(target.stem+'-overview-detail.png'),(160,285,min(2060,overview.width),1600))
    print(json.dumps({'svg':str(target),'bytes':target.stat().st_size,**coverage},ensure_ascii=False))


if __name__=='__main__':
    main()
