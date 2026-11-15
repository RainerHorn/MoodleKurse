"""Version 1: replace href placeholders from explicit Moodle readback mappings."""
import argparse
import html
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

PLACEHOLDER = re.compile(r'__MOODLE_URL_([a-z0-9_]+)__')


def render(data, targets, origin):
    values = {}
    for key, item in targets.items():
        url = urlsplit(item['viewurl'])
        if (url.scheme not in ('http', 'https') or not url.netloc or
                url.scheme + '://' + url.netloc != origin or url.fragment or
                not re.fullmatch(r'/mod/[a-z]+/view\.php', url.path) or
                url.path != '/mod/' + item['modname'] + '/view.php' or
                not re.fullmatch(r'id=[1-9][0-9]*', url.query) or
                url.query != 'id=' + str(item['cmid']) or not item.get('source')):
            raise ValueError('Invalid readback mapping: ' + key)
        values[key] = html.escape(url.path + '?' + url.query, quote=True)
    text = data.decode('utf-8')

    def replace(match):
        key = match[2]
        if key not in values:
            raise ValueError('Missing target: ' + key)
        return match[1] + values[key] + match[3]

    output = re.sub(r'((?<![\w:-])href=")__MOODLE_URL_([a-z0-9_]+)__(")', replace, text)
    if '__MOODLE_URL_' in output:
        raise ValueError('Unresolved placeholder or placeholder outside supported href')
    return output.encode('utf-8')


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('source', type=Path)
    cli.add_argument('target', type=Path)
    cli.add_argument('--mapping', required=True, type=Path)
    cli.add_argument('--origin', required=True, help='Exact readback origin; root wwwroot only')
    cli.add_argument('--build', action='store_true', help='Create only, never overwrite')
    args = cli.parse_args()
    mapping = json.loads(args.mapping.read_text(encoding='utf-8-sig'))
    expected = render(args.source.read_bytes(), mapping['targets'], args.origin)
    if args.build:
        with args.target.open('xb') as output:
            output.write(expected)
    if args.target.read_bytes() != expected:
        raise ValueError('Output differs from href-only replacement')
    print('PASS href-only replacement; no live target/access check')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        sys.exit(2)
