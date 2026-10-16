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
source_tree = support.parent
root = workspace / 'chromium-m58'
depot = workspace / 'depot_tools'
if root.exists() or depot.exists():
    raise SystemExit('Chromium/depot_tools destination exists; refusing to modify it')
environment = json.loads((support / 'host-environment.json').read_text())
logs = workspace / '.orchestrator/logs'
logs.mkdir(parents=True, exist_ok=True)
def report_failure(kind, error, traceback):
    import traceback as tb
    with (logs / 'chromium-source-prepare.log').open('a') as output:
        tb.print_exception(kind, error, traceback, file=output)
    print('Chromium preparation failed; log: ' + str(logs / 'chromium-source-prepare.log'), file=sys.stderr)
sys.excepthook = report_failure
# gclient is Python 3/vpython3 at the pinned depot_tools revision. Historical
# M58 hooks also invoke `python`; supply the restored Python 2 wrapper explicitly.
env = dict(os.environ, DEPOT_TOOLS_UPDATE='0', ANDROID_BUILD_TOP=str(source_tree))
env['RIDI_WORKSPACE'] = str(workspace)
env['RIDI_HOST_COMPAT'] = str(workspace / 'host-compat')
env['JAVA_HOME'] = str(support / 'host-tools/jdk8-local/usr/lib/jvm/java-8-openjdk-amd64')
env['LD_LIBRARY_PATH'] = os.pathsep.join([str(workspace / 'host-compat/lib/x86_64-linux-gnu'),
                                        str(workspace / 'host-compat/usr/lib/x86_64-linux-gnu'),
                                        os.environ.get('LD_LIBRARY_PATH', '')])
env['PATH'] = os.pathsep.join([str(depot), str(support / 'host-tools/android8-bin'),
                             str(Path(env['JAVA_HOME']) / 'bin'), os.environ['PATH']])
with (logs / 'chromium-source-prepare.log').open('w') as log:
    def run(args, **kwargs):
        subprocess.run(args, stdout=log, stderr=subprocess.STDOUT, check=True, **kwargs)
    run(['python3', str(manifest / 'check-host.py'), 'webview', str(workspace),
         '--min-free-gb', os.environ.get('RIDI_MIN_FREE_GB', '100'),
         '--json', str(logs / 'host-webview.json')])
    root.mkdir(parents=True)
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
    # The RIDI dependency changes are bundled inside the main Chromium repo.
    for row in lock['chromium_dependency_changes']:
        overrides[row['path']] = row['upstream_url'] + '@' + row['base_commit']
    config = "target_os = ['android']\ntarget_os_only = True\nsolutions = " + repr([{
        'name': 'src', 'url': source['url'] + '@' + source['commit'], 'deps_file': 'DEPS',
        'managed': False, 'custom_deps': overrides, 'custom_vars': {},
    }]) + '\n'
    (root / '.gclient').write_text(config)
    run([str(depot / 'gclient'), 'sync', '--no-history'], cwd=root, env=env)
    run(['python3', str(root / 'src/ridi-dependencies/apply.py'), str(root)])
print('Chromium source restored; log: ' + str(logs / 'chromium-source-prepare.log'))
