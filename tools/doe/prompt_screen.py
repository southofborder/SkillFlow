"""Eight first-response requests across annotation and review, without correction.

This deliberately bounded experiment is not a production response chain. The
production unlimited structural-correction policy is unchanged. Every complete
response is retained and classified after exactly one logical request per arm.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
import re
import subprocess
import sys
from threading import Event

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.json_normalization import normalize_response, NORMALIZATION_VERSION
from skillflow.common.llm.config import LlmConfig
from skillflow.common.recording import (
    RecordingClient, SavedResponseClient, SavedCallFailure, ResponseIntegrityError,
    canonical_sha256, implementation_provenance, injected_factory, now, sha_file,
    streaming_factory, validated_trace, verify_request_identity,
)
from skillflow.common.runs import exclusive_run
from skillflow.common.semantic_failure import SemanticFailure
from skillflow.common.source_evidence import _json_object
from skillflow.common.validation import StructuralValidationError, diagnostic_materials
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.annotation.config import annotation_config, PUBLIC_CONFIG_FIELDS
from skillflow.propagation.annotation.prompts import build_prompt as annotation_prompt
from skillflow.propagation.review.material import prepare_review_material
from skillflow.propagation.review.prompts import build_prompt as review_prompt
from skillflow.propagation.review.services import validate_response as validate_review
from tools.doe.prompt_screen_fixtures import screen_fixtures, review_reference
from tools.doe.summarize_pipeline_run import sum_usage

IDENTITY = "skillflow-first-response-screen-v1"
ARMS = ("baseline", "revised")
CLAIM = "A first-response engineering screen, not proof of semantic correctness or generalized cost improvement."


def _read(path): return _json_object(Path(path).read_text(encoding="utf-8"))
def _seal(value): return {**value, "manifest_sha256": canonical_sha256(value)}


def _unseal(value):
    raw=deepcopy(value); expected=raw.pop("manifest_sha256", None)
    if canonical_sha256(raw)!=expected: raise ResponseIntegrityError("Screen artifact seal differs")
    return raw


def _safe(path):
    path=Path(path)
    for parent in (path,*path.parents):
        if parent.exists() or parent.is_symlink():
            if parent.is_symlink() or getattr(parent.lstat(),"st_file_attributes",0)&0x400:
                raise ValueError("Screen paths cannot contain links or reparse points")
    return path.resolve()


def _implementation():
    names=("prompt_screen.py","prompt_screen_fixtures.py","compare_prompts.py","summarize_pipeline_run.py")
    return {"production":implementation_provenance(),"tools":{name:sha_file(Path(__file__).with_name(name)) for name in names}}


def _exact(writer,path,value,*,replay=False):
    if path.exists():
        if canonical_sha256(_read(path))!=canonical_sha256(value):
            raise ResponseIntegrityError("Saved screen artifact differs: "+str(path))
    elif replay: raise ResponseIntegrityError("Missing saved screen artifact: "+str(path))
    else: writer.json(path,value)


def _render_snapshot(snapshot,items):
    """Use only an audited frozen package in an isolated offline subprocess."""
    code=r'''
import json,pathlib,socket,sys
sys.stdout.reconfigure(encoding="utf-8");sys.stdin.reconfigure(encoding="utf-8")
root=pathlib.Path(sys.argv[1]).resolve();sys.path.insert(0,str(root/"src"))
def no_network(*args,**kwargs): raise RuntimeError("Frozen prompt rendering cannot access the network")
socket.socket.connect=no_network;socket.socket.connect_ex=no_network;socket.create_connection=no_network
from skillflow.propagation.annotation.prompts import build_prompt as annotation_prompt
from skillflow.propagation.review.prompts import build_prompt as review_prompt
data=json.load(sys.stdin);prompts={x["name"]:(annotation_prompt if x["stage"]=="annotation" else review_prompt)(x["material"]) for x in data}
imports={}
for name,module in list(sys.modules.items()):
 if name=="skillflow" or name.startswith("skillflow."):
  p=getattr(module,"__file__",None)
  if p:
   p=pathlib.Path(p).resolve()
   if not p.is_relative_to(root/"src"): raise RuntimeError("Frozen renderer imported live production source: "+name)
   imports[name]=p.relative_to(root).as_posix()
print(json.dumps({"prompts":prompts,"imports":imports},ensure_ascii=False))
'''
    completed=subprocess.run([sys.executable,"-I","-B","-c",code,str(snapshot)],
        input=json.dumps(items,ensure_ascii=False),text=True,encoding="utf-8",capture_output=True,cwd=snapshot,check=False)
    if completed.returncode:
        raise ValueError("Frozen offline prompt rendering failed: "+completed.stderr[-4000:])
    return _json_object(completed.stdout)


def _sizes(prompt):
    blocks=dict(re.findall(r"<!-- SKILLFLOW_PROMPT:([A-Z_]+):BEGIN -->\n(.*?)\n<!-- SKILLFLOW_PROMPT:\1:END -->",prompt,re.S))
    if not {"INPUT","FORMAT","EXAMPLES"}<=set(blocks): raise ValueError("Missing auditable prompt section markers")
    def size(s): return {"characters":len(s),"utf8_bytes":len(s.encode("utf-8"))}
    return {"total":size(prompt),"input":size(blocks["INPUT"]),"format":size(blocks["FORMAT"]),
            "examples":size(blocks["EXAMPLES"]),"instructions":size("\n".join(v for k,v in blocks.items() if k not in {"INPUT","FORMAT","EXAMPLES"})),
            "static":size(prompt.replace(blocks["INPUT"],"",1))}


def prepare_screen(run_dir,*,baseline_dir,config):
    directory,baseline=_safe(run_dir),_safe(baseline_dir)
    if directory.exists() and any(directory.iterdir()): raise ValueError("Prepare requires a new empty screen directory")
    if set(config)-set(PUBLIC_CONFIG_FIELDS): raise ValueError("Screen configuration must be public")
    config=annotation_config(config); LlmConfig(api_key="identity-check-only", **config); writer=ArtifactWriter(())
    source_files=_read(baseline/"files.json")
    frozen={name:digest for name,digest in source_files.items() if name.startswith("src/")}
    if not frozen or not all((baseline/name).is_file() and sha_file(baseline/name)==digest for name,digest in frozen.items()):
        raise ValueError("Frozen baseline source snapshot does not match its original receipt")
    cases=screen_fixtures(); inputs=[]
    with exclusive_run(directory):
        snapshot=directory/"audit/baseline-source"
        for name,digest in frozen.items():
            path=_safe(snapshot/name)
            if not path.is_relative_to(snapshot): raise ValueError("Baseline path escaped its snapshot")
            writer.text(path,(baseline/name).read_bytes().decode("utf-8"))
            if sha_file(path)!=digest: raise ValueError("Baseline source bytes changed during freezing")
        writer.json(directory/"audit/baseline-receipt.json",{"files":frozen,"files_sha256":canonical_sha256(frozen),"original_receipt_sha256":sha_file(baseline/"files.json")})
        for case in cases:
            compile_response(case["reference"],case["material"])
            material=(prepare_review_material(case["material"],case["reference"]) if case["stage"]=="review" else case["material"])
            if case["stage"]=="review":
                answer=review_reference(material,adverse=case["name"]=="review_b_dispatch")
                validate_review(answer,material); case["reference_response"]=answer
            else: case["reference_response"]=case["reference"]
            writer.json(directory/f"cases/{case['name']}/material.json",material)
            writer.json(directory/f"audit/fixtures/{case['name']}.json",case)
            inputs.append({"name":case["name"],"stage":case["stage"],"material":material})
        rendered=_render_snapshot(snapshot,inputs)
        writer.json(directory/"audit/baseline-render.json",{"imports":rendered["imports"],"snapshot_sha256":canonical_sha256(frozen),"network_disabled":True})
        for item in inputs:
            prompts={"baseline":rendered["prompts"][item["name"]],"revised":(annotation_prompt if item["stage"]=="annotation" else review_prompt)(item["material"])}
            blocks=[]
            for arm,prompt in prompts.items():
                if re.search(r"[\u4e00-\u9fff]",prompt): raise ValueError("First-response screen inputs and instructions must be English")
                blocks.append(re.search(r"<!-- SKILLFLOW_PROMPT:INPUT:BEGIN -->\n(.*?)\n<!-- SKILLFLOW_PROMPT:INPUT:END -->",prompt,re.S).group(1))
                writer.text(directory/f"cases/{item['name']}/{arm}/prompt.txt",prompt)
                writer.json(directory/f"cases/{item['name']}/{arm}/prompt-sizes.json",_sizes(prompt))
            if blocks[0]!=blocks[1]: raise ValueError("Paired prompt arms must receive exactly the same model input")
        # Counterbalance arm order and interleave annotation and review stages.
        order=[cases[0],cases[2],cases[1],cases[3]]
        schedule=[{"case":case["name"],"stage":case["stage"],"arm":arm} for index,case in enumerate(order)
                  for arm in (ARMS if index%2==0 else tuple(reversed(ARMS)))]
        preregistration={"initial_requests":8,"structural_corrections":0,"task_calls":0,"extra_review_calls":0,"semantic_repairs":0,"quality_reruns":0,
            "mechanical_gate":"All four revised first responses must be valid under the shared strict validator; normalization is reported separately.",
            "semantic_gate":"External review must pass the frozen per-case relationship checks and both review controls; structure alone cannot pass this gate.",
            "cost_gate":"Compare all observed HTTP input and output tokens, including failed responses; a shorter prompt alone is not measured benefit.",
            "next_stage":"No automatic correction experiment or formal-case rerun. Stop and report if there is no measurable benefit.",
            "expert_gold_standard":False,"semantic_checks":{case["name"]:case["semantic_checks"] for case in cases}}
        writer.json(directory/"audit/preregistration.json",preregistration)
        files={p.relative_to(directory).as_posix():sha_file(p) for p in sorted(directory.rglob('*')) if p.is_file() and p.name!='.runner.lock'}
        manifest={"identity":IDENTITY,"created_at":now(),"config":config,"implementation":_implementation(),"normalization":NORMALIZATION_VERSION,
                  "cases":[{"name":x["name"],"stage":x["stage"]} for x in cases],"schedule":schedule,"files":files,"claim":CLAIM}
        writer.json(directory/"manifest.json",_seal(manifest))
    return manifest


def load_screen(run_dir,*,check_implementation=False):
    directory=_safe(run_dir); manifest=_unseal(_read(directory/"manifest.json"))
    if manifest.get("identity")!=IDENTITY: raise ValueError("Unsupported first-response screen identity")
    expected={(c["name"],arm) for c in manifest['cases'] for arm in ARMS}
    if len(manifest['schedule'])!=8 or {(x['case'],x['arm']) for x in manifest['schedule']}!=expected:
        raise ResponseIntegrityError("Screen does not declare exactly one request per case and arm")
    for relative,digest in manifest['files'].items():
        path=_safe(directory/relative)
        if not path.is_relative_to(directory) or not path.is_file() or sha_file(path)!=digest:
            raise ResponseIntegrityError("Frozen screen material changed: "+relative)
    if check_implementation and manifest['implementation']!=_implementation():
        raise ResponseIntegrityError("Screen implementation changed; no silent resume or replay")
    return manifest


def _call_metrics(call_dir):
    if not (call_dir/'call.json').exists(): return {"logical_calls":0,"http_attempts":0,"http_attempts_observed":False,"usage":sum_usage([]),"returned_models":[],"call_seconds":None}
    call=_read(call_dir/'call.json'); trace=validated_trace(call_dir/'transport.json'); attempts=[a for g in trace for a in g.get('http_attempts',[])]
    return {"logical_calls":1,"http_attempts":len(attempts),"http_attempts_observed":bool(trace) and all(g.get('http_attempts_observed') is True for g in trace),
            "http_retries":sum(max(0,len(g.get('http_attempts',[]))-1) for g in trace),"usage":sum_usage(attempts),
            "returned_models":sorted({g['returned_model'] for g in [*trace,*attempts] if g.get('returned_model')}),
            "call_seconds":((datetime.fromisoformat(call['finished_at'])-datetime.fromisoformat(call['started_at'])).total_seconds() if call.get('finished_at') else None)}


def _one(directory,manifest,item,*,writer,factory,stopping,replay=False):
    stage=directory/'cases'/item['case']/item['arm']; call_dir=stage/'calls'/item['stage']/'a001'
    material=_read(directory/'cases'/item['case']/'material.json'); prompt=(stage/'prompt.txt').read_bytes().decode('utf-8')
    if item['arm']=='revised' and prompt!=(annotation_prompt if item['stage']=='annotation' else review_prompt)(material):
        raise ResponseIntegrityError("Revised prepared prompt differs from its current builder")
    request={"identity":IDENTITY,"index":1,"kind":"first_response_"+item['stage'],"arm":item['arm'],"prompt_sha256":canonical_sha256(prompt),
             "material_sha256":canonical_sha256(material),"config_sha256":canonical_sha256(manifest['config'])}
    _exact(writer,call_dir/'request.json',request,replay=replay)
    previous=_unseal(_read(stage/'result.json')) if (stage/'result.json').exists() else None
    if replay and previous is None: raise ResponseIntegrityError("Replay needs a recorded terminal or interrupted decision")
    if previous:
        for name,digest in previous['call_files'].items():
            if not (stage/name).is_file() or sha_file(stage/name)!=digest: raise ResponseIntegrityError("Saved screen call artifact changed: "+name)
    response=None; validation=None; normalization=None; output=None
    try:
        exists=(call_dir/'call.json').exists()
        if not exists:
            if replay and previous['status']=='interrupted' and previous['metrics']['logical_calls']==0:
                raise KeyboardInterrupt("No request was started before the recorded interruption")
            if replay: raise ResponseIntegrityError("Replay has no saved call")
            if stopping.is_set(): raise KeyboardInterrupt("Interrupted before starting a request")
            if factory is None: raise ValueError("A live client factory is required only for a new request")
            client=RecordingClient(call_dir,factory,writer)
        else: client=SavedResponseClient(call_dir,writer)
        response=client.complete(prompt)
        saved=SavedResponseClient(call_dir,writer).complete(prompt)
        if canonical_sha256(saved)!=canonical_sha256(response): raise ResponseIntegrityError("Actual response differs from saved response")
        identity=verify_request_identity(call_dir,manifest['config'],prompt=prompt)
        _exact(writer,call_dir/'request-validation.json',identity,replay=replay)
        if (stopping.is_set() and not replay) or (replay and previous['status']=='interrupted'):
            raise KeyboardInterrupt("Interrupted after the recorded response; no later request started")
        candidate,normalization=normalize_response(response)
        if normalization is not None: _exact(writer,call_dir/'normalization.json',normalization,replay=replay)
        elif (call_dir/'normalization.json').exists(): raise ResponseIntegrityError("Unexpected normalization receipt")
        try:
            output=(compile_response(candidate,material) if item['stage']=='annotation' else validate_review(candidate,material).model_dump(mode='json'))
            validation={"status":"valid","diagnostics":[]}
        except StructuralValidationError as error:
            validation={"status":"structural_invalid",**diagnostic_materials(error.diagnostics)}
        except SemanticFailure as error: validation={"status":"semantic_failure","failure":error.failure,"diagnostics":[]}
        validation.update(response_sha256=canonical_sha256(response),candidate_sha256=canonical_sha256(candidate),normalization_sha256=canonical_sha256(normalization) if normalization else None)
        _exact(writer,call_dir/'validation.json',validation,replay=replay)
        if output is not None:
            if item['stage']=='annotation':
                for name,value in zip(('raw-annotation.json','compiled-annotation.json','mapping.json'),output): _exact(writer,stage/name,value,replay=replay)
            else: _exact(writer,stage/'review.json',output,replay=replay)
        status=validation['status']; error=None
    except ResponseIntegrityError: raise
    except KeyboardInterrupt:
        status='interrupted'; error={'type':'KeyboardInterrupt','message':'Stopped without starting a later request.'}
    except Exception as caught:
        # No broad exception authorizes another model call. An exception before
        # durable transport belongs to the implementation and is raised.
        if not (call_dir/'call.json').exists(): raise
        call=_read(call_dir/'call.json')
        if call.get('status')=='complete': raise
        if (call_dir/'transport.json').exists(): verify_request_identity(call_dir,manifest['config'],prompt=prompt)
        kind=caught.error_type if isinstance(caught,SavedCallFailure) else type(caught).__name__
        status='interrupted' if kind=='KeyboardInterrupt' else 'execution_error'
        error=({'type':'KeyboardInterrupt','message':'Stopped without starting a later request.'} if kind=='KeyboardInterrupt'
               else {'type':kind,'message':call.get('error',writer.clean(str(caught)))})
    result={**item,'status':status,'error':error,'validation':validation,'normalization':normalization,
            'metrics':_call_metrics(call_dir),'semantic_acceptance':'not_assessed',
            'output_sha256':canonical_sha256(output) if output is not None else None,
            'call_files':{p.relative_to(stage).as_posix():sha_file(p) for p in sorted((stage/'calls').rglob('*')) if p.is_file()}}
    if previous and (replay or previous['status']!='interrupted') and result!=previous:
        raise ResponseIntegrityError("Screen decision differs from its recorded first response")
    if not replay: writer.json(stage/'result.json',_seal(result))
    return result


def _report(directory,summary,writer):
    lines=['# First-response prompt screen','',CLAIM,'',
        'Four held-out materials each receive one baseline and one revised response. There is no structural correction, Task extraction, semantic repair, or automatic formal-case rerun.',
        '', '| Case | Stage | Arm | Response status | Error / diagnostic families | Normalized | Observed total tokens |', '|---|---|---|---|---|---|---:|']
    for row in summary['results']:
        usage=row['metrics']['usage']['total_tokens']; tokens=str(usage['total']) if usage['total'] is not None else 'Unknown'
        detail=(row['error']['type'] if row['error'] else ', '.join(sorted({d['code'] for d in (row['validation'] or {}).get('diagnostics',[])}))) or 'None'
        lines.append(f"| {row['case']} | {row['stage']} | {row['arm']} | {row['status']} | {detail} | {bool(row['normalization'])} | {tokens} |")
    lines+=['','Semantic acceptance is pending external review against the preregistered relationships. Reference candidates are assistant-authored, not independent expert gold labels.',
        'Reasoning and cache values are token breakdowns, not additional totals. Missing HTTP usage remains unknown. Invalid responses remain in the comparison.',
        '', '[Preregistered checks](audit/preregistration.json)'+(' · [Frozen online metrics](metrics.json)' if (directory/'metrics.json').exists() else ''), '']
    for row in summary['results']:
        base=f"cases/{row['case']}/{row['arm']}"; actual=f"{base}/calls/{row['stage']}/a001/call.json"
        lines.append(f"- {row['case']} / {row['arm']}: [prompt]({base}/prompt.txt), [decision]({base}/result.json)"+(", [actual request]("+actual+")" if (directory/actual).exists() else '; no request was started'))
    text='\n'.join(lines)+'\n'; writer.text(directory/'report.md',text)
    import markdown_it
    body=markdown_it.MarkdownIt('commonmark').enable('table').render(text)
    html="<!doctype html><html lang='en'><meta charset='utf-8'><title>First-response screen</title><style>body{max-width:1150px;margin:2rem auto;font:16px/1.6 system-ui}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:.4rem}</style>"+body+'</html>'
    writer.text(directory/'index.html',html); writer.text(directory/'report.html',html)


def _freeze_metrics(directory,summary,writer):
    path=directory/'metrics.json'
    if path.exists():
        metrics=_unseal(_read(path))
        if metrics['summary_sha256']!=canonical_sha256(summary): raise ResponseIntegrityError("Frozen online summary changed")
        for rel,digest in metrics['call_files'].items():
            if not (directory/rel).exists() or sha_file(directory/rel)!=digest: raise ResponseIntegrityError("Frozen online call files changed")
        return metrics
    arm_metrics={}
    for arm in ARMS:
        rows=[r for r in summary['results'] if r['arm']==arm]; traces=[]
        for row in rows: traces+=validated_trace(directory/'cases'/row['case']/arm/'calls'/row['stage']/'a001/transport.json')
        attempts=[a for g in traces for a in g.get('http_attempts',[])]
        arm_metrics[arm]={'requests':sum(r['metrics']['logical_calls'] for r in rows),'valid':sum(r['status']=='valid' for r in rows),
            'valid_without_normalization':sum(r['status']=='valid' and not r['normalization'] for r in rows),
            'http_attempts_observed':bool(traces) and all(g.get('http_attempts_observed') is True for g in traces),
            'http_attempts':len(attempts),'http_retries':sum(max(0,len(g.get('http_attempts',[]))-1) for g in traces),'usage':sum_usage(attempts),
            'returned_models':sorted({g['returned_model'] for g in [*traces,*attempts] if g.get('returned_model')}),
            'call_seconds':sum(r['metrics']['call_seconds'] or 0 for r in rows)}
    start=_read(directory/'online-state.json')['started_at']; end=now()
    metrics={'identity':IDENTITY,'summary_sha256':canonical_sha256(summary),'frozen_at':end,'online_timing':{'started_at':start,'ended_at':end,
        'seconds':(datetime.fromisoformat(end)-datetime.fromisoformat(start)).total_seconds(),'basis':'Initial screen execution to completed request decisions; excludes prepare and replay, includes any interruption/resume interval.'},
        'arms':arm_metrics,'structural_corrections':0,'task_calls':0,'semantic_repairs':0,
        'call_files':{p.relative_to(directory).as_posix():sha_file(p) for p in sorted((directory/'cases').rglob('*')) if p.is_file() and 'calls' in p.relative_to(directory/'cases').parts},
        'gate':{'structural':all(r['status']=='valid' for r in summary['results'] if r['arm']=='revised') and len(summary['results'])==8,
                'semantic':'pending_external_review','formal_rerun':'not_scheduled'}}
    writer.json(path,_seal(metrics)); return metrics


def run_screen(run_dir,*,env_file=None,clients=None,client_factory=None,stop_event=None,replay=False,progress=None):
    directory=_safe(run_dir); manifest=load_screen(directory,check_implementation=True); stopping=stop_event or Event(); writer=ArtifactWriter(())
    if replay and (clients is not None or client_factory is not None): raise ValueError("Replay cannot use a live client")
    if clients is not None and client_factory is not None: raise ValueError("Choose injected clients or a factory")
    # A completed/resumable screen can be inspected without credentials. Create
    # a live transport only at the first actually missing call.
    factory=client_factory
    with exclusive_run(directory):
        if not replay and not (directory/'online-state.json').exists(): writer.json(directory/'online-state.json',{'started_at':now()})
        prior=_read(directory/'summary.json') if (directory/'summary.json').exists() else None
        summary={'identity':IDENTITY,'status':'complete','results':[],'claim':CLAIM}
        for item in manifest['schedule']:
            stage=directory/'cases'/item['case']/item['arm']; recorded=(stage/'calls'/item['stage']/'a001/call.json').exists()
            if replay and not (stage/'result.json').exists(): continue
            if not replay and stopping.is_set(): summary['status']='interrupted'; break
            use_factory=factory
            if not replay and not recorded:
                if clients is not None: use_factory=injected_factory(clients[(item['case'],item['arm'])])
                elif factory is None:
                    factory,secrets=streaming_factory(manifest['config'],env_file=env_file); writer=ArtifactWriter(secrets); use_factory=factory
            if writer.clean(manifest)!=manifest: raise ValueError("Credential overlaps frozen screen material")
            if progress: progress(('Read saved response: ' if recorded else 'Start first response: ')+item['case']+'/'+item['arm'])
            row=_one(directory,manifest,item,writer=writer,factory=use_factory,stopping=stopping,replay=replay)
            summary['results'].append(row)
            if row['status']=='interrupted': summary['status']='interrupted'; stopping.set()
            if not replay: writer.json(directory/'summary.json',summary)
            if stopping.is_set(): break
        if len(summary['results'])<8 and summary['status']=='complete': summary['status']='partial'
        if replay:
            # A stop before the first request has no per-arm result to replay.
            # Preserve that recorded stop only; an ordinary partial screen is
            # not changed into an interruption and no request is authorized.
            if (prior is not None and prior.get('status')=='interrupted'
                    and not prior.get('results') and not summary['results']):
                summary['status']='interrupted'
            if prior is None or summary!=prior: raise ResponseIntegrityError("First-response replay differs from saved decisions")
            if (directory/'metrics.json').exists(): _freeze_metrics(directory,summary,writer)
            receipt={'identity':IDENTITY,'status':'matched','api_calls':0,'summary_sha256':canonical_sha256(summary)}
            writer.json(directory/'replay.json',receipt); return receipt
        writer.json(directory/'summary.json',summary)
        if summary['status']=='complete': _freeze_metrics(directory,summary,writer)
        _report(directory,summary,writer)
    return summary


def replay_screen(run_dir): return run_screen(run_dir,replay=True)
