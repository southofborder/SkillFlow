import sys, time, os
LOG='D:/projects/SkillFlow/packages/skill-fcg-py/diagB_js8.log'
def w(msg):
    with open(LOG,'a',encoding='utf-8') as f: f.write(msg+'\n')
open(LOG,'w').close()
sys.argv=['x','analyze',sys.argv[1],'-o','D:/projects/SkillFlow/packages/skill-fcg-py/diagB_out.json']
try:
    import psutil; proc=psutil.Process(os.getpid()); rss=lambda: proc.memory_info().rss/1e6
except Exception: rss=lambda: -1
import skill_fcg.flood.state as S
import skill_fcg.flood.analyzer as A

# --- force JS 8-component key (drop transform_sig 9th + origin_class 10th) ---
def js8_key(state):
    label = state.label or {}
    return "|".join([
        state.current_node or "",
        label.get("label") or "",
        label.get("category") or "",
        label.get("subtype") or "",
        S.label_availability(label, state),
        state.storage_key or "",
        state.flow_mode or "",
        state.phase or "after_action",
    ])
A.build_flow_state_key = js8_key

cnt={'n':0,'t0':None,'last':None}
origreg=A.register_label_flow
def reg(flow,state,**k):
    if cnt['t0'] is None:
        cnt['t0']=time.time(); cnt['last']=cnt['t0']; w('FLOOD START rss=%.0fMB'%rss())
    cnt['n']+=1
    if cnt['n']%2000==0:
        now=time.time(); dt=now-cnt['last']; cnt['last']=now
        w('calls=%d flows=%d queue=%d events=%d rss=%.0fMB elapsed=%.0fs rate=%.0f/s'%(
            cnt['n'],len(state.label_flows),len(state.queue),len(state.all_events),rss(),now-cnt['t0'],2000/dt if dt else 0))
    return origreg(flow,state,**k)
A.register_label_flow=reg
w('LOADED js8-key, running LLM+flood...')
from skill_fcg.cli import main
try: main()
except SystemExit: pass
except Exception as e: w('EXC %r'%e)
w('DONE calls=%d elapsed=%.0fs'%(cnt['n'], (time.time()-cnt['t0']) if cnt['t0'] else -1))
