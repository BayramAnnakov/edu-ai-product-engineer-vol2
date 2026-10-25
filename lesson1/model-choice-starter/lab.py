#!/usr/bin/env python3
"""Offline development practice with real recorded model calls. No network or keys."""
import argparse,hashlib,json,math,time
from pathlib import Path
import router
ROOT=Path(__file__).resolve().parent
WORK=ROOT/'work'

def read(p):return json.loads(Path(p).read_text())
def write(p,d):Path(p).write_text(json.dumps(d,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load_data():
 m=read(ROOT/'manifest.json')
 # router.py is intentionally editable; facts and recordings stay fixed.
 if sha(ROOT/'data.json')!=m['files']['data.json']:raise ValueError('Recorded inputs changed; new facts or prompts need new calls')
 return read(ROOT/'data.json')
def valid(c,a):
 if not isinstance(a,dict) or set(a)!={'score','reason_code','evidence_ids'}:return False
 ids=a['evidence_ids']
 return type(a['score']) is int and 1<=a['score']<=5 and a['reason_code'] in ('buying_signal','icp_fit','budget_frozen','locked_in_competitor','not_icp') and isinstance(ids,list) and 1<=len(ids)<=2 and all(isinstance(i,str) and i in {r['id'] for r in c['records'] if r['account_id']==c['account_id']} for i in ids) and len(set(ids))==len(ids)
def task_correct(c,a,reference):
 return valid(c,a) and all(a[k]==reference[k] for k in ('score','reason_code')) and bool(set(a['evidence_ids']) & set(reference['evidence_ids']))
def execute(policy,data=None,*,custom_router=True):
 data=data or load_data();rows=[]
 if policy['model'] not in ('sol','luna','terra'):raise ValueError('Unknown recorded model')
 if any(type(policy[k]) is not bool for k in ('use_rule','use_jev')):raise ValueError('Policy flags must be true or false')
 for item in data['rows']:
  c=item['input'];recordings=item['recordings'];calls=[]
  answer=router.answer_rule(c) if policy['use_rule'] else None
  if answer is None:
   jc=None
   if policy['use_jev']:
    calls.append(recordings['jev']);jc=recordings['jev']['choice']
   model=router.choose_model(c,jc,policy['model']) if custom_router else policy['model']
   if model not in ('sol','luna','terra'):raise ValueError('Unrecorded model choice; no substituted answer')
   call=recordings[model];calls.append(call);answer=call['answer']
   if model!='sol' and not valid(c,answer):calls.append(recordings['sol']);answer=recordings['sol']['answer']
  correct=task_correct(c,answer,item['reference'])
  rows.append({'case_id':c['id'],'company':c['company'],'answer':answer,'task_correct':correct,
   'attempts':len(calls),'cost_usd':sum(x['cost_usd'] for x in calls),'seconds':sum(x['seconds'] for x in calls)})
 n=len(rows);q=sum(r['task_correct'] for r in rows);cost=sum(r['cost_usd'] for r in rows)
 return {'n':n,'q':q,'cost_usd':cost,'cost_per_correct':cost/q if q else None,
  'scoring_p95':sorted(r['seconds'] for r in rows)[round((n-1)*.95)],'attempts':sum(r['attempts'] for r in rows),'rows':rows}
def print_summary(name,r):print(f"{name}: {r['q']}/{r['n']} correct; ${r['cost_usd']/r['n']:.6f}/company; ${r['cost_usd']:.6f} total; scoring p95 {r['scoring_p95']:.2f}s; {r['attempts']} model/router attempts")
def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True)
 sub.add_parser('compare')
 inspect=sub.add_parser('inspect');inspect.add_argument('--case',required=True)
 init=sub.add_parser('init');init.add_argument('--model',choices=['sol','luna','terra'],required=True)
 sub.add_parser('run')
 export=sub.add_parser('export');export.add_argument('--decision',choices=['revert','insufficient-evidence','test-further'],required=True);export.add_argument('--reason',required=True);export.add_argument('--trace-case',required=True)
 a=p.parse_args();data=load_data()
 if a.cmd=='inspect':
  item=next((r for r in data['rows'] if r['input']['id']==a.case),None)
  if item is None:raise ValueError('Choose an existing development case ID')
  print(json.dumps({'scoring_criteria':data['scoring_criteria'],**item},indent=2));return
 if a.cmd=='compare':
  for model in ('sol','luna','terra'):print_summary(model,execute({'model':model,'use_rule':False,'use_jev':False},data,custom_router=False))
  print_summary('Jev -> Luna/Sol',execute({'model':'luna','use_rule':False,'use_jev':True},data));return
 if a.cmd=='init':
  WORK.mkdir(exist_ok=False)
  write(WORK/'policy.json',{'model':a.model,'use_rule':False,'use_jev':False})
  write(WORK/'prediction.json',{'hypothesis':'','quality_floor':None,'minimum_gain_percent':None,'stop_minutes':None})
  print('Fill work/prediction.json; edit one setting in work/policy.json or router.py.');return
 if a.cmd=='run':
  pred=read(WORK/'prediction.json');policy=read(WORK/'policy.json')
  if not pred.get('hypothesis','').strip():raise ValueError('Write the hypothesis first')
  for field in ('quality_floor','minimum_gain_percent','stop_minutes'):
   value=pred.get(field)
   if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0 or (field=='stop_minutes' and not 0<value<=120) or (field!='stop_minutes' and value>100):raise ValueError('Choose a valid '+field)
  lock=WORK/'prediction-lock.json'
  if lock.exists():
   frozen=read(lock)
   if pred!=frozen['prediction']:raise ValueError('Forecast locked; start a separately named experiment')
   if time.time()-frozen['started']>pred['stop_minutes']*60:raise ValueError('Tuning-time cap exhausted; export completed evidence')
  else:write(lock,{'prediction':pred,'started':time.time()})
  baseline=execute({'model':'luna','use_rule':False,'use_jev':False},data,custom_router=False);candidate=execute(policy,data)
  gain=100*(1-candidate['cost_per_correct']/baseline['cost_per_correct']) if candidate['cost_per_correct'] is not None else None
  report={'evidence_mode':'recorded-provider replay','scope':'Development practice only; no held-out validation or new paid calls',
   'prediction':pred,'policy':policy,'router_hash':sha(ROOT/'router.py'),'data_hash':sha(ROOT/'data.json'),'baseline':baseline,'candidate':candidate,
   'gain_percent_vs_luna':gain,'quality_pass':candidate['q']/candidate['n']*100>=pred['quality_floor'],
   'gain_pass':gain is not None and gain>=pred['minimum_gain_percent']}
  (WORK/'tested-router.py').write_text((ROOT/'router.py').read_text())
  write(WORK/'report.json',report);print_summary('candidate',candidate);print(f"Cost/correct vs Luna: {abs(gain):.1f}% {'lower' if gain>=0 else 'higher'}" if gain is not None else 'No finite cost/correct');print('Read error cases and preserve failed gates.');return
 report=read(WORK/'report.json')
 if not a.reason.strip():raise ValueError('Give a reason')
 item=next((r for r in data['rows'] if r['input']['id']==a.trace_case),None)
 if item is None:raise ValueError('Select an existing development case as trace evidence')
 report['selected_trace']={**item,'baseline':next(r for r in report['baseline']['rows'] if r['case_id']==a.trace_case),'candidate':next(r for r in report['candidate']['rows'] if r['case_id']==a.trace_case)}
 report['owner_decision']={'choice':a.decision,'reason':a.reason,'authorizes_deployment':False}
 write(WORK/'decision.json',report)
 b=report['baseline'];c=report['candidate'];trace=report['selected_trace']
 text=['# Development decision',report['scope'],'## Hypothesis',report['prediction']['hypothesis'],
  f"Quality floor: {report['prediction']['quality_floor']}%; useful cost/correct reduction: {report['prediction']['minimum_gain_percent']}%; tuning cap: {report['prediction']['stop_minutes']} minutes.",
  '## Observed comparison']
 table=['| Path | Correct | Total model USD | USD/correct | Model/router attempts | Scoring p95 |','|---|---|---|---|---|---|']
 for name,r in [('Fixed Luna baseline',b),('Candidate',c)]:
  unit=f"${r['cost_per_correct']:.6f}" if r['cost_per_correct'] is not None else 'No finite value'
  table.append(f"| {name} | {r['q']}/{r['n']} | ${r['cost_usd']:.6f} | {unit} | {r['attempts']} | {r['scoring_p95']:.3f}s |")
 text.append('\n'.join(table))
 text += [f"Quality gate: {'pass' if report['quality_pass'] else 'fail'}. Useful-gain gate: {'pass' if report['gain_pass'] else 'fail'}.",
  '## Owner decision',a.decision+': '+a.reason,'This decision authorizes no deployment.',
  '## Tested configuration','```json\n'+json.dumps(report['policy'],indent=2)+'\n```',
  'Exact tested code: tested-router.py. Router SHA256: '+report['router_hash']+'. Data SHA256: '+report['data_hash']+'.',
  '## Selected evidence: '+a.trace_case,'```json\n'+json.dumps({'input':trace['input'],'reference':trace['reference'],'baseline':trace['baseline'],'candidate':trace['candidate']},indent=2)+'\n```',
  '## Limits','Known synthetic development cases, no new independent evaluation. Model cost uses recorded provider usage; local code, infrastructure, review and coding-agent effort are unpriced. P95 uses one saved call per request. No production saving is established.']
 (WORK/'decision.md').write_text('\n\n'.join(text)+'\n')
 print('Saved work/decision.md and work/decision.json. This is development evidence, not production validation.')
if __name__=='__main__':
 try:main()
 except (ValueError,FileExistsError,FileNotFoundError,KeyError) as e:raise SystemExit(str(e))
