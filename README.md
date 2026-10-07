# RIDI PAPER PRO Android 8 source checkpoint

Private checkpoint: `source-snapshot-20261007`, GitHub owner `INO-33`.
`default.xml` pins every Android project to an exact commit. `release-lock.json`
records the original source HEADs, exported commits and essential asset hashes.

## Restore Android sources

Authenticate GitHub CLI as INO-33 (or an authorized collaborator), configure Git
authentication with `gh auth setup-git`, and clone this manifest repository:

```sh
gh repo clone INO-33/RIDI_ANDROID8_MANIFEST
cd RIDI_ANDROID8_MANIFEST
./prepare.sh /absolute/path/to/new-ridi-workspace
source /absolute/path/to/new-ridi-workspace/env.sh
"$ANDROID_BUILD_TOP/ridi-build-support/build.sh" check e70q10_reference-eng
"$ANDROID_BUILD_TOP/ridi-build-support/build.sh" build e70q10_reference-eng
```

Requires Linux x86-64, Git, Python 3, GitHub access and sufficient disk/RAM for
Android sources and outputs. The original host was Ubuntu 24.04; its package
inventory, Java 8 runtime and portable Python 2 wrappers are in build support.
Host package installation is not automated or validated in a fresh environment.
The prepare command refuses an existing source destination and never flashes a
device. Build scripts write logs under the new workspace's `.orchestrator/logs`.
Emulator products are `e70q10_emulator-eng` and `e70q10_emulator_armv7-eng`.

## WebView source reconstruction

Android uses the preserved `device/ridi/e70q10/webview/SystemWebView.apk`.
Its hash is pinned, but a match to the current Chromium source was not verified.
To separately restore Chromium M58 and its two modified Git dependencies:

```sh
python3 prepare-chromium.py "$RIDI_WORKSPACE"
CHROMIUM_SRC_ROOT="$RIDI_WORKSPACE/chromium-m58/src" \
DEPOT_TOOLS_ROOT="$RIDI_WORKSPACE/depot_tools" \
"$RIDI_WORKSPACE/tools/chromium-m58-build/build_m58_xenial_arm.sh"
```

The analogous x86 script is `build_m58_xenial_x86.sh`. Docker is required.
The M58 source commit, depot_tools commit and dependency checkout inventory are
preserved. Upstream DEPS downloads and old Ubuntu package archives remain
external dependencies; the entire dependency ecosystem is not mirrored.

## History and completeness

The existing RIDI kernel/device repositories retain their parent history.
New private repositories contain an upstream-tree baseline followed by the RIDI
checkpoint commit. This avoids fetching enormous upstream histories from shallow
checkouts. Original upstream SHAs are recorded for comparison and provenance.
No existing source HEAD, branch, index or working file was reset or overwritten.
Temporary caches/backups and generated libxml2 Python MANIFEST were excluded.

This checkpoint preserves sources; it is **not** confirmation that a new machine
can already build the full product. No clean build, installation or physical
validation was performed. Unmodified AOSP/NXP repositories remain upstream,
so long-term upstream mirrors, fixed host package/image archives and a complete
fresh-environment build still need verification before deleting original sources.
Historical installer scripts are archived for reference; the updater producer
owns its required assets. Production signing keys and whole disk backups are not
included. Keep repositories private because device/stock assets are present.
