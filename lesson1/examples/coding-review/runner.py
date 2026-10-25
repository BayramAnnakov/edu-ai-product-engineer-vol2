#!/usr/bin/env python3
"""Execute routing code against an explicitly authored offline model bank."""
import argparse,importlib.util,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--split',choices=['dev','eval'],required=True);p.add_argument('--arm',choices=['baseline','candidate'],required=True);p.add_argument('--out',required=True);a=p.parse_args()
base=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('workflow',base/'workflow.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
cases=json.loads((base/(a.split+'.json')).read_text());bank=json.loads((base/(a.split+'-model-bank.json')).read_text());rows=[]
for c in cases:
 route='model' if a.arm=='baseline' else w.choose_route(c['input'])
 if route not in ('model','cheap'):raise ValueError('choose_route must return model or cheap')
 output=bank[c['id']] if route=='model' else w.cheap_answer(c['input'])
 rows.append({'case_id':c['id'],'output':output,'judge_accepted':True,'serious_failure':bool(route=='cheap' and c['input'].get('cache') and c['input']['cache']['tenant']!=c['input']['tenant']),'job_seconds':9.0 if route=='model' else 1.0,'review_seconds':None,'evidence_mode':'fixture','route':route,'attempts':[{'id':c['id']+'-model','status':'success','cost_usd':.02,'input_tokens':500,'output_tokens':20,'cache_read_tokens':0,'cache_write_tokens':0}] if route=='model' else []})
Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(''.join(json.dumps(r)+'\n' for r in rows));print(json.dumps({'cases':len(rows),'model_calls':sum(len(r['attempts']) for r in rows),'mode':'fixture','out':a.out}))
