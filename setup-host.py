#!/usr/bin/env python3
"""Print Ubuntu package setup, or install only with explicit --install."""
import argparse
import json
import platform
import shlex
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--profile', choices=['source', 'android', 'webview', 'sd', 'all'], default='android')
parser.add_argument('--install', action='store_true', help='Run sudo apt-get update/install; default only prints commands')
args = parser.parse_args()
config = json.loads(Path(__file__).with_name('host-packages.json').read_text())
profiles = ['source'] + (['android', 'sd', 'webview'] if args.profile == 'all' else [args.profile])
packages = sorted({p for profile in profiles for p in config['profiles'][profile]})
commands = [['sudo', 'apt-get', 'update'], ['sudo', 'apt-get', 'install', '--no-install-recommends', *packages]]
if args.install:
    os_release = platform.freedesktop_os_release()
    if (os_release.get('ID'), os_release.get('VERSION_ID'), platform.machine()) != ('ubuntu', '24.04', 'x86_64'):
        parser.error('--install supports Ubuntu 24.04 amd64 only; review printed commands for other hosts')
    for command in commands:
        subprocess.run(command, check=True)
else:
    for command in commands:
        print(shlex.join(command))
if args.profile in ('all', 'webview'):
    print('WebView also needs a working Docker daemon: https://docs.docker.com/engine/install/ubuntu/')
