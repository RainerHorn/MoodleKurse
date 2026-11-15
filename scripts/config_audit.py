"""Read-only audit of the project's simple Hermes YAML subset; never prints secrets."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys


def block(text, key, indent):
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if re.fullmatch(' ' * indent + re.escape(key) + r':\s*(?:#.*)?', line)]
    if len(starts) != 1:
        raise ValueError('Missing/ambiguous block: ' + key)
    result = []
    for line in lines[starts[0] + 1:]:
        if line.strip() and not line.lstrip().startswith('#') and len(line) - len(line.lstrip()) <= indent:
            break
        result.append(line)
    return '\n'.join(result)


def scalar(text, key, indent):
    values = re.findall('^' + ' ' * indent + re.escape(key) + r':\s*(.+?)\s*$', text, re.M)
    if len(values) != 1:
        raise ValueError('Missing/ambiguous scalar: ' + key)
    value = values[0]
    if value.startswith('"'):
        return json.loads(value)
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    if any(ch in value for ch in '#&*!{}[]'):
        raise ValueError('Unsupported scalar syntax: ' + key)
    return value


def subset(text):
    if '\t' in text or re.search(r'^\s*(?:<<:|---|\.\.\.)', text, re.M):
        raise ValueError('Unsupported YAML structure')
    moodle = block(block(text, 'mcp_servers', 0), 'moodle', 2)
    arguments = block(moodle, 'args', 4)
    raw_args = [line.strip()[2:] for line in arguments.splitlines()
                if line.strip() and not line.lstrip().startswith('#')]
    if len(raw_args) != 1:
        raise ValueError('Expected one MCP script argument')
    script = scalar('x: ' + raw_args[0], 'x', 0)
    policy = block(moodle, 'tools', 4)
    include = block(policy, 'include', 6)
    allowed = []
    for line in include.splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        match = re.fullmatch(r'        - (moodle_[a-z_]+)\s*', line)
        if not match:
            raise ValueError('Unsupported allowlist syntax')
        allowed.append(match[1])
    if not allowed or len(allowed) != len(set(allowed)) or 'moodle_delete_module' in allowed:
        raise ValueError('Empty/duplicate/forbidden allowlist')
    # Unknown include-policy overrides must not silently pass this narrow audit.
    other = re.findall(r'^      (\w+):', policy, re.M)
    if any(key not in ('include', 'resources', 'prompts') for key in other):
        raise ValueError('Unsupported tool policy')
    return {'command': scalar(moodle, 'command', 4), 'script': script.replace('\\', '/').lower(),
            'tools': sorted(allowed),
            'cwd': scalar(block(text, 'terminal', 0), 'cwd', 2).replace('\\', '/').lower()}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    repo = Path(__file__).resolve().parents[1]
    cli.add_argument('--template', type=Path, default=repo / 'agents/moodle-mcp/config.template.yaml')
    cli.add_argument('--profile', default='moodle-mcp', help='Hermes profile that holds the Moodle MCP server')
    default_home = os.environ.get('HERMES_HOME') or str(Path(os.environ.get('LOCALAPPDATA', '.')) / 'hermes')
    cli.add_argument('--profiles', type=Path, default=Path(default_home) / 'profiles')
    args = cli.parse_args()
    wanted = subset(args.template.read_text(encoding='utf-8-sig'))
    actual = subset((args.profiles / args.profile / 'config.yaml').read_text(encoding='utf-8-sig'))
    matches = {key: actual[key] == wanted[key] for key in wanted}
    other_moodle_profiles = []
    for config in args.profiles.glob('*/config.yaml'):
        if config.parent.name == args.profile:
            continue
        value = config.read_text(encoding='utf-8-sig')
        if re.search(r'^\s*moodle:\s*$', value, re.M) or 'moodle-mcp.js' in value:
            other_moodle_profiles.append(config.parent.name)
    script = Path(wanted['script'])
    print(json.dumps({'scope': 'command/script/allowlist/cwd only; not effective runtime or server version',
                      'matches': matches, 'other_moodle_profiles': other_moodle_profiles,
                      'local_script_sha256': hashlib.sha256(script.read_bytes()).hexdigest() if script.is_file() else None}, indent=2))
    return 0 if all(matches.values()) and not other_moodle_profiles else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError):
        print('ERROR: Missing file or unsupported/ambiguous configuration; inspect locally without exposing secrets.', file=sys.stderr)
        sys.exit(2)
