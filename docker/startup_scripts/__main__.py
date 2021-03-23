#!/usr/bin/env python3

import runpy
import os

from distutils.util import strtobool
from os.path import dirname, abspath

this_dir = dirname(abspath(__file__))
skip_startup_scripts = bool(strtobool(os.environ.get('SKIP_STARTUP_SCRIPTS', "false")))

def filename(f):
  return f.name

with os.scandir(this_dir) as it:
  for f in sorted(it, key = filename):
    if not f.is_file():
      continue

    if f.name.startswith('__'):
      continue

    if not f.name.endswith('.py'):
      continue

    if skip_startup_scripts and "required" not in f.name:
      continue

    print(f"▶️ Running the startup script {f.path}")
    try:
      runpy.run_path(f.path)
    except SystemExit as e:
      if e.code is not None and e.code != 0:
        print(f"‼️ The startup script {f.path} returned with code {e.code}, exiting.")
        raise
