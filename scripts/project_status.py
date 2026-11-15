"""Read-only validation of local course status; never grants publishing permission."""
import hashlib
import json
from pathlib import Path
import re
import sys


def validate(data, base):
    errors = []

    def require(ok, message):
        if not ok:
            errors.append(message)

    def local_file(name):
        path = (base / name).resolve()
        if not path.is_relative_to(base.resolve()) or not path.is_file():
            raise ValueError(f"Missing/out-of-course file: {name}")
        return path

    def evidence(paths):
        require(isinstance(paths, list) and bool(paths), "Evidence reference missing")
        for name in paths:
            local_file(name)

    schema = data.get("schema_version")
    require(schema in (1, 2), "Unsupported schema_version")
    require(data.get("owner") == "orchestrator", "Status owner must be orchestrator")
    require(bool(data.get("course")), "Course missing")
    require(bool(data.get("next_action", {}).get("owner")) and
            bool(data.get("next_action", {}).get("action")), "Next action missing")
    package = data["package"]
    require(bool(package.get("id")), "Package ID missing")
    hashes = {}
    package_binding = None
    if schema == 1:
        for item in package["artifacts"]:
            name = item["path"]
            require(name not in hashes, f"Duplicate artifact: {name}")
            require(bool(item.get("owner")), f"Artifact owner missing: {name}")
            require(bool(re.fullmatch(r"[0-9a-f]{64}", item["sha256"])), f"Invalid SHA-256: {name}")
            actual = hashlib.sha256(local_file(name).read_bytes()).hexdigest()
            require(actual == item["sha256"], f"CHANGED: {name}; reconcile affected evidence only")
            hashes[name] = item["sha256"]
    else:
        files = set()
        for item in package.get("files", []):
            name = item["path"]
            require(name not in files, f"Duplicate artifact: {name}")
            require(bool(item.get("owner")), f"Artifact owner missing: {name}")
            local_file(name)
            files.add(name)
        package_binding = package.get("binding")
        if package_binding is not None:
            require(package_binding.get("type") in ("manifest", "git"), "Invalid package binding type")
            value = package_binding.get("value", "")
            if package_binding.get("type") == "manifest":
                require(bool(re.fullmatch(r"[0-9a-f]{64}", value)), "Invalid manifest binding")
            else:
                require(bool(re.fullmatch(r"[0-9a-f]{7,64}", value)), "Invalid git binding")
    for review in data["reviews"]:
        require(review["status"] in ("PENDING", "APPROVED", "REJECTED", "HISTORICAL_APPROVED", "UNRECONCILED"), "Invalid review status")
        require(review["scope"] in ("artifacts", "deployment-plan"), "Invalid review scope")
        if review["status"] != "PENDING":
            evidence(review["evidence"])
        if review["status"] in ("APPROVED", "REJECTED"):
            require(review.get("reviewer") == "reviewer", "Independent reviewer required")
            require(review.get("package_id") == package["id"], "Review package binding missing/stale")
            if schema == 1:
                require(bool(review.get("artifact_hashes")), "Review hash binding missing")
                reviewed = review.get("artifact_hashes", {})
                require(all(hashes.get(k) == v for k, v in reviewed.items()), "Review hash binding stale")
                if review["scope"] == "artifacts" and review.get("coverage") == "complete":
                    require(reviewed == hashes, "Complete review does not cover full package")
            elif package_binding is not None:
                require(review.get("binding") == package_binding, "Review package binding stale")
            if review["status"] == "APPROVED":
                for finding in data["findings"]:
                    require(not (finding["status"] == "OPEN" and
                                 finding.get("blocks") == review["scope"]),
                            f"APPROVED with open blocker: {finding['id']}")
    technical = data["technical"]
    require(technical["status"] in ("UNKNOWN", "OPEN", "READY"), "Invalid technical status")
    if technical.get("capabilities"):
        local_file(technical["capabilities"])
    if technical["status"] == "READY":
        require(bool(technical.get("environment")), "READY needs environment")
        evidence(technical["evidence"])
        require(not any(f["status"] == "OPEN" and f.get("blocks") == "technical"
                        for f in data["findings"]), "READY with technical blocker")
    auth = data["user_authorization"]
    require(auth["status"] in ("NOT_GRANTED", "GRANTED", "HISTORICAL_TEST_ONLY"), "Invalid authorization status")
    if auth["status"] != "NOT_GRANTED":
        evidence(auth["evidence"])
        require(bool(auth.get("scope")), "Authorization scope missing")
    if auth["status"] == "GRANTED":
        require(auth.get("package_id") == package["id"], "Authorization package binding stale")
        if schema == 1:
            require(bool(hashes) and auth.get("artifact_hashes") == hashes, "Authorization hash binding missing/stale")
        elif package_binding is not None:
            require(auth.get("binding") == package_binding, "Authorization package binding stale")
        require(bool(auth.get("instance")) and auth.get("course_id") is not None, "Authorization target missing")
    ids = set()
    for finding in data["findings"]:
        require(finding["id"] not in ids, "Duplicate finding ID")
        ids.add(finding["id"])
        for key in ("owner", "problem", "acceptance", "severity", "blocks"):
            require(bool(finding.get(key)), f"Finding {finding['id']}: {key} missing")
        require(finding["status"] in ("OPEN", "RESOLVED"), "Invalid finding status")
        if finding["status"] == "RESOLVED":
            evidence(finding["evidence"])
    return errors


def main():
    path = Path(sys.argv[1]).resolve(strict=True)
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    errors = validate(data, path.parent)
    if errors:
        print("\n".join(errors))
        return 1
    print(f"CONSISTENT: {data['course']} | package={data['package']['id']}")
    print(f"technical={data['technical']['status']} | user={data['user_authorization']['status']}")
    print(f"NEXT ({data['next_action']['owner']}): {data['next_action']['action']}")
    print("Local metadata only; no new review, live-state verification or publishing authorization.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
