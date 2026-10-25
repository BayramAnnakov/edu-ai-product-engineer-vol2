import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


B = module("bakeoff", ROOT / "skills/bakeoff/scripts/bakeoff.py")
I = module("installer", ROOT / "scripts/install_skill.py")
G = module("guard", ROOT / "scripts/check_bundle.py")


class BakeoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p = Path(self.tmp.name)
        self.cases = [{"id": f"e-{n}", "group": f"group-{n}", "input": {"value": n}, "expected": "yes"} for n in range(3)]
        B.dump(self.p / "cases.json", self.cases)
        self.contract = json.loads((ROOT / "skills/bakeoff/assets/experiment.json").read_text())
        self.contract.update(name="test", task_contract="Return yes correctly", hypothesis="Avoid redundant work", label_source="Independent fixture labels")
        self.rows = [{"case_id": c["id"], "output": "yes", "judge_accepted": True, "serious_failure": False, "job_seconds": 1, "review_seconds": None, "evidence_mode": "fixture", "attempts": [{"id": c["id"] + "-a", "status": "success", "cost_usd": .1}]} for c in self.cases]

    def jsonl(self, name, rows):
        p = self.p / name; p.write_text("".join(json.dumps(r) + "\n" for r in rows)); return p

    def lock(self):
        B.dump(self.p / "experiment.json", self.contract)
        return B.freeze(self.p / "experiment.json", self.p / "lock.json")

    def compare(self, candidate, baseline=None):
        return B.comparison(self.lock(), self.jsonl("baseline.jsonl", baseline or self.rows), self.jsonl("candidate.jsonl", candidate))

    def cheaper(self):
        rows = copy.deepcopy(self.rows)
        for row in rows: row["attempts"][0]["cost_usd"] = .05
        return rows

    def test_quality_failure_blocks_keep_even_when_judge_accepts(self):
        rows = self.cheaper(); rows[0]["output"] = "wrong"
        r = self.compare(rows)
        self.assertEqual(r["experiment_verdict"], "failed")
        self.assertEqual(r["candidate"]["judge_accepted"], 3)
        self.assertEqual(r["candidate"]["task_correct"], 2)
        B.write_report(r, self.p / "report")
        with self.assertRaises(B.EvidenceError): B.decide(self.p / "report/report.json", "keep", "Cheap", {})
        with self.assertRaises(B.EvidenceError): B.decide(self.p / "report/report.json", "bounded-trial", "Test limits", {})
        d = B.decide(self.p / "report/report.json", "bounded-trial", "Explicit risk", {k: "bounded" for k in ("owner", "value", "exposure", "rollback", "checkpoint")})
        self.assertEqual(d["experiment_verdict"], "failed")
        self.assertFalse(d["owner_decision"]["authorizes_deployment"])

    def test_failed_attempt_is_charged_and_unknown_cost_is_not_zero(self):
        rows = self.cheaper(); rows[0]["attempts"].append({"id": "retry-error", "status": "error", "cost_usd": .3})
        r = self.compare(rows)
        self.assertAlmostEqual(r["candidate"]["machine_cost_usd"], .45)
        self.assertEqual(r["candidate"]["failed_attempts"], 1)

    def test_unknown_cost_is_inconclusive(self):
        rows = self.cheaper(); rows[0]["attempts"][0]["cost_usd"] = None
        r = self.compare(rows)
        self.assertIsNone(r["candidate"]["machine_cost_usd"])
        self.assertEqual(r["experiment_verdict"], "inconclusive")

    def test_missing_cases_keep_fixed_denominator(self):
        r = self.compare(self.cheaper()[:2])
        self.assertEqual(r["candidate"]["n"], 3)
        self.assertEqual(r["candidate"]["missing_cases"], ["e-2"])
        self.assertEqual(r["experiment_verdict"], "inconclusive")

    def test_repeated_case_and_attempt_rejected(self):
        path = self.jsonl("bad.jsonl", [self.rows[0], self.rows[0]])
        with self.assertRaises(B.EvidenceError): B.load_rows(path, self.cases)
        rows = copy.deepcopy(self.rows); rows[1]["attempts"][0]["id"] = rows[0]["attempts"][0]["id"]
        with self.assertRaises(B.EvidenceError): B.load_rows(self.jsonl("bad.jsonl", rows), self.cases)

    def test_changed_frozen_input_is_rejected(self):
        lock = self.lock(); B.dump(self.p / "cases.json", self.cases[:2])
        with self.assertRaises(B.EvidenceError): B.verify_lock(lock)

    def test_renamed_dev_input_is_not_heldout(self):
        B.dump(self.p / "dev.json", [{**self.cases[0], "id": "d-new", "group": "another-group"}])
        self.contract["dev_cases"] = "dev.json"
        with self.assertRaises(B.EvidenceError): self.lock()

    def test_shared_entity_is_not_heldout(self):
        B.dump(self.p / "dev.json", [{**self.cases[0], "id": "d-new", "input": {"value": 99}}])
        self.contract["dev_cases"] = "dev.json"
        with self.assertRaises(B.EvidenceError): self.lock()

    def test_prior_development_cost_counts_against_total_budget(self):
        prior = copy.deepcopy(self.rows); prior[0]["attempts"][0]["cost_usd"] = 1
        self.jsonl("dev.jsonl", prior); self.contract.update(prior_receipts=["dev.jsonl"], max_total_cost_usd=1)
        r = self.compare(self.cheaper())
        self.assertGreater(r["budget_accounting"]["known_total_cost_usd"], 1)
        self.assertFalse(r["gates"]["budget"])
        self.assertEqual(r["experiment_verdict"], "failed")

    def test_unknown_prior_cost_stays_unknown(self):
        prior = copy.deepcopy(self.rows); prior[0]["attempts"][0]["cost_usd"] = None
        self.jsonl("dev.jsonl", prior); self.contract["prior_receipts"] = ["dev.jsonl"]
        r = self.compare(self.cheaper()); self.assertIsNone(r["gates"]["budget"])

    def test_zero_correct_has_no_finite_ratio(self):
        rows = self.cheaper()
        for r in rows: r["output"] = "wrong"
        r = self.compare(rows)
        self.assertIsNone(r["candidate"]["cost_per_correct"])
        self.assertEqual(r["experiment_verdict"], "failed")

    def test_negative_nonfinite_and_boolean_costs_rejected(self):
        for cost in (-1, float("inf"), True):
            rows = self.cheaper(); rows[0]["attempts"][0]["cost_usd"] = cost
            with self.assertRaises(B.EvidenceError): B.load_rows(self.jsonl("bad.jsonl", rows), self.cases)

    def test_output_grade_is_independent_from_supplied_judge(self):
        rows = self.cheaper(); rows[0]["task_correct"] = False
        with self.assertRaises(B.EvidenceError): B.load_rows(self.jsonl("bad.jsonl", rows), self.cases)
        del rows[0]["task_correct"]; del rows[0]["output"]
        with self.assertRaises(B.EvidenceError): B.load_rows(self.jsonl("bad.jsonl", rows), self.cases)

    def test_human_labels_need_provenance(self):
        cases = copy.deepcopy(self.cases)
        for c in cases: del c["expected"]
        with self.assertRaises(B.EvidenceError): B.load_rows(self.jsonl("bad.jsonl", self.cheaper()), cases)

    def test_report_cannot_be_silently_edited_before_decision(self):
        r = self.compare(self.cheaper()); B.write_report(r, self.p / "report")
        rp = self.p / "report/report.json"; d = B.read(rp); d["experiment_verdict"] = "failed"; B.dump(rp, d)
        with self.assertRaises(B.EvidenceError): B.decide(rp, "revert", "Evidence", {})

    def test_dev_only_export_and_unmeasured_review(self):
        self.contract["stage"] = "dev-screening"
        r = self.compare(self.cheaper())
        self.assertIn("Dev screening only", B.markdown(r))
        self.assertIsNone(r["candidate"]["review_seconds"])

    def test_install_both_hosts_and_preserve_existing_skill(self):
        for host in ("codex", "claude"):
            installed = I.install(self.p / host, host)
            self.assertTrue((installed / "references/receipt-format.md").is_file())
            before = (installed / "SKILL.md").read_bytes()
            with self.assertRaises(FileExistsError): I.install(self.p / host, host)
            self.assertEqual((installed / "SKILL.md").read_bytes(), before)

    def test_kit_links_trace_manifest_and_sanitization_guard(self):
        errors, count = G.check(); self.assertEqual(errors, []); self.assertGreater(count, 20)
        self.assertTrue(G.scan_text("https://us.cloud." + "langfuse.com/project/private"))


if __name__ == "__main__": unittest.main()
