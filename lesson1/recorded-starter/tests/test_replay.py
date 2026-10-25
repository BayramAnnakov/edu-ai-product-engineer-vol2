import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import lab
import engine as E


class RecordedStarterTests(unittest.TestCase):
    def test_actual_reference_and_jev_error_without_network(self):
        with patch('socket.socket.connect', side_effect=AssertionError('network forbidden')):
            bank = lab.load_bank()
            reference = E.run('dev', 'free-wins', E.DEFAULT_POLICY, bank)
            candidate = E.run('dev', 'hybrid-fixed', {**E.DEFAULT_POLICY, 'rules': True, 'typed': True}, bank)
        self.assertEqual((reference['summary']['q'], reference['summary']['n']), (30, 30))
        self.assertAlmostEqual(reference['summary']['cost'], .0497, places=6)
        self.assertEqual(candidate['summary']['q'], 27)
        failure = next(r for r in candidate['rows'] if r['id'] == 'D-005')
        self.assertEqual(failure['answer']['score'], 3)
        self.assertFalse(failure['correct'])

    def test_unseen_request_fails_instead_of_inventing_an_answer(self):
        case = copy.deepcopy(E.F.CASES['dev'][0])
        case['company'] = 'A changed input not in the recordings'
        with self.assertRaisesRegex(E.LabError, 'Unseen request'):
            E.response(case, 'large', 'high', E.DEFAULT_POLICY, lab.load_bank())

    def test_router_receives_facts_without_reference_answers(self):
        def check(case, strict):
            self.assertNotIn('label', case)
            self.assertTrue(all('supports' not in r for r in case['records']))
            return None
        with patch.object(E.ROUTER, 'rule', side_effect=check):
            E.rule(E.F.CASES['dev'][0])

    def test_quality_failure_is_not_overridden_by_savings(self):
        bank = lab.load_bank()
        reference = E.run('dev', 'free-wins', E.DEFAULT_POLICY, bank)
        candidate = E.run('dev', 'hybrid-fixed', {**E.DEFAULT_POLICY, 'rules': True, 'typed': True}, bank)
        prediction = {'minimum_gain': 30, 'quality_floor': 95}
        verdict = E.assess({'free-wins': reference, 'candidate': candidate}, prediction)['rows']['candidate']
        self.assertGreater(verdict['gain_percent'], 30)
        self.assertFalse(verdict['quality_pass'])
        self.assertFalse(verdict['passes'])

    def test_bundle_has_only_dev_recordings_and_no_private_urls(self):
        bank = lab.load_bank()
        self.assertEqual(len(E.F.CASES['dev']), 30)
        self.assertNotIn('s1', E.F.CASES)
        self.assertTrue(all(r['request']['case']['id'].startswith('D-') for r in bank['responses'].values()))
        self.assertNotIn('trace_url', json.dumps(bank))

    def test_cli_requires_explicit_start_and_complete_prediction(self):
        with tempfile.TemporaryDirectory() as folder:
            def call(*args):
                return subprocess.run([sys.executable, str(ROOT / 'lab.py'), *args], cwd=folder, capture_output=True, text=True)
            self.assertNotEqual(call('init').returncode, 0)
            self.assertEqual(call('init', '--start', 'rule-starter').returncode, 0)
            state_path = Path(folder) / '.lab-state.json'
            self.assertIsNone(json.loads(state_path.read_text())['started'])
            self.assertEqual(call('compare').returncode, 0)
            self.assertIsNone(json.loads(state_path.read_text())['started'])
            blocked = call('run', '--effort', 'fixed')
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIsNone(json.loads(state_path.read_text())['started'])
            lab.write(Path(folder) / 'prediction.json', {'hypothesis': 'Try Jev on eligible cases', 'minimum_gain': 30, 'quality_floor': 95, 'stop_minutes': 15})
            policy_path = Path(folder) / 'policy.json'
            policy = json.loads(policy_path.read_text()); policy['typed'] = True; lab.write(policy_path, policy)
            result = call('run', '--effort', 'fixed')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('27/30 correct', result.stdout)
            self.assertIn('Quality floor failed', result.stdout)
            self.assertNotEqual(call('evaluate', '--packet', 'not-released.json').returncode, 0)
            self.assertEqual(call('export', '--decision', 'revert', '--reason', 'Three wrong priorities exceed our tolerance').returncode, 0)
            receipt = json.loads((Path(folder) / 'decision.json').read_text())
            self.assertEqual(receipt['scope'], 'Development only; final evaluation not run')
            self.assertEqual(receipt['results']['hybrid-fixed']['summary']['q'], 27)

    def test_freeze_requires_matching_runs_and_blocks_policy_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            def call(*args):
                return subprocess.run([sys.executable, str(ROOT / 'lab.py'), *args], cwd=folder, capture_output=True, text=True)
            self.assertEqual(call('init', '--start', 'compact').returncode, 0)
            lab.write(Path(folder) / 'prediction.json', {'hypothesis': 'Test the narrow rule', 'minimum_gain': 5, 'quality_floor': 100, 'stop_minutes': 15})
            self.assertEqual(call('compare').returncode, 0)
            policy_path = Path(folder) / 'policy.json'
            policy = json.loads(policy_path.read_text()); policy['rules'] = True; lab.write(policy_path, policy)
            self.assertEqual(call('run', '--effort', 'fixed').returncode, 0)
            self.assertNotEqual(call('freeze').returncode, 0)
            self.assertEqual(call('run', '--effort', 'adaptive').returncode, 0)
            self.assertEqual(call('freeze').returncode, 0)
            self.assertNotEqual(call('run', '--effort', 'fixed').returncode, 0)
            policy['typed'] = True; lab.write(policy_path, policy)
            rejected = call('evaluate', '--packet', 'not-released.json')
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('remain unchanged', rejected.stderr)


if __name__ == '__main__':
    unittest.main()
