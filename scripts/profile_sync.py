"""Read-only profile plan, then explicit hash-bound synchronization. No config/secrets."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def contained(root, relative):
    path = root / relative
    if Path(relative).is_absolute() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Path outside root')
    # Reject even in-root symlinks/junctions, including a linked profile root.
    for part in (path, *path.parents):
        if part.is_symlink() or (hasattr(part, 'is_junction') and part.is_junction()):
            raise ValueError('Linked path: ' + str(part))
    return path


def skill_files(skills):
    if not skills.exists():
        return []
    return sorted(p for p in skills.rglob('*') if p.is_file() and
                  not any(v.startswith('.') or v == '__pycache__' for v in p.relative_to(skills).parts)
                  and p.suffix not in ('.bak', '.pyc', '.log', '.tmp'))


def sources(repo):
    """Role files plus agents/_shared/skills, which is one source for every role."""
    result = {}
    shared = repo / 'agents' / '_shared' / 'skills'
    for soul in sorted((repo / 'agents').glob('*/SOUL.md')):
        role = soul.parent.name
        for path in [soul] + skill_files(soul.parent / 'skills'):
            target = role + '/' + path.relative_to(soul.parent).as_posix()
            result[target] = path.relative_to(repo).as_posix()
        for path in skill_files(shared):
            target = role + '/skills/' + path.relative_to(shared).as_posix()
            if target in result:
                raise ValueError('Shared skill collides with role file: ' + target)
            result[target] = path.relative_to(repo).as_posix()
    return result


def plan(repo, profiles):
    entries = []
    for target, source in sources(repo).items():
        src = contained(repo, source)
        dst = contained(profiles, target)
        a, b = digest(src), digest(dst)
        entries.append({'source': source, 'target': target, 'source_sha256': a,
                        'target_sha256': b, 'decision': 'same' if a == b else 'keep',
                        'state': 'SAME' if a == b else 'MISSING' if b is None else 'DIFF'})
    return {'schema': 1, 'repo': str(repo.resolve()), 'profiles': str(profiles.resolve()),
            'entries': entries}


def apply(plan_data, repo, profiles):
    if (plan_data['schema'] != 1 or Path(plan_data['repo']).resolve() != repo.resolve()
            or Path(plan_data['profiles']).resolve() != profiles.resolve()):
        raise ValueError('Plan roots/schema mismatch')
    allowed = sources(repo)
    writes, seen = [], set()
    for entry in plan_data['entries']:
        target = entry['target']
        if target in seen or allowed.get(target) != entry['source']:
            raise ValueError('Invalid/duplicate mapping')
        seen.add(target)
        src, dst = contained(repo, entry['source']), contained(profiles, target)
        if digest(src) != entry['source_sha256'] or digest(dst) != entry['target_sha256']:
            raise ValueError('Changed since preview: ' + target)
        decision = entry['decision']
        if decision not in ('same', 'keep', 'replace'):
            raise ValueError('Invalid decision')
        if decision == 'replace' and digest(src) != digest(dst):
            if not (profiles / target.split('/')[0]).is_dir():
                raise ValueError('Create missing profile using Hermes first: ' + target)
            backup = contained(profiles, target + '.bak')
            if backup.exists() and not backup.is_file():
                raise ValueError('Invalid backup path')
            writes.append((src, dst, backup, entry['target_sha256']))
    if seen != set(allowed):
        raise ValueError('Incomplete or stale plan')
    # Preflight all files before any writes. Each file is checked again just before replacement.
    for src, dst, backup, old_hash in writes:
        if digest(dst) != old_hash:
            raise ValueError('Concurrent target edit: ' + str(dst))
        content = src.read_bytes()
        expected = next(e['source_sha256'] for e in plan_data['entries'] if e['source'] == src.relative_to(repo).as_posix())
        if hashlib.sha256(content).hexdigest() != expected:
            raise ValueError('Concurrent source edit')
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and not backup.exists():
            with backup.open('xb') as handle:
                handle.write(dst.read_bytes())
        if dst.exists():
            dst.write_bytes(content)
        else:
            with dst.open('xb') as handle:
                handle.write(content)
        if digest(dst) != expected:
            raise ValueError('Write verification failed')
    return len(writes)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    default_home = os.environ.get('HERMES_HOME') or str(Path(os.environ.get('LOCALAPPDATA', '.')) / 'hermes')
    cli.add_argument('--profiles', type=Path, default=Path(default_home) / 'profiles')
    cli.add_argument('--apply', type=Path, help='Reviewed JSON plan; explicit replace decisions')
    args = cli.parse_args()
    repo, profiles = args.repo.resolve(), args.profiles.resolve()
    if args.apply:
        count = apply(json.loads(args.apply.read_text(encoding='utf-8-sig')), repo, profiles)
        print(f'SYNCED {count} files; start new sessions to load; config/models untouched')
    else:
        print(json.dumps(plan(repo, profiles), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        sys.exit(2)
