"""Stage approved course sources below the plan folder and keep quelle-manifest.json.

mbz.ps1 copies only the folder of kursplan.json into the build container, so the
sources must lie below it. This tool copies them byte-identically to quelle/ and
records their SHA-256. The manifest is an internal tool log, not a review binding.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

MAPPING = 'quelle-zuordnung.json'
MANIFEST = 'quelle-manifest.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(text, prefix=None):
    """Validate a forward-slash relative path; optionally require a first segment."""
    parts = PurePosixPath(text).parts
    if '\\' in text or not parts or PurePosixPath(text).is_absolute() or ':' in text \
            or any(part in ('..', '.') for part in parts):
        raise ValueError('Ungueltiger Pfad: ' + text)
    if prefix and (parts[0] != prefix or len(parts) < 2):
        raise ValueError('Ziel muss unter ' + prefix + '/ liegen: ' + text)
    return text


def load(plan_dir):
    """Return {target below plan folder: source below course folder}."""
    mapping = json.loads((plan_dir / MAPPING).read_text(encoding='utf-8'))
    if not isinstance(mapping, dict) or not mapping:
        raise ValueError(MAPPING + ' muss ein nicht leeres Objekt Ziel -> Quelle sein')
    return {relative(target, 'quelle'): relative(source) for target, source in mapping.items()}


def read_manifest(plan_dir):
    path = plan_dir / MANIFEST
    if not path.is_file():
        return {}
    return {key.replace('\\', '/'): value for key, value in json.loads(path.read_text(encoding='utf-8')).items()}


def check(plan_dir):
    """Return a list of deviations between sources, staged copies and manifest."""
    mapping, manifest, problems = load(plan_dir), read_manifest(plan_dir), []
    for target, source in sorted(mapping.items()):
        origin, copy = plan_dir.parent / source, plan_dir / target
        if not origin.is_file():
            problems.append('QUELLE FEHLT: ' + source)
        elif not copy.is_file():
            problems.append('KOPIE FEHLT: ' + target)
        elif manifest.get(target) != sha(copy):
            problems.append('KOPIE WEICHT VOM MANIFEST AB: ' + target)
        elif sha(origin) != manifest[target]:
            problems.append('QUELLE GEAENDERT: ' + source + ' -> ' + target)
    staged = plan_dir / 'quelle'
    present = {p.relative_to(plan_dir).as_posix() for p in staged.rglob('*') if p.is_file()} if staged.is_dir() else set()
    problems += ['NICHT ZUGEORDNET: ' + name for name in sorted(present - set(mapping))]
    problems += ['MANIFEST OHNE ZUORDNUNG: ' + name for name in sorted(set(manifest) - set(mapping))]
    return problems


def copy(plan_dir, targets, everything):
    """Copy missing targets; replace existing ones only if named or everything is set."""
    mapping, manifest = load(plan_dir), read_manifest(plan_dir)
    unknown = sorted(set(targets) - set(mapping))
    if unknown:
        raise ValueError('Nicht in ' + MAPPING + ': ' + ', '.join(unknown))
    done = []
    for target, source in sorted(mapping.items()):
        origin, dest = plan_dir.parent / source, plan_dir / target
        if not origin.is_file():
            raise ValueError('Quelle fehlt: ' + source)
        if dest.is_file() and not (everything or target in targets):
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(origin.read_bytes())
        manifest[target] = sha(dest)
        done.append(target)
    manifest = {key: manifest[key] for key in sorted(manifest) if key in mapping}
    (plan_dir / MANIFEST).write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + '\n',
                                     encoding='utf-8', newline='\n')
    return done


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    cli.add_argument('aktion', choices=('pruefen', 'kopieren'))
    cli.add_argument('--plan-ordner', type=Path, required=True, help='Ordner der kursplan.json, z. B. <Kurs>/moodle-mbz')
    cli.add_argument('--alle', action='store_true', help='kopieren: auch vorhandene Kopien ersetzen')
    cli.add_argument('ziele', nargs='*', help='kopieren: vorhandene Kopien, die ersetzt werden sollen (quelle/...)')
    args = cli.parse_args(argv)
    try:
        plan_dir = args.plan_ordner.resolve()
        if args.aktion == 'kopieren':
            for name in copy(plan_dir, args.ziele, args.alle):
                print('KOPIERT: ' + name)
        problems = check(plan_dir)
    except (OSError, ValueError) as error:
        print('FEHLER: ' + str(error), file=sys.stderr)
        return 2
    for line in problems:
        print(line)
    print('PASS' if not problems else 'FAIL: %d Abweichung(en)' % len(problems))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
