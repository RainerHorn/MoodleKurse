"""Render the subject-specialist SOUL files from one template. Default: check only."""
import argparse
import json
from pathlib import Path
import re
import sys

SHARED = Path('agents') / '_shared' / 'fach'


def render(repo):
    """Return {relative SOUL path: text} for every role in rollen.json."""
    template = (repo / SHARED / 'SOUL.template.md').read_bytes().decode('utf-8')
    roles = json.loads((repo / SHARED / 'rollen.json').read_text(encoding='utf-8'))['rollen']
    result = {}
    for role, values in sorted(roles.items()):
        if not re.fullmatch(r'[a-z][a-z0-9-]*', role):
            raise ValueError('Invalid role name: ' + role)
        block = '\n'.join(values['schwerpunkte'])
        fields = {'titel': values['titel'], 'beruf': values['beruf'], 'ordner': values['ordner'],
                  'schwerpunkte': '\n' + block + '\n' if block else ''}
        text = template
        for key, value in fields.items():
            text = text.replace('{{' + key + '}}', value)
        if re.search(r'\{\{[a-z_]+\}\}', text):
            raise ValueError('Unresolved placeholder for ' + role)
        result['agents/' + role + '/SOUL.md'] = text
    return result


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    cli.add_argument('--write', action='store_true', help='Write differing SOUL files (Git is the backup)')
    args = cli.parse_args()
    drift = []
    for relative, text in render(args.repo).items():
        path = args.repo / relative
        current = path.read_bytes().decode('utf-8') if path.exists() else None
        if current == text:
            continue
        drift.append(relative)
        if args.write:
            if not path.parent.is_dir():
                raise ValueError('Role folder missing: ' + relative)
            path.write_bytes(text.encode('utf-8'))
    for relative in drift:
        print(('WRITTEN ' if args.write else 'DRIFT ') + relative)
    if not drift:
        print('SAME all subject SOUL files')
    return 0 if args.write or not drift else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        sys.exit(2)
