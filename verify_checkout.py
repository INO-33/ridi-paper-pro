#!/usr/bin/env python3
"""Verify actual project HEADs against the pinned manifest without building."""
from pathlib import Path
import json
import subprocess
import sys
import xml.etree.ElementTree as ET

manifest = Path(__file__).resolve().parent / 'default.xml'
source = Path(sys.argv[1]).resolve()
errors = []
projects = ET.parse(manifest).getroot().findall('project')
package = source / 'ridi-android-changes/projects.json'
changes = {row['path']: row for row in json.loads(package.read_text())['projects']}
for project in projects:
    relative = project.get('path', project.get('name'))
    expression = 'HEAD^{tree}' if relative in changes else 'HEAD'
    expected = changes[relative]['result_tree'] if relative in changes else project.get('revision')
    result = subprocess.run(['git', '-C', str(source / relative), 'rev-parse', expression],
                            capture_output=True, text=True)
    if result.returncode or result.stdout.strip() != expected:
        errors.append(relative)
if errors:
    raise SystemExit('Missing or mismatched project revisions: ' + ', '.join(errors))
subprocess.run(['python3', str(package.parent / 'apply.py'), str(source), '--verify'], check=True)
print('Verified ' + str(len(projects)) + ' exact Android source revisions/trees')
