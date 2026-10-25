"""Public development data loader. The final evaluation packet is released later."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data/cases-dev.json").read_text())
VERSION = DATA["version"]
AS_OF = DATA["as_of"]
RUBRIC = DATA["rubric"]
REASONS = RUBRIC["reason_codes"]
CASES = {"dev": DATA["cases"]}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def public_case(case):
    result = copy.deepcopy(case)
    for key in ("slice", "enrichment_s", "label"):
        result.pop(key, None)
    for record in result["records"]:
        record.pop("supports", None)
    return result
