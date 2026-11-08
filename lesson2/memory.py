"""Local memory exercise. Work on allow_write and visible in this file."""

import argparse
import json
import os
from pathlib import Path
import tempfile

FIXTURE = Path(__file__).with_name("memory.json")
SNAPSHOT = "2026-11-07"


def load_store(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_store(path, store):
    """Replace the exercise file only after the new contents are complete."""
    with tempfile.NamedTemporaryFile("w", dir=path.parent, encoding="utf-8", delete=False) as stream:
        pending = Path(stream.name)
        try:
            json.dump(store, stream, indent=2, ensure_ascii=False)
            stream.close()
            os.replace(pending, path)
        finally:
            pending.unlink(missing_ok=True)


def allow_write(candidate, source, session_client, now):
    # Lab B edit point 1. Source identity alone does not establish authority.
    return bool(source)


def visible(records, session_client, now):
    # Lab B edit point 2. The starting implementation returns all stored facts.
    return list(records)


def commit(path, candidate, session_client, now=SNAPSHOT):
    store = load_store(path)
    source = next((row for row in store["sources"] if row["id"] == candidate["source_id"]), None)
    if not allow_write(candidate, source, session_client, now):
        return False
    record_id = candidate["source_id"]
    if any(row["id"] == record_id for row in store["memory"]):
        return True
    current_records = [
        row for row in store["memory"]
        if row["client_id"] == candidate["client_id"] and row["key"] == candidate["key"] and not row.get("superseded_by")
    ]
    if any(row["effective_on"] >= candidate["effective_on"] for row in current_records):
        return False
    for row in current_records:
        row["superseded_by"] = record_id
    fields = ("source_id", "client_id", "key", "value", "effective_on", "expires_on")
    store["memory"].append({"id": record_id, **{name: candidate[name] for name in fields}})
    save_store(path, store)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("client", choices=["client-a", "client-b"])
    parser.add_argument("--store", type=Path, default=FIXTURE)
    args = parser.parse_args()
    print(json.dumps(visible(load_store(args.store)["memory"], args.client, SNAPSHOT), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
