#!/usr/bin/env python3
"""Verify a git tag matches the built wheel's version before publishing.

Usage: verify_release_tag.py <git-ref-or-tag> <wheel>

Normalizes the tag (strips a leading 'v' and PEP 440-normalizes it, so v4.7.0-beta1
becomes 4.7.0b1) and asserts it equals the wheel's Version metadata.
"""

import sys
import zipfile
from email.parser import Parser

from packaging.version import Version


def wheel_version(wheel_path):
    with zipfile.ZipFile(wheel_path) as archive:
        meta_name = next(name for name in archive.namelist() if name.endswith('.dist-info/METADATA'))
        metadata = Parser().parsestr(archive.read(meta_name).decode())
    return metadata['Version']


def normalize_tag(ref):
    tag = ref.rsplit('/', 1)[-1]
    if tag.startswith('v'):
        tag = tag[1:]
    return str(Version(tag))


def main(argv):
    if len(argv) != 3:
        print('usage: verify_release_tag.py <git-ref-or-tag> <wheel>')
        return 2
    tag_version = normalize_tag(argv[1])
    built_version = str(Version(wheel_version(argv[2])))
    if tag_version != built_version:
        print(f'Tag/version mismatch: tag -> {tag_version}, wheel -> {built_version}')
        return 1
    print(f'OK: tag matches wheel version ({built_version})')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
