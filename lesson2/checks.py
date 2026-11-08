"""Public acceptance contract. Run python3 -m unittest -v checks."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import memory


def candidate(source):
    return {
        "source_id": source["id"],
        **{key: source[key] for key in ("client_id", "key", "value", "effective_on", "expires_on")},
    }


class MemoryChecks(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "store.json"
        self.path.write_bytes(memory.FIXTURE.read_bytes())
        self.sources = {row["id"]: candidate(row) for row in memory.load_store(self.path)["sources"]}
        self.note = self.sources["CALL-NOTE-09"]
        self.correction = self.sources["OWNER-07"]

    def read_fresh(self, client):
        output = subprocess.check_output(
            [sys.executable, str(Path(memory.__file__).resolve()), client, "--store", str(self.path)],
            text=True,
        )
        return {row["id"]: row for row in json.loads(output)}

    def test_untrusted_note_cannot_approve_discount(self):
        self.assertFalse(memory.commit(self.path, self.note, "client-a"))
        spoofed = {**self.note, "kind": "authorized_approval_event"}
        self.assertFalse(memory.commit(self.path, spoofed, "client-a"))
        self.assertNotIn("CALL-NOTE-09", self.read_fresh("client-a"))
        self.assertFalse(memory.commit(self.path, self.sources["OWNER-08"], "client-a"))
        self.assertTrue(memory.commit(self.path, self.sources["DEAL-APPROVAL-15"], "client-a"))
        self.assertIn("DEAL-APPROVAL-15", self.read_fresh("client-a"))

    def test_verified_correction_survives_restart(self):
        altered = {**self.correction, "value": "Contact the CFO first."}
        self.assertFalse(memory.commit(self.path, altered, "client-a"))
        self.assertFalse(memory.commit(self.path, {**self.correction, "client_id": "client-b"}, "client-a"))
        self.assertTrue(memory.commit(self.path, {**self.correction, "audit_override": "approved"}, "client-a"))
        self.assertNotIn("audit_override", self.read_fresh("client-a")["OWNER-07"])

    def test_client_isolation_applies_to_read_and_write(self):
        self.assertFalse(memory.commit(self.path, self.correction, "client-b"))
        self.assertTrue(memory.commit(self.path, self.correction, "client-a"))
        self.assertEqual(set(self.read_fresh("client-b")), {"OWNER-12"})

    def test_expired_and_superseded_records_are_excluded(self):
        self.assertTrue(memory.commit(self.path, self.correction, "client-a"))
        self.assertFalse(memory.commit(self.path, self.sources["OWNER-10"], "client-a"))
        self.assertEqual(set(self.read_fresh("client-a")), {"OWNER-07", "TEMP-02"})


if __name__ == "__main__":
    unittest.main()
