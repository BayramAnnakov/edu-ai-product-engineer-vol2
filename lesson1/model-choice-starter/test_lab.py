import copy,socket,unittest,json,tempfile,sys,io
from pathlib import Path
from contextlib import redirect_stdout
from unittest.mock import patch
import lab
class StarterTests(unittest.TestCase):
 def test_actual_model_comparison_offline(self):
  with patch.object(socket,'socket',side_effect=AssertionError('Network forbidden')):
   d=lab.load_data()
   rows={m:lab.execute({'model':m,'use_rule':False,'use_jev':False},d,custom_router=False) for m in ('sol','luna','terra')}
  self.assertEqual(len(d['rows']),30)
  self.assertEqual([rows[m]['q'] for m in ('sol','luna','terra')],[30,30,29])
  self.assertLess(rows['luna']['cost_usd'],rows['sol']['cost_usd'])
  self.assertTrue(all(r['input']['id'].startswith('D-') for r in d['rows']))
 def test_router_overhead_and_rule_coverage_counted(self):
  d=lab.load_data();base=lab.execute({'model':'luna','use_rule':False,'use_jev':False},d)
  routed=lab.execute({'model':'luna','use_rule':False,'use_jev':True},d)
  with patch.object(lab.router,'answer_rule',return_value=d['rows'][0]['reference']):
   ruled=lab.execute({'model':'luna','use_rule':True,'use_jev':False},d)
  self.assertEqual(routed['attempts'],60);self.assertGreater(routed['cost_usd'],base['cost_usd'])
  self.assertEqual(ruled['attempts'],0)  # Resolved rules must incur no recorded model call.
 def test_edited_router_cannot_change_frozen_luna_baseline(self):
  d=lab.load_data();policy={'model':'luna','use_rule':False,'use_jev':False}
  expected=lab.execute(policy,d,custom_router=False)
  with patch.object(lab.router,'choose_model',return_value='terra'):
   baseline=lab.execute(policy,d,custom_router=False)
   candidate=lab.execute(policy,d)
  self.assertEqual(baseline,expected)
  self.assertEqual(candidate['q'],29)
  self.assertEqual(baseline['q'],30)
 def test_correct_score_with_non_supporting_real_record_fails(self):
  item=lab.load_data()['rows'][0];a={**item['reference'],'evidence_ids':[item['input']['records'][0]['id']]}
  self.assertTrue(lab.valid(item['input'],a))
  self.assertFalse(lab.task_correct(item['input'],a,item['reference']))
 def test_complete_offline_cli_exports_readable_table_and_tested_code(self):
  with tempfile.TemporaryDirectory() as td,patch.object(lab,'WORK',Path(td)/'work'),redirect_stdout(io.StringIO()):
   for args in [['init','--model','luna']]:
    with patch.object(sys,'argv',['lab.py',*args]):lab.main()
   lab.write(lab.WORK/'prediction.json',{'hypothesis':'Check immutable Luna baseline','quality_floor':100,'minimum_gain_percent':0,'stop_minutes':10})
   with patch.object(sys,'argv',['lab.py','run']):lab.main()
   with patch.object(sys,'argv',['lab.py','export','--decision','test-further','--trace-case','D-015','--reason','Known dev practice; gather independent cases']):lab.main()
   text=(lab.WORK/'decision.md').read_text();saved=lab.read(lab.WORK/'decision.json')
   self.assertIn('Scoring p95 |\n|---',text)
   self.assertIn('Selected evidence: D-015',text)
   self.assertFalse(saved['owner_decision']['authorizes_deployment'])
   self.assertEqual(lab.sha(lab.WORK/'tested-router.py'),saved['router_hash'])
 def test_public_business_policy_is_included(self):
  self.assertIn('50',lab.load_data()['scoring_criteria']['fit'])
 def test_valid_format_does_not_mean_correct_score(self):
  item=next(r for r in lab.load_data()['rows'] if r['input']['id']=='D-015')
  a=item['recordings']['terra']['answer'];self.assertTrue(lab.valid(item['input'],a))
  self.assertNotEqual(a['score'],item['reference']['score'])
if __name__=='__main__':unittest.main()
