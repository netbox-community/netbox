#!/usr/bin/env python3
"""Render a release's notes from docs/release-notes/ as the body of its GitHub PR or release."""

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

# MkDocs admonition type (including Material's aliases) -> GitHub alert type
ALERTS = {
    'attention': 'WARNING',
    'bug': 'CAUTION',
    'caution': 'WARNING',
    'danger': 'CAUTION',
    'error': 'CAUTION',
    'failure': 'CAUTION',
    'hint': 'TIP',
    'important': 'IMPORTANT',
    'info': 'NOTE',
    'note': 'NOTE',
    'tip': 'TIP',
    'warning': 'WARNING',
}


def extract_section(text, version):
    """Return the lines of the section for the given version, excluding its heading."""
    lines = text.splitlines()
    heading = re.compile(rf'^## v{re.escape(version)} \(')
    start = next((i for i, line in enumerate(lines) if heading.match(line)), None)
    if start is None:
        raise SystemExit(f'No section for v{version} found')
    section = []
    for line in lines[start + 1:]:
        if line == '---' or line.startswith('## '):
            break
        section.append(line)
    return section


def convert_admonitions(lines):
    """Convert MkDocs admonitions to GitHub alerts. GitHub alerts have no title, so it is dropped."""
    output = []
    i = 0
    while i < len(lines):
        if not (match := re.match(r'^!!! (\w+)', lines[i])):
            output.append(lines[i])
            i += 1
            continue
        output.append(f'> [!{ALERTS.get(match[1], "NOTE")}]')
        i += 1
        # The body is every following line indented four spaces, including blank lines between paragraphs
        end = i
        while end < len(lines) and (lines[end].startswith('    ') or not lines[end].strip()):
            end += 1
        while end > i and not lines[end - 1].strip():
            end -= 1
        output.extend(f'> {line[4:]}' if line.strip() else '>' for line in lines[i:end])
        i = end
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('version', help='Release version, e.g. 4.7.5')
    parser.add_argument('--format', choices=('pr', 'release'), default='pr')
    args = parser.parse_args()

    version = args.version.removeprefix('v')
    major, minor = version.split('.')[:2]
    text = (ROOT / 'docs' / 'release-notes' / f'version-{major}.{minor}.md').read_text()

    lines = convert_admonitions(extract_section(text, version))
    if args.format == 'release':
        # Promote each heading one level (### -> ##)
        lines = [re.sub(r'^#(#+ )', r'\1', line) for line in lines]

    print('\n'.join(lines).strip())


if __name__ == '__main__':
    main()
