"""Generic readable record tables, isolated from production rendering."""
from copy import deepcopy
import json
from measure_review_size import RUN, BASE, compact, write, global_scope_inventory, expand_global_scope_inventory
from measure_shared_values import shared


def record_tables(value, maps=False):
    counts={"array_tables":0,"map_tables":0}
    def pack(rows, names=None):
        shapes=[]; indexes={}; encoded=[]
        for index,row in enumerate(rows):
            shape=tuple(row)
            if shape not in indexes:indexes[shape]=len(shapes);shapes.append(list(shape))
            encoded.append(([names[index]] if names is not None else [])+[indexes[shape],*row.values()])
        if len(shapes)==1:
            encoded=[([row[0]]+row[2:] if names is not None else row[1:]) for row in encoded]
            table={"columns":shapes[0],"rows":encoded}
        else:table={"column_sets":shapes,"rows":encoded}
        return {"$map_records" if names is not None else "$records":table}
    def encode(v):
        if isinstance(v,dict):
            if set(v)&{"$records","$map_records"}:raise ValueError("Record-marker collision in original")
            result={k:encode(z) for k,z in v.items()}
            if maps and len(result)>2 and all(isinstance(z,dict) for z in result.values()):
                packed=pack(list(result.values()),list(result))
                if len(compact(packed))<len(compact(result)):
                    counts['map_tables']+=1;return packed
            return result
        if isinstance(v,list):
            result=[encode(z) for z in v]
            if len(result)>1 and all(isinstance(z,dict) for z in result):
                packed=pack(result)
                if len(compact(packed))<len(compact(result)):
                    counts['array_tables']+=1;return packed
            return result
        return v
    def unpack(v):
        if isinstance(v,dict):
            names = "$map_records" in v and len(v)==1
            if names or set(v)=={"$records"}:
                table=v['$map_records' if names else '$records'];result=[]
                for row in table['rows']:
                    name,fields=(row[0],row[1:]) if names else (None,row)
                    columns=table.get('columns')
                    if columns is None:columns,fields=table['column_sets'][fields[0]],fields[1:]
                    item={k:unpack(z) for k,z in zip(columns,fields)}
                    result.append((name,item) if names else item)
                return dict(result) if names else result
            return {k:unpack(z) for k,z in v.items()}
        if isinstance(v,list):return [unpack(z) for z in v]
        return v
    encoded=encode(value)
    assert unpack(encoded)==value
    return encoded,counts


def main():
    prompt=(RUN/'review/prompt.txt').read_text(encoding='utf-8')
    raw=prompt.split('\nINPUT_JSON\n',1)[1].split('\nCOMPLETE SOURCE\n',1)[0]
    payload=json.loads(raw)
    result=[]
    variants=[]
    inventory_only=deepcopy(payload)
    inventory_only['input_contract_inventory']=global_scope_inventory(payload['input_contract_inventory'])
    assert expand_global_scope_inventory(inventory_only['input_contract_inventory'])==payload['input_contract_inventory']
    variants.append(('inventory_tables',inventory_only,{}))
    for maps in [False,True]:
        encoded,counts=record_tables(payload,maps)
        variants.append(('generic_record_tables'+('_and_maps' if maps else ''),encoded,counts))
    for name,encoded,counts in variants:
        for dictionary in [False,True]:
            variant=encoded
            extra={}
            if dictionary:variant,extra=shared(encoded,20)
            chars=1079505-len(raw)+len(compact(variant))
            result.append({'name':name+('_shared_values' if dictionary else ''),'delivery_chars_before_instructions':chars,
                'saved_chars':1079505-chars,'headroom_before_instructions':1048576-chars,'counts':counts,
                'dictionary':extra,'roundtrip_equal':True,'source_unchanged':True})
            if name=='generic_record_tables_and_maps' and dictionary:write('generic-tables-and-shared-values-payload.json',variant)
    write('record-table-measurement.json',{'variants':result})
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
