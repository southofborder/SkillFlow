"""Lossless exact-value dictionary experiments on the frozen prompt only."""
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
from measure_review_size import BASE, RUN, compact, sha, write


def shared(value, minimum=25, marker="$ref"):
    counts, raw = Counter(), {}
    def visit(v):
        if isinstance(v, (dict, list, str)):
            key = compact(v)
            counts[key] += 1
            raw[key] = v
        if isinstance(v, dict):
            if set(v) == {marker}: raise ValueError("Reference-marker collision in original payload")
            for child in v.values():visit(child)
        elif isinstance(v,list):
            for child in v:visit(child)
    visit(value)
    candidates = [key for key,count in counts.items() if count > 1 and len(key) >= minimum]
    ids = {key:"V"+str(i) for i,key in enumerate(sorted(candidates,key=lambda s:(len(s),s)))}
    selected = set(ids)
    def encode(v, defining=None):
        key = compact(v) if isinstance(v,(dict,list,str)) else None
        if key in selected and key != defining:return {marker:ids[key]}
        if isinstance(v,dict):return {k:encode(z) for k,z in v.items()}
        if isinstance(v,list):return [encode(z) for z in v]
        return v
    while True:
        definitions={ids[key]:encode(raw[key],defining=key) for key in ids if key in selected}
        root=encode(value)
        used=Counter()
        def refs(v):
            if isinstance(v,dict):
                if set(v)=={marker}:used[v[marker]]+=1
                else:
                    for z in v.values():refs(z)
            elif isinstance(v,list):
                for z in v:refs(z)
        refs(root)
        for item in definitions.values():refs(item)
        remove=[]
        for key in selected:
            name=ids[key]; n=used[name]; size=len(compact(definitions[name])); refsize=len(compact({marker:name}))
            if n<2 or (n-1)*size-n*refsize-len(compact(name))-2<=0:remove.append(key)
        if not remove:break
        selected.difference_update(remove)
    encoded={"shared_values":definitions,"value":root}
    def decode(v):
        if isinstance(v,dict):
            if set(v)=={marker}:return decode(definitions[v[marker]])
            return {k:decode(z) for k,z in v.items()}
        if isinstance(v,list):return [decode(z) for z in v]
        return v
    assert decode(root)==value
    return encoded, {"definitions":len(definitions),"references":sum(used.values()),
        "definition_chars":len(compact(definitions)),"root_chars":len(compact(root)),
        "encoded_chars":len(compact(encoded)),"decoded_equal":True}


def main():
    prompt=(RUN/'review/prompt.txt').read_text(encoding='utf-8')
    raw=prompt.split('\nINPUT_JSON\n',1)[1].split('\nCOMPLETE SOURCE\n',1)[0]
    payload=json.loads(raw)
    summaries=[]
    for minimum in [20,25,40,60,100]:
        encoded,metrics=shared(payload,minimum)
        summary={"minimum_candidate_chars":minimum,**metrics,"full_delivery_chars_before_instructions":1079505-len(raw)+metrics['encoded_chars'],
            "saved_chars":len(raw)-metrics['encoded_chars']}
        summary['headroom_before_instructions']=1048576-summary['full_delivery_chars_before_instructions']
        summaries.append(summary)
        if minimum==25:write('shared-values-payload.json',encoded)
    write('shared-values-measurement.json',{'results':summaries,'source_unchanged':True,'historical_run':str(RUN)})
    print(json.dumps(summaries,indent=2))


if __name__=='__main__':main()
