#!/usr/bin/env python3
"""Copy the complete local skill into a project; never overwrite an existing skill."""
import argparse
from pathlib import Path
import shutil


def install(target, host):
    if host not in ("codex", "claude"):
        raise ValueError("host must be codex or claude")
    root = Path(__file__).resolve().parents[1]
    folder = Path(target).expanduser().resolve() / (".agents" if host == "codex" else ".claude") / "skills" / "bakeoff"
    if folder.exists() or folder.is_symlink():
        raise FileExistsError(f"Existing skill preserved: {folder}")
    folder.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(root / "skills" / "bakeoff", folder, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return folder


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--host", choices=("codex", "claude"), required=True)
    p.add_argument("--target", required=True)
    a = p.parse_args()
    try:
        print(f"Installed {install(a.target, a.host)}; use " + ("$bakeoff" if a.host == "codex" else "/bakeoff"))
    except (OSError, ValueError) as e:
        p.exit(1, str(e) + "\n")
