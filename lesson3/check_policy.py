"""Boundary checks for event identity, intended writes and current routing."""

import concurrent.futures
import os
from pathlib import Path
import tempfile
import unittest
import policy
import service


class RecoveryPolicy(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        os.environ["SCOUT_LAB_STATE"] = str(Path(temp.name) / "drill")
        service.initialize()

    def test_two_deliveries_one_event(self):
        self.assertEqual(
            policy.inbox_key(service.TIMER, "one"),
            policy.inbox_key(service.TIMER, "two"),
        )
        self.assertNotEqual(
            policy.inbox_key(service.TIMER, "one"),
            policy.inbox_key(service.PILOT, "two"),
        )

    def test_two_triggers_one_request_and_new_authorized_request(self):
        other = dict(service.ALDER, event_id="reconcile-17")
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            replies = list(pool.map(service.create_draft, (service.ALDER, other)))
        self.assertEqual(replies[0], replies[1])
        new = service.create_draft(dict(other, request_id="outreach/17/dec"))
        self.assertNotEqual(replies[0], new)

    def test_new_event_for_same_account_enters_inbox_once(self):
        with service.transaction() as db:
            service.deliver(db, service.DECEMBER, "dec-first")
            service.deliver(db, service.DECEMBER, "dec-again")
        events = [j["event"] for j in service.inspect()["jobs"]]
        self.assertEqual(events, [service.ALDER, service.DECEMBER])

    def test_updated_routing_and_approval(self):
        service.outage()
        self.assertEqual(service.create_draft(service.TIMER), "skipped: revoked")
        service.create_draft(service.PILOT)
        self.assertEqual(
            [r["recipient"] for r in service.inspect()["drafts"]], ["procurement"]
        )


if __name__ == "__main__":
    unittest.main()
