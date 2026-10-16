#!/usr/bin/env python3
"""Check onboarding prerequisites without building or changing system configuration."""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('profile', choices=['source', 'android', 'webview', 'sd'])
parser.add_argument('workspace', type=Path)
parser.add_argument('--min-free-gb', type=int, default=100, help='Free space floor, not an estimate of total build size')
parser.add_argument('--json', type=Path, help='Save detailed check results')
args = parser.parse_args()
workspace = args.workspace.expanduser().resolve()
checks = []
def check(name, ok, detail):
    checks.append(dict(name=name, ok=bool(ok), detail=detail))
def execute(name, command, env=None, expected=None):
    try:
        result = subprocess.run(command, capture_output=True, text=True, env=env, timeout=45)
        output = (result.stdout + result.stderr).strip()
        check(name, result.returncode == 0 and (expected is None or expected in output), output[-1500:] or f'exit status {result.returncode}')
    except (OSError, subprocess.TimeoutExpired) as error:
        check(name, False, str(error))

check('platform', sys.platform == 'linux' and platform.machine() == 'x86_64', 'Linux x86-64 required for Android/WebView host tools')
release = platform.freedesktop_os_release() if sys.platform == 'linux' else {}
check('host OS', (release.get('ID'), release.get('VERSION_ID')) == ('ubuntu', '24.04'), 'Documented host: Ubuntu 24.04 amd64; other distributions need their own dependency mapping')
check('Python 3', sys.version_info >= (3, 10), sys.version.split()[0])
check('workspace path', not any(c.isspace() for c in str(workspace)), 'Use a workspace path without whitespace')
parent = workspace
while not parent.exists():
    parent = parent.parent
free = shutil.disk_usage(parent).free / 1024**3
check('free disk', free >= args.min_free_gb, f'{free:.1f} GiB available; configured minimum {args.min_free_gb} GiB')
try:
    with tempfile.TemporaryDirectory(prefix='.ridi-fs-check-', dir=parent) as temp:
        probe = Path(temp) / 'CaseProbe'
        probe.write_text('check')
        check('case-sensitive filesystem', not (Path(temp) / 'caseprobe').exists(), str(parent))
        (Path(temp) / 'link').symlink_to(probe)
        check('symlinks', (Path(temp) / 'link').read_text() == 'check', str(parent))
except OSError as error:
    check('writable filesystem', False, str(error))
config = json.loads(Path(__file__).with_name('host-packages.json').read_text())
profiles = ['source'] + (['android'] if args.profile in ('android', 'webview') else [args.profile])
packages = sorted({p for profile in profiles for p in config['profiles'][profile]})
if shutil.which('dpkg-query'):
    missing = []
    for package in packages:
        result = subprocess.run(['dpkg-query', '-W', '-f=${Architecture} ${Status}\n', package], capture_output=True, text=True)
        installed = any(line in ('amd64 install ok installed', 'all install ok installed') for line in result.stdout.splitlines())
        if result.returncode or not installed:
            missing.append(package)
    check('host packages', not missing, 'Missing: ' + ' '.join(missing) if missing else 'Declared package set installed')
else:
    check('host packages', False, 'dpkg-query missing')
for command in ['git', 'curl', 'python3', 'dpkg-deb']:
    check('command ' + command, shutil.which(command), 'Required executable: ' + command)

source = workspace / 'android-sources/nxp-o8.0.0_1.0.0-ga'
support = source / 'ridi-build-support'
if args.profile in ('android', 'webview'):
    env = dict(os.environ, ANDROID_BUILD_TOP=str(source))
    jdk = support / 'host-tools/jdk8-local/usr/lib/jvm/java-8-openjdk-amd64'
    env['PATH'] = str(support / 'host-tools/android8-bin') + os.pathsep + str(jdk / 'bin') + os.pathsep + os.environ['PATH']
    compat = workspace / 'host-compat'
    env['RIDI_HOST_COMPAT'] = str(compat)
    env['RIDI_WORKSPACE'] = str(workspace)
    env['LD_LIBRARY_PATH'] = os.pathsep.join([str(compat / 'lib/x86_64-linux-gnu'), str(compat / 'usr/lib/x86_64-linux-gnu'), os.environ.get('LD_LIBRARY_PATH', '')])
    for library in ['libtinfo.so.5', 'libncurses.so.5']:
        check(library, any((compat / prefix / library).is_file() for prefix in ['lib/x86_64-linux-gnu', 'usr/lib/x86_64-linux-gnu']), 'Run prepare-host-libs.py for this workspace')
    execute('Java 8 compiler', [str(jdk / 'bin/javac'), '-version'], expected='1.8.')
    check('complete Python 2', (compat / 'usr/bin/python2.7').is_file(), 'Run prepare-host-libs.py; AOSP fallback lacks SSL')
    execute('Python 2 runtime', [str(support / 'host-tools/android8-bin/python'), '-c', 'import sys, ssl, zlib, ctypes, sqlite3, readline; print(sys.version); print(ssl.OPENSSL_VERSION)'], env=env, expected='2.7.')
    compiler = source / 'prebuilts/gcc/linux-x86/arm/arm-linux-androideabi-4.9/bin/arm-linux-androideabi-gcc'
    execute('ARM compiler', [str(compiler), '--version'], env=env)
    for version in ['clang-3289846', 'clang-4053586']:
        clang = source / 'prebuilts/clang/host/linux-x86' / version / 'bin/clang'
        execute(version, [str(clang), '--version'], env=env)
    for item in ['build/envsetup.sh', 'device/ridi/e70q10/AndroidProducts.mk']:
        check(item, (source / item).is_file(), str(source / item))
if args.profile == 'webview':
    execute('Docker daemon', ['docker', 'info', '--format', '{{.OSType}}'], expected='linux')
if args.profile == 'sd':
    execute('Tk import', [sys.executable, '-c', 'import tkinter; print(tkinter.TkVersion)'])
    for command in ['fastboot', 'mkfs.vfat', 'lsblk']:
        check('command ' + command, shutil.which(command), 'Required for SD/device operations; no device accessed')
if args.json:
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(dict(profile=args.profile, workspace=str(workspace), checks=checks), indent=2) + '\n')
failures = [c for c in checks if not c['ok']]
print(f'{args.profile}: {len(checks)-len(failures)}/{len(checks)} prerequisite checks passed')
for failure in failures:
    print(f"FAIL {failure['name']}: {failure['detail']}", file=sys.stderr)
sys.exit(bool(failures))
