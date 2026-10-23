#!/usr/bin/env python3
"""Validate a security-auditor coverage.json.

Usage: python3 -I check_coverage.py <coverage.json> [--final] [--skill-dir DIR]

--final      also require that no unit is still planned or in_progress (Step 6).
--skill-dir  also require every lens reference to name an existing reference file.
Exit status 0 when valid, 1 when invalid, 2 on usage or read errors.
"""
import json
import os
import re
import sys

STATUSES = {
    "planned", "in_progress", "covered", "candidate", "blocked",
    "deferred", "out_of_scope", "not_applicable",
}
REASON_STATUSES = {"deferred", "out_of_scope", "not_applicable"}
OWNED_STATUSES = {"in_progress", "covered", "candidate", "blocked"}
FINGERPRINT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]*$")
AGENT = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
REQUIRED = ("id", "surface", "boundary", "lens", "subsystem", "paths", "status")


def nonempty_str(value):
    return isinstance(value, str) and value.strip() != ""


def rel_path_ok(value):
    return (
        nonempty_str(value)
        and not os.path.isabs(value)
        and ".." not in value.replace("\\", "/").split("/")
    )


def check_unit(unit, idx, errors, skill_dir):
    base = f"units[{idx}]"
    if not isinstance(unit, dict):
        errors.append(f"{base}: expected object")
        return
    for key in REQUIRED:
        if key not in unit:
            errors.append(f"{base}.{key}: missing")
    for key in ("id", "surface", "boundary", "lens", "subsystem"):
        if key in unit and not nonempty_str(unit[key]):
            errors.append(f"{base}.{key}: expected non-empty string")
    paths = unit.get("paths")
    if not isinstance(paths, list) or not paths or not all(rel_path_ok(p) for p in paths):
        errors.append(f"{base}.paths: expected non-empty list of repository-relative paths")

    lens = unit.get("lens")
    if skill_dir and nonempty_str(lens):
        lens_file = lens.split("#", 1)[0]
        if not os.path.isfile(os.path.join(skill_dir, "references", lens_file)):
            errors.append(f"{base}.lens: no reference file {lens_file!r}")

    status = unit.get("status")
    if status not in STATUSES:
        errors.append(f"{base}.status: {status!r} not one of {sorted(STATUSES)}")
        return

    owner = unit.get("owner")
    checks = unit.get("checks", [])
    fps = unit.get("fingerprints", [])
    unresolved = unit.get("unresolved", [])
    reason = unit.get("reason")

    if not isinstance(checks, list):
        errors.append(f"{base}.checks: expected list")
        checks = []
    if not isinstance(fps, list):
        errors.append(f"{base}.fingerprints: expected list")
        fps = []
    if not isinstance(unresolved, list):
        errors.append(f"{base}.unresolved: expected list")
        unresolved = []

    for fp in fps:
        if not isinstance(fp, str) or not FINGERPRINT.match(fp):
            errors.append(f"{base}.fingerprints: invalid fingerprint {fp!r}")

    for c_idx, check in enumerate(checks):
        cbase = f"{base}.checks[{c_idx}]"
        if not isinstance(check, dict):
            errors.append(f"{cbase}: expected object")
            continue
        if not (isinstance(check.get("agent"), str) and AGENT.match(check["agent"])):
            errors.append(f"{cbase}.agent: expected lowercase agent id")
        if check.get("method") not in ("source", "local"):
            errors.append(f"{cbase}.method: expected 'source' or 'local'")
        cpaths = check.get("paths")
        if not isinstance(cpaths, list) or not cpaths or not all(rel_path_ok(p) for p in cpaths):
            errors.append(f"{cbase}.paths: expected non-empty list of repository-relative paths")
        if not nonempty_str(check.get("result")):
            errors.append(f"{cbase}.result: expected non-empty string")
        evidence = check.get("evidence")
        if check.get("method") == "local" and not rel_path_ok(evidence):
            errors.append(f"{cbase}.evidence: local check needs an output-relative evidence path")
        if check.get("method") == "source" and evidence not in (None, ""):
            errors.append(f"{cbase}.evidence: source check takes no evidence file")

    if status in OWNED_STATUSES:
        if not (isinstance(owner, str) and AGENT.match(owner)):
            errors.append(f"{base}.owner: {status} unit needs a lowercase agent id")
    elif owner not in (None, ""):
        errors.append(f"{base}.owner: {status} unit must have no owner")

    if status in ("planned", "in_progress") and (checks or fps or unresolved):
        errors.append(f"{base}: {status} unit must have no checks, fingerprints, or unresolved facts")
    if status in REASON_STATUSES:
        if not nonempty_str(reason):
            errors.append(f"{base}.reason: {status} unit needs a reason")
        if checks or fps:
            errors.append(f"{base}: {status} unit must carry no evidence")
    if status in ("covered", "candidate", "blocked") and not checks:
        errors.append(f"{base}.checks: {status} unit needs at least one check")
    if status == "covered" and (fps or unresolved):
        errors.append(f"{base}: covered unit must have no fingerprints or unresolved facts")
    if status == "candidate" and not fps:
        errors.append(f"{base}.fingerprints: candidate unit needs at least one fingerprint")
    if status == "blocked":
        if fps:
            errors.append(f"{base}.fingerprints: blocked unit carries no fingerprint")
        if not unresolved:
            errors.append(f"{base}.unresolved: blocked unit needs the blocking fact")


def main(argv):
    args = [a for a in argv[1:]]
    final = "--final" in args
    skill_dir = None
    if "--skill-dir" in args:
        i = args.index("--skill-dir")
        if i + 1 >= len(args):
            print("--skill-dir needs a value", file=sys.stderr)
            return 2
        skill_dir = args[i + 1]
        del args[i:i + 2]
    args = [a for a in args if a != "--final"]
    if len(args) != 1:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        with open(args[0], encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError) as exc:
        print(f"cannot read {args[0]}: {exc}", file=sys.stderr)
        return 2

    errors = []
    units = data.get("units") if isinstance(data, dict) else None
    if not isinstance(units, list):
        print("FAIL: top level must be an object with a 'units' list")
        return 1

    seen_ids, seen_keys = set(), {}
    for idx, unit in enumerate(units):
        check_unit(unit, idx, errors, skill_dir)
        if not isinstance(unit, dict):
            continue
        uid = unit.get("id")
        if uid in seen_ids:
            errors.append(f"units[{idx}].id: duplicate {uid!r}")
        seen_ids.add(uid)
        key = (unit.get("surface"), unit.get("boundary"), unit.get("lens"), unit.get("lifecycle"))
        if key in seen_keys:
            errors.append(f"units[{idx}]: same surface/boundary/lens/lifecycle as {seen_keys[key]!r}")
        seen_keys.setdefault(key, uid)
        if final and unit.get("status") in ("planned", "in_progress"):
            errors.append(f"units[{idx}] ({uid}): still {unit.get('status')} at final check")

    if errors:
        for err in errors[:100]:
            print(f"ERROR: {err}")
        if len(errors) > 100:
            print(f"... {len(errors) - 100} more")
        print(f"FAIL: {len(errors)} error(s) in {len(units)} unit(s)")
        return 1
    counts = {}
    for unit in units:
        counts[unit["status"]] = counts.get(unit["status"], 0) + 1
    summary = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
    print(f"PASS: {len(units)} unit(s) valid ({summary})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
