import sys, time, os
LOG='D:/projects/SkillFlow/packages/skill-fcg-py/diagC.log'
def w(msg):
    with open(LOG,'a',encoding='utf-8') as f: f.write(msg+'\n')
open(LOG,'w').close()
sys.argv=['x','analyze',sys.argv[1],'-o','D:/projects/SkillFlow/packages/skill-fcg-py/diagC_out.json']
try:
    import psutil; proc=psutil.Process(os.getpid()); rss=lambda: proc.memory_info().rss/1e6
except Exception: rss=lambda: -1
import skill_fcg.flood.analyzer as A
import skill_fcg.flood.state as S
from skill_fcg.flood.observations import is_sink_like_profile

def label_key(label):
    label = label or {}
    return "%s|%s|%s" % (label.get("label") or "", label.get("category") or "", label.get("subtype") or "")

sink_full=set()   # (node,label,transform_sig,origin_class)  == DOE current unit
sink_noseq=set()  # (node,label,origin_class)                == floor without transform order
cnt={'n':0,'t0':None,'last':None}
origreg=A.register_label_flow
def reg(flow,state,**k):
    if cnt['t0'] is None:
        cnt['t0']=time.time(); cnt['last']=cnt['t0']; w('FLOOD START rss=%.0fMB'%rss())
    cnt['n']+=1
    prof=state.profiles_by_node.get(flow.current_node)
    if is_sink_like_profile(prof):
        lk=label_key(flow.label)
        oc=S._origin_class_of(flow)
        sink_full.add((flow.current_node, lk, flow.transform_sig or "", oc))
        sink_noseq.add((flow.current_node, lk, oc))
    if cnt['n']%4000==0:
        now=time.time(); dt=now-cnt['last']; cnt['last']=now
        w('calls=%d flows=%d queue=%d sinkFULL=%d sinkNOSEQ=%d rss=%.0fMB t=%.0fs rate=%.0f/s'%(
            cnt['n'],len(state.label_flows),len(state.queue),len(sink_full),len(sink_noseq),
            rss(),now-cnt['t0'],4000/dt if dt else 0))
    return origreg(flow,state,**k)
A.register_label_flow=reg
w('LOADED, running LLM+flood...')
from skill_fcg.cli import main
try: main()
except SystemExit: pass
except Exception as e: w('EXC %r'%e)
w('DONE calls=%d flows=%d sinkFULL=%d sinkNOSEQ=%d elapsed=%.0fs'%(
    cnt['n'], -1, len(sink_full), len(sink_noseq), (time.time()-cnt['t0']) if cnt['t0'] else -1))
