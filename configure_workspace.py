#!/usr/bin/env python3
"""Create portable workspace links without overwriting existing directories."""
from pathlib import Path
import shlex
import sys

workspace = Path(sys.argv[1]).resolve()
source = workspace / 'android-sources/nxp-o8.0.0_1.0.0-ga'
support = source / 'ridi-build-support'
sd_tools = source / 'ridi-sd-tools'
if not (support / 'build.sh').is_file():
    raise SystemExit('Build support checkout is missing')
if not (sd_tools / 'verify_assets.py').is_file():
    raise SystemExit('SD tools checkout is missing')
for name in ['host-tools', 'tools', 'porting', 'scripts']:
    destination = workspace / name
    target = (sd_tools if name == 'porting' else support) / name
    if destination.exists() or destination.is_symlink():
        if destination.is_symlink() and destination.resolve() == target.resolve():
            continue
        raise SystemExit('Refusing to overwrite existing workspace path: ' + str(destination))
    destination.symlink_to(target, target_is_directory=True)
for name in ['android-out', 'deliverables', '.orchestrator/logs']:
    (workspace / name).mkdir(parents=True, exist_ok=True)
env = workspace / 'env.sh'
content = '\n'.join([
    'export RIDI_WORKSPACE=' + shlex.quote(str(workspace)),
    'export RIDI_MANIFEST_DIR=' + shlex.quote(str(Path(__file__).resolve().parent)),
    'export ANDROID_BUILD_TOP=' + shlex.quote(str(source)),
    'export JAVA_HOME=' + shlex.quote(str(support / 'host-tools/jdk8-local/usr/lib/jvm/java-8-openjdk-amd64')),
    'export RIDI_ANDROID8_TOOL_BIN=' + shlex.quote(str(support / 'host-tools/android8-bin')),
    'export CHROMIUM_SRC_ROOT=' + shlex.quote(str(workspace / 'chromium-m58/src')),
    'export DEPOT_TOOLS_ROOT=' + shlex.quote(str(workspace / 'depot_tools')),
    'export RIDI_HOST_COMPAT=' + shlex.quote(str(workspace / 'host-compat')),
    'export LD_LIBRARY_PATH="$RIDI_HOST_COMPAT/lib/x86_64-linux-gnu:$RIDI_HOST_COMPAT/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"',
    'export PATH="$RIDI_ANDROID8_TOOL_BIN:$JAVA_HOME/bin:$PATH"',
    '',
])
if env.exists() and env.read_text() != content:
    raise SystemExit('Refusing to overwrite different env.sh: ' + str(env))
env.write_text(content)
print('Portable workspace configured')
