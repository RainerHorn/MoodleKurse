"""Version 1: byte-preserving Moodle XML category removal; local files only."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from xml.parsers import expat


def derive(data):
    data.decode('utf-8-sig')
    parser = expat.ParserCreate()
    stack, spans = [], []
    category_start = None
    category_empty_end = None

    def reject(*_):
        raise ValueError('DTD/entities are not supported')

    def start(name, attrs):
        nonlocal category_start, category_empty_end
        if not stack and name != 'quiz':
            raise ValueError('Expected quiz root')
        if len(stack) == 1:
            if name != 'question':
                raise ValueError('Only question children supported')
            if attrs.get('type') == 'category':
                category_start = parser.CurrentByteIndex
                tag = re.match(rb'''<question\b(?:[^>"']|"[^"]*"|'[^']*')*>''', data[category_start:])
                if tag is None:
                    raise ValueError('Unsupported category tag')
                category_empty_end = category_start + tag.end() if tag[0].endswith(b'/>') else None
        stack.append(name)

    def end(name):
        nonlocal category_start
        if len(stack) == 2 and category_start is not None:
            end_at = category_empty_end if category_empty_end is not None else parser.CurrentByteIndex
            # Expat points after '/>' for empty elements, at '</' otherwise.
            if category_empty_end is None and data[end_at:end_at + 2] == b'</':
                end_at = data.index(b'>', end_at) + 1
            begin = category_start
            line_start = data.rfind(b'\n', 0, begin) + 1
            if data[line_start:begin].strip() == b'':
                trailing = re.match(rb'[ \t]*(?:\r?\n)', data[end_at:])
                if trailing:
                    begin, end_at = line_start, end_at + trailing.end()
            spans.append((begin, end_at))
            category_start = None
        stack.pop()

    parser.StartElementHandler = start
    parser.EndElementHandler = end
    parser.StartDoctypeDeclHandler = reject
    parser.EntityDeclHandler = reject
    parser.Parse(data, True)
    result = data
    for begin, end_at in reversed(spans):
        result = result[:begin] + result[end_at:]
    return result, len(spans)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('source', type=Path)
    cli.add_argument('target', type=Path)
    cli.add_argument('--derive', action='store_true', help='Create only; never overwrite')
    cli.add_argument('--source-sha256', help='Optional approved source binding')
    args = cli.parse_args()
    source = args.source.read_bytes()
    digest = hashlib.sha256(source).hexdigest()
    if args.source_sha256 and args.source_sha256 != digest:
        raise ValueError('Source hash mismatch')
    expected, count = derive(source)
    if args.derive:
        with args.target.open('xb') as output:
            output.write(expected)
    if args.target.read_bytes() != expected:
        raise ValueError('Target differs beyond category removal')
    print(json.dumps({'status': 'PASS', 'categories_removed': count,
                      'source_sha256': digest,
                      'target_sha256': hashlib.sha256(expected).hexdigest()}))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, expat.ExpatError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        sys.exit(2)
