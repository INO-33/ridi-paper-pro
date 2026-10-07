#!/usr/bin/env python3
"""Prepare a new M58 checkout including modified breakpad/SwiftShader sources."""
import json
import os
from pathlib import Path
import subprocess
import sys

manifest = Path(__file__).resolve().parent
lock = json.loads((manifest / 'release-lock.json').read_text())
workspace = Path(sys.argv[1]).resolve()
support = workspace / 'android-sources/nxp-o8.0.0_1.0.0-ga/ridi-build-support'
root = workspace / 'chromium-m58'
depot = workspace / 'depot_tools'
if root.exists() or depot.exists():
    raise SystemExit('Chromium/depot_tools destination exists; refusing to modify it')
environment = json.loads((support / 'host-environment.json').read_text())
root.mkdir(parents=True)
logs = workspace / '.orchestrator/logs'
logs.mkdir(parents=True, exist_ok=True)
with (logs / 'chromium-source-prepare.log').open('w') as log:
    def run(args, **kwargs):
        subprocess.run(args, stdout=log, stderr=subprocess.STDOUT, check=True, **kwargs)
    run(['git', 'clone', '--no-checkout', '--depth=1',
         'https://chromium.googlesource.com/chromium/tools/depot_tools.git', str(depot)])
    run(['git', '-C', str(depot), 'fetch', '--depth=1', 'origin', environment['depot_tools_commit']])
    run(['git', '-C', str(depot), 'checkout', '--detach', environment['depot_tools_commit']])
    source = next(r for r in lock['source_repositories'] if r['path'] == 'chromium')
    overrides = {
        'src/third_party/WebKit/Source/devtools/devtools-node-modules': None,
        'src/third_party/swiftshader/third_party/pnacl-subzero':
            'https://chromium.googlesource.com/native_client/pnacl-subzero@c48bb8b02c98ae49438e43aa1143a958784822a5',
    }
    for row in lock['source_repositories']:
        if row['path'].startswith('chromium-deps/'):
            overrides[row['path'].removeprefix('chromium-deps/')] = row['url'] + '@' + row['commit']
    config = "target_os = ['android']\ntarget_os_only = True\nsolutions = " + repr([{
        'name': 'src', 'url': source['url'] + '@' + source['commit'], 'deps_file': 'DEPS',
        'managed': False, 'custom_deps': overrides, 'custom_vars': {},
    }]) + '\n'
    (root / '.gclient').write_text(config)
    env = os.environ | {'DEPOT_TOOLS_UPDATE': '0', 'PATH': str(depot) + os.pathsep + os.environ['PATH']}
    run([str(depot / 'gclient'), 'sync', '--no-history'], cwd=root, env=env)
print('Chromium source restored; log: ' + str(logs / 'chromium-source-prepare.log'))
