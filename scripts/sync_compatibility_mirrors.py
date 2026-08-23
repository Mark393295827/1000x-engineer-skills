#!/usr/bin/env python3
"""Generate and verify complete compatibility mirrors from the canonical plugin skill."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

CANONICAL = Path("plugins/1000x-engineer/skills/1000x-engineer")
MIRRORS = (Path("skills/1000x-engineer"), Path(".agents/skills/1000x-engineer"))
IGNORED_PARTS = {"__pycache__", ".DS_Store"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


def files(root: Path) -> dict[str, Path]:
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file() and not (set(path.parts) & IGNORED_PARTS) and path.suffix not in IGNORED_SUFFIXES
    }


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def differences(canonical: Path, mirror: Path) -> list[str]:
    canonical_files = files(canonical)
    mirror_files = files(mirror) if mirror.is_dir() else {}
    issues = [f"missing {name}" for name in sorted(canonical_files.keys() - mirror_files.keys())]
    issues += [f"extra {name}" for name in sorted(mirror_files.keys() - canonical_files.keys())]
    issues += [
        f"mismatch {name}"
        for name in sorted(canonical_files.keys() & mirror_files.keys())
        if digest(canonical_files[name]) != digest(mirror_files[name])
    ]
    return issues


def sync(canonical: Path, mirror: Path, prune: bool) -> None:
    canonical_files = files(canonical)
    mirror.mkdir(parents=True, exist_ok=True)
    for relative, source in canonical_files.items():
        target = mirror / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    if prune:
        for relative, target in files(mirror).items():
            if relative not in canonical_files:
                target.unlink()
        for directory in sorted((path for path in mirror.rglob("*") if path.is_dir()), reverse=True):
            if not any(directory.iterdir()):
                directory.rmdir()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sync compatibility mirrors from the canonical plugin skill.")
    parser.add_argument("--check", action="store_true", help="Report drift without writing files")
    parser.add_argument("--prune", action="store_true", help="Remove stale mirror files after canonical files are copied")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    canonical = (root / CANONICAL).resolve()
    if not canonical.is_dir():
        print(f"missing canonical skill: {canonical}", file=sys.stderr)
        return 2
    has_drift = False
    for relative in MIRRORS:
        mirror = (root / relative).resolve()
        if args.check:
            issues = differences(canonical, mirror)
            if issues:
                has_drift = True
                print(f"mirror drift: {relative}", file=sys.stderr)
                for issue in issues:
                    print(f"  {issue}", file=sys.stderr)
        else:
            sync(canonical, mirror, args.prune)
            print(f"synchronized {relative}")
    return 1 if has_drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
