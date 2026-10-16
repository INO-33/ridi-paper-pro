#!/usr/bin/env python3
"""Extract pinned Ubuntu legacy host libraries into a workspace, without sudo."""
import argparse
import hashlib
import json
import os
import platform
import subprocess
import tempfile
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('workspace', type=Path)
args = parser.parse_args()
if platform.system() != 'Linux' or platform.machine() != 'x86_64':
    parser.error('Linux x86-64 required')
workspace = args.workspace.expanduser().resolve()
workspace.mkdir(parents=True, exist_ok=True)
destination = workspace / 'host-compat'
packages = json.loads(Path(__file__).with_name('legacy-libraries.json').read_text())
marker = destination / '.ridi-libraries.json'
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
if destination.exists():
    if not marker.is_file():
        raise SystemExit('Refusing to overwrite unmanaged host-compat directory')
    state = json.loads(marker.read_text())
    if state['packages'] != packages or any(digest(destination / p) != h for p, h in state['files'].items()):
        raise SystemExit('Existing host compatibility files differ; preserve and inspect the directory')
    print('Pinned host compatibility libraries verified')
else:
    with tempfile.TemporaryDirectory(prefix='.ridi-host-libs-', dir=workspace) as temp:
        stage = Path(temp) / 'root'
        stage.mkdir()
        for package in packages:
            archive = Path(temp) / (package['package'] + '.deb')
            subprocess.run(['curl', '--fail', '--location', '--silent', '--show-error',
                            '--retry', '3', '--connect-timeout', '20', '--max-time', '180',
                            '--output', str(archive), package['url']], check=True)
            if digest(archive) != package['sha256']:
                raise SystemExit('Ubuntu package SHA256 mismatch: ' + package['package'])
            subprocess.run(['dpkg-deb', '--extract', str(archive), str(stage)], check=True)
        files = {str(p.relative_to(stage)): digest(p) for p in sorted(stage.rglob('*')) if p.is_file()}
        for library in ['libtinfo.so.5', 'libncurses.so.5']:
            if not any(p.name == library and p.is_file() for p in stage.rglob(library)):
                raise SystemExit('Expected library missing from package: ' + library)
        if not (stage / 'usr/bin/python2.7').is_file():
            raise SystemExit('Complete Python 2 executable missing from packages')
        (stage / '.ridi-libraries.json').write_text(json.dumps(dict(packages=packages, files=files), indent=2) + '\n')
        os.rename(stage, destination)
    print('Pinned host compatibility libraries prepared without system installation')
