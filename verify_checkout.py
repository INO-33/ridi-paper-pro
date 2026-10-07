#!/usr/bin/env python3
"""Verify actual project HEADs against the pinned manifest without building."""
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

manifest = Path(__file__).resolve().parent / 'default.xml'
source = Path(sys.argv[1]).resolve()
errors = []
projects = ET.parse(manifest).getroot().findall('project')
for project in projects:
    relative = project.get('path', project.get('name'))
    result = subprocess.run(['git', '-C', str(source / relative), 'rev-parse', 'HEAD'],
                            capture_output=True, text=True)
    if result.returncode or result.stdout.strip() != project.get('revision'):
        errors.append(relative)
if errors:
    raise SystemExit('Missing or mismatched project revisions: ' + ', '.join(errors))
print('Verified ' + str(len(projects)) + ' exact Android project commits')
