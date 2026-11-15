"""Local deterministic check evidence and metrics. Never calls Moodle itself."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import uuid


REASONS = ("change", "first-acceptance", "diagnosis", "repeat-unchanged")


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def atomic_json(path, value):
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp, path)


def append_event(root, event):
    with (root / "events.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"at": now(), **event}, ensure_ascii=False) + "\n")


@contextmanager
def locked(root):
    root.mkdir(parents=True, exist_ok=True)
    lock = root / ".lock"
    with lock.open("x", encoding="utf-8") as stream:
        stream.write(str(os.getpid()))
    try:
        yield
    finally:
        lock.unlink()


def files_hash(base, names, root):
    if not names:
        raise ValueError("Empty dependency list")
    result = {}
    for name in names:
        path = (base / name).resolve(strict=True)
        paths = sorted(path.rglob("*")) if path.is_dir() else [path]
        # Include directory presence even when empty; detect files added/removed.
        if path.is_dir():
            result[str(path) + "/"] = "directory"
        for item in paths:
            item = item.resolve(strict=True)
            if item == root or root in item.parents:
                raise ValueError("Evidence/log directory must not be an input")
            if item.is_file():
                result[str(item)] = digest(item)
    return result


def fingerprint(base, check, root):
    command = list(check["command"])
    if not command or not all(isinstance(v, str) for v in command):
        raise ValueError("command must be a nonempty argument array")
    cwd = (base / check.get("cwd", ".")).resolve(strict=True)
    if not cwd.is_dir():
        raise ValueError("cwd must be a directory")
    if command[0] == "{python}":
        command[0] = sys.executable
    executable = shutil.which(command[0])
    if not executable:
        candidate = (cwd / command[0]).resolve(strict=True)
        executable = str(candidate)
    command[0] = str(Path(executable).resolve(strict=True))
    # Batch/shell wrappers are not a safe deterministic command interface.
    if Path(command[0]).suffix.lower() in (".bat", ".cmd"):
        raise ValueError("Use an executable directly, not a batch wrapper")
    for key in ("id", "phase", "property", "scope", "environment"):
        if not check.get(key):
            raise ValueError(f"Missing check field: {key}")
    if check.get("reason") not in REASONS:
        raise ValueError("Invalid reason")
    metadata = {
        "inputs": files_hash(base, check["inputs"], root),
        "validators": files_hash(base, check["validators"], root),
        "runner_sha256": digest(__file__),
        "executable_sha256": digest(command[0]),
        "command": command,
        "cwd": str(cwd),
        "platform": platform.platform(),
        "environment": check["environment"],
        "property": check["property"],
        "scope": check["scope"],
        "timeout_seconds": check.get("timeout_seconds", 300),
    }
    key = hashlib.sha256(json.dumps(metadata, sort_keys=True).encode()).hexdigest()
    return key, metadata


def run_checks(spec, root, args):
    config = read_json(spec)
    checks = config["checks"]
    ids = [c["id"] for c in checks]
    if len(set(ids)) != len(ids) or not ids:
        raise ValueError("Check IDs must be unique and nonempty")
    if args.check and args.check not in ids:
        raise ValueError("Unknown check ID")
    evidence_path = root / "evidence.json"
    evidence = read_json(evidence_path) if evidence_path.exists() else {}
    failed = False
    for check in checks:
        if args.check and check["id"] != args.check:
            continue
        started = time.perf_counter()
        event = {"kind": "check", "id": check["id"], "phase": check["phase"],
                 "reason": "repeat-unchanged" if args.force_reason else check["reason"]}
        if args.force_reason:
            event["force_reason"] = args.force_reason
        key, metadata = fingerprint(spec.parent, check, root)
        old = evidence.get(check["id"], {})
        cacheable = check.get("cacheable") is True
        if (cacheable and not args.force_reason and old.get("status") == "PASS"
                and old.get("fingerprint") == key):
            append_event(root, {**event, "status": "REUSED", "evidence_at": old["at"],
                                "duration_seconds": time.perf_counter() - started})
            print(f"REUSED {check['id']} ({old['at']})")
            continue
        # Invalidate previous success before executing; interruptions cannot revive it.
        evidence[check["id"]] = {"status": "RUNNING", "at": now()}
        atomic_json(evidence_path, evidence)
        log_dir = root / "logs"
        log_dir.mkdir(exist_ok=True)
        log_path = log_dir / (uuid.uuid4().hex + ".log")
        code = None
        error = None
        try:
            with log_path.open("wb") as log:
                result = subprocess.run(metadata["command"], cwd=metadata["cwd"],
                                        stdout=log, stderr=subprocess.STDOUT,
                                        timeout=metadata["timeout_seconds"], check=False)
            code = result.returncode
            after, _ = fingerprint(spec.parent, check, root)
            status = "PASS" if code == 0 and after == key else "FAIL"
            if after != key:
                error = "Inputs, validator or environment changed during execution"
        except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
            status = "FAIL"
            error = type(exc).__name__
        record = {"status": status, "at": now(), "fingerprint": key,
                  "metadata": metadata, "exit_code": code,
                  "log": str(log_path), "duration_seconds": time.perf_counter() - started}
        if error:
            record["error"] = error
        evidence[check["id"]] = record
        atomic_json(evidence_path, evidence)
        append_event(root, {**event, "status": status, "exit_code": code,
                            "duration_seconds": record["duration_seconds"]})
        print(f"{status} {check['id']} ({record['duration_seconds']:.3f}s) log={log_path}")
        failed |= status != "PASS"
    return int(failed)


def number(value):
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise argparse.ArgumentTypeError("Expected a finite nonnegative number")
    return value


def count(value):
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("Expected a nonnegative integer")
    return parsed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("run", "event", "summary"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--spec", required=True, type=Path)
        if name == "run":
            cmd.add_argument("--check")
            cmd.add_argument("--force-reason")
        if name == "event":
            cmd.add_argument("--phase", required=True)
            cmd.add_argument("--reason", required=True, choices=REASONS)
            cmd.add_argument("--source", required=True)
            for field in ("reads", "writes", "errors", "corrections"):
                cmd.add_argument("--" + field, type=count)
            for field in ("duration-seconds", "wait-seconds"):
                cmd.add_argument("--" + field, type=number)
    args = parser.parse_args()
    spec = args.spec.resolve(strict=True)
    root = spec.parent / (spec.stem + ".pruefung-intern")
    if args.action == "summary":
        totals = {}
        events = root / "events.jsonl"
        for line in events.read_text(encoding="utf-8").splitlines() if events.exists() else []:
            event = json.loads(line)
            group = totals.setdefault(event["phase"] + "/" + event["reason"], {})
            state = event.get("status", "reported_package")
            group[state] = group.get(state, 0) + 1
            for field in ("reads", "writes", "errors", "corrections", "wait_seconds", "duration_seconds"):
                if field in event:
                    label = ("check_seconds" if event["kind"] == "check" else "package_seconds") if field == "duration_seconds" else field
                    group[label] = group.get(label, 0) + event[field]
        print(json.dumps(totals, ensure_ascii=False, indent=2))
        return 0
    with locked(root):
        if args.action == "run":
            return run_checks(spec, root, args)
        event = {k: v for k, v in vars(args).items() if k not in ("action", "spec") and v is not None}
        append_event(root, {"kind": "package", **event})
        print("RECORDED package metrics (reported, not independently measured)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
