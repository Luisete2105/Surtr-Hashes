#!/usr/bin/env python3
"""Validate the Surtr hashes registry (hashes.json).

Usage:
    python tools/validate_hashes.py [hashes.json]

Exit code 0 = valid, 1 = invalid.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date

HEX64 = re.compile(r"^[0-9a-f]{64}$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

REQUIRED_FIELDS = ("sha256", "surtr_version", "nickname", "name", "date_added")
OPTIONAL_FIELDS = ("note", "repo_url", "approved_by")


def parse_version(value: str) -> tuple[int, ...]:
    core = value.split("-")[0].split("+")[0]
    parts: list[int] = []
    for chunk in core.split("."):
        parts.append(int(chunk) if chunk.isdigit() else 0)
    return tuple(parts)


def compare_versions(a: str, b: str) -> int:
    pa, pb = parse_version(a), parse_version(b)
    length = max(len(pa), len(pb))
    for i in range(length):
        x = pa[i] if i < len(pa) else 0
        y = pb[i] if i < len(pb) else 0
        if x != y:
            return -1 if x < y else 1
    return 0


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else "hashes.json"
    errors: list[str] = []
    warnings: list[str] = []

    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not read {path}: {exc}")
        return 1

    if not isinstance(data, dict):
        print("ERROR: root of hashes.json must be a JSON object")
        return 1

    if not isinstance(data.get("schema"), int):
        errors.append("'schema' must be an integer")

    entries = data.get("entries")
    if not isinstance(entries, list):
        print("ERROR: 'entries' must be a JSON array")
        return 1

    seen_hashes: dict[str, int] = {}

    for index, entry in enumerate(entries):
        where = f"entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{where}: entry must be a JSON object")
            continue

        for field in REQUIRED_FIELDS:
            value = entry.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append(f"{where}: missing required field '{field}'")

        for field in entry:
            if field not in REQUIRED_FIELDS and field not in OPTIONAL_FIELDS:
                warnings.append(f"{where}: unknown field '{field}'")

        sha = entry.get("sha256")
        if isinstance(sha, str):
            if not HEX64.match(sha):
                errors.append(f"{where}: 'sha256' must be 64 lowercase hex characters")
            elif sha in seen_hashes:
                errors.append(f"{where}: duplicate sha256 (also at entries[{seen_hashes[sha]}])")
            else:
                seen_hashes[sha] = index

        version = entry.get("surtr_version")
        if isinstance(version, str) and not SEMVER.match(version):
            errors.append(f"{where}: 'surtr_version' must look like '0.1.0'")

        added = entry.get("date_added")
        if isinstance(added, str):
            if not DATE_RE.match(added):
                errors.append(f"{where}: 'date_added' must be YYYY-MM-DD")
            else:
                try:
                    date.fromisoformat(added)
                except ValueError:
                    errors.append(f"{where}: 'date_added' is not a valid date")

        repo = entry.get("repo_url")
        if repo is not None and (
            not isinstance(repo, str) or not repo.startswith(("http://", "https://"))
        ):
            warnings.append(f"{where}: 'repo_url' should be an http(s) URL")

        approvers = entry.get("approved_by")
        if approvers is not None:
            if isinstance(approvers, str):
                # A single reviewer name, or "" when nobody has verified it yet.
                pass
            elif isinstance(approvers, list):
                for j, reviewer in enumerate(approvers):
                    if not isinstance(reviewer, str) or not reviewer.strip():
                        errors.append(
                            f"{where}: 'approved_by[{j}]' must be a non-empty string"
                        )
            else:
                errors.append(
                    f"{where}: 'approved_by' must be a string or a list of reviewer names"
                )

    # Ordering: Surtr version ascending, then date_added ascending.
    for index in range(1, len(entries)):
        prev, cur = entries[index - 1], entries[index]
        if not isinstance(prev, dict) or not isinstance(cur, dict):
            continue
        pv, cv = prev.get("surtr_version"), cur.get("surtr_version")
        if not isinstance(pv, str) or not isinstance(cv, str):
            continue
        cmp = compare_versions(pv, cv)
        if cmp > 0:
            errors.append(f"entries[{index}]: out of order - {cv} must come before {pv}")
            continue
        if cmp == 0:
            pd, cd = str(prev.get("date_added", "")), str(cur.get("date_added", ""))
            if pd > cd:
                errors.append(
                    f"entries[{index}]: same version {cv} but date {cd} is before {pd}"
                )

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        print(f"\nInvalid: {len(errors)} error(s), {len(warnings)} warning(s).")
        return 1

    print(f"OK: {len(entries)} entries valid ({len(warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
