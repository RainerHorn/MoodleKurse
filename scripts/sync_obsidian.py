#!/usr/bin/env python3
"""Generate safe Obsidian course index notes from Moodle course metadata."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CourseInfo:
    source_root: Path
    course_dir: Path
    subject: str
    slug: str
    status: dict[str, Any]


def _load_status(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def discover_courses(source_root: Path) -> list[CourseInfo]:
    courses_root = source_root / "courses"
    result: list[CourseInfo] = []
    if not courses_root.is_dir():
        return result
    for subject_dir in sorted(p for p in courses_root.iterdir() if p.is_dir()):
        for course_dir in sorted(p for p in subject_dir.iterdir() if p.is_dir()):
            status_path = course_dir / "STATUS.json"
            if status_path.is_file():
                result.append(CourseInfo(
                    source_root=source_root.resolve(),
                    course_dir=course_dir.resolve(),
                    subject=subject_dir.name,
                    slug=course_dir.name,
                    status=_load_status(status_path),
                ))
    return result


def _yaml_text(value: object) -> str:
    text = "" if value is None else str(value)
    return '"' + text.replace('\\', '\\\\').replace('"', '\\"') + '"'


def _file_link(label: str, path: Path) -> str:
    return f"[{label}]({path.resolve().as_uri()})"


def _mapping(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def render_course_note(course: CourseInfo) -> str:
    status = course.status
    brief = _mapping(status.get("brief"))
    technical = _mapping(status.get("technical"))
    authorization = _mapping(status.get("user_authorization"))
    next_action = _mapping(status.get("next_action"))
    title = str(status.get("course") or course.slug)
    updated = str(status.get("updated_at") or "")

    source_links = [
        _file_link("Projektordner", course.course_dir),
        _file_link("STATUS.json", course.course_dir / "STATUS.json"),
    ]
    for name in ("AUFTRAG.md", "RAHMEN.md", "PROZESS.md", "DEPLOYMENT-PLAN.md"):
        path = course.course_dir / name
        if path.is_file():
            source_links.append(_file_link(name, path))

    action_text = str(next_action.get("action") or "Nicht im Status hinterlegt.")
    owner = str(next_action.get("owner") or "")
    if owner:
        action_text += f" — Zuständig: `{owner}`"

    lines = [
        "---",
        "typ: kurs",
        f"fachrichtung: {course.subject}",
        f"slug: {course.slug}",
        f"lernfeld: {_yaml_text(brief.get('learning_field'))}",
        f"stunden_minuten: {brief.get('minutes') or ''}",
        f"aktualisiert: {_yaml_text(updated)}",
        f"quelle: {_yaml_text(course.course_dir.as_posix())}",
        "statusquelle: STATUS.json",
        "---",
        f"# {title}",
        "",
        "<!-- BEGIN GENERATED -->",
        "## Überblick",
        f"- **Bildungsgang:** {brief.get('program') or 'Nicht hinterlegt'}",
        f"- **Lernfeld:** {brief.get('learning_field') or 'Nicht hinterlegt'}",
        f"- **Umfang:** {brief.get('minutes') or 'Nicht hinterlegt'} Minuten",
        f"- **Handlungsprodukt:** {brief.get('product') or 'Nicht hinterlegt'}",
        f"- **Technischer Status:** `{technical.get('status') or 'UNKNOWN'}`",
        f"- **Benutzerfreigabe:** `{authorization.get('status') or 'UNKNOWN'}`",
        "",
        "## Verbindliche Originale",
        *[f"- {link}" for link in source_links],
        "",
        "> [!important] Quelle der Wahrheit",
        "> Diese Notiz ist ein Wegweiser. Kursartefakte und Status werden ausschließlich im Moodle-Kurse-Projekt gepflegt.",
        "",
        "## Nächster Schritt",
        action_text,
        "<!-- END GENERATED -->",
        "",
        "## Eigene Notizen",
        "<!-- BEGIN MANUAL -->",
        "",
        "<!-- END MANUAL -->",
        "",
    ]
    return "\n".join(lines)


def _manual_block(existing: str) -> str:
    begin = "<!-- BEGIN MANUAL -->"
    end = "<!-- END MANUAL -->"
    if begin not in existing or end not in existing:
        return ""
    return existing.split(begin, 1)[1].split(end, 1)[0].strip("\r\n")


def _with_manual_block(rendered: str, manual: str) -> str:
    begin = "<!-- BEGIN MANUAL -->"
    end = "<!-- END MANUAL -->"
    before, remainder = rendered.split(begin, 1)
    _, after = remainder.split(end, 1)
    body = f"\n{manual}\n" if manual else "\n\n"
    return before + begin + body + end + after


def sync_courses(source_root: Path, vault: Path, dry_run: bool = False) -> list[Path]:
    changed: list[Path] = []
    for course in discover_courses(source_root):
        target = vault / "10-Kurse" / course.subject / f"{course.slug}.md"
        rendered = render_course_note(course)
        if target.is_file():
            existing = target.read_text(encoding="utf-8")
            rendered = _with_manual_block(rendered, _manual_block(existing))
        else:
            existing = ""
        if rendered != existing:
            changed.append(target)
            if not dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(rendered, encoding="utf-8", newline="\n")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--vault", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    changed = sync_courses(args.source_root, args.vault, dry_run=args.dry_run)
    for target in changed:
        print(target)
    print(f"{len(changed)} Notiz(en) würden geändert" if args.dry_run else f"{len(changed)} Notiz(en) geändert")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
