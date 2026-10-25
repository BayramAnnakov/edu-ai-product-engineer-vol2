#!/usr/bin/env python3
"""Release guard: local references, trace manifest, and common private-data mistakes."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", "__pycache__", ".bakeoff", "work", "dist"}
FORBIDDEN = [r"us\.cloud\.langfuse\.com", r"github\.com/Empatika/twain", r"/Users/[A-Za-z]", r"[A-Za-z0-9._%+-]+@(?:gmail|empatika)\.", r"sk-(?:proj|lf)-[A-Za-z0-9_-]{12,}", r"pk-lf-[A-Za-z0-9_-]{12,}", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"]


def scan_text(text):
    return [pattern for pattern in FORBIDDEN if re.search(pattern, text)]


def check(root=ROOT):
    failures = []
    files = [p for p in root.rglob("*") if p.is_file() and not set(p.relative_to(root).parts) & SKIP]
    for p in files:
        rel = p.relative_to(root)
        if set(rel.parts) & {"instructor", ".secrets", ".env", ".firecrawl"}:
            failures.append(f"Excluded path: {rel}")
        if p.stat().st_size > 1_000_000:
            failures.append(f"Unexpected large file: {rel}")
        try: text = p.read_text(encoding="utf-8")
        except UnicodeError:
            failures.append(f"Unexpected binary: {rel}"); continue
        if p.name != "check_bundle.py" and scan_text(text):
            failures.append(f"Private-data pattern in {rel}")
        if p.suffix == ".md":
            for link in re.findall(r"\]\(([^)]+)\)", text):
                if "://" in link or link.startswith("#") or " " in link: continue
                target = (p.parent / link.split("#")[0]).resolve()
                if not target.exists(): failures.append(f"Missing local link in {rel}: {link}")
    td = root / "lesson1" / "traces"
    manifest = json.loads((td / "manifest.json").read_text())
    for name, expected in manifest["sha256"].items():
        if hashlib.sha256((td / name).read_bytes()).hexdigest() != expected:
            failures.append(f"Trace changed: {name}")
        for line in (td / name).read_text().splitlines():
            row = json.loads(line)
            if any(k in row for k in ("trace_url", "headers", "raw_response", "request", "organization_id", "project_id")):
                failures.append(f"Private trace field in {name}")
            if row["evidence_mode"] != "recorded-provider" or row["input_text_complete"] is not False:
                failures.append(f"Trace scope incorrect: {name}")
    return failures, len(files)


if __name__ == "__main__":
    errors, n = check()
    if errors:
        print("\n".join(errors), file=sys.stderr); raise SystemExit(1)
    print(f"Student bundle checked: {n} files; local links and trace hashes valid; no configured private-data patterns found. Manual review still required for new content.")
