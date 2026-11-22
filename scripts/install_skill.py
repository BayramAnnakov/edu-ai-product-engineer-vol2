#!/usr/bin/env python3
"""Copy a complete local skill (bakeoff, memory-wiki or kill-resume-drill) into a project; never overwrite an existing skill."""
import argparse
from pathlib import Path
import shutil


SKILLS = ("bakeoff", "memory-wiki", "kill-resume-drill")


def install(target, host, skill="bakeoff"):
    if host not in ("codex", "claude"):
        raise ValueError("host must be codex or claude")
    if skill not in SKILLS:
        raise ValueError("skill must be one of " + ", ".join(SKILLS))
    root = Path(__file__).resolve().parents[1]
    folder = Path(target).expanduser().resolve() / (".agents" if host == "codex" else ".claude") / "skills" / skill
    if folder.exists() or folder.is_symlink():
        raise FileExistsError(f"Existing skill preserved: {folder}")
    folder.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(root / "skills" / skill, folder, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return folder


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--host", choices=("codex", "claude"), required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--skill", choices=SKILLS, default="bakeoff")
    a = p.parse_args()
    try:
        print(f"Installed {install(a.target, a.host, a.skill)}; use " + ("$" if a.host == "codex" else "/") + a.skill)
    except (OSError, ValueError) as e:
        p.exit(1, str(e) + "\n")
