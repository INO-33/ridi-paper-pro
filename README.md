# RIDI Android 8 — six repositories

Checkpoint: `consolidated-20261007`. Owner: `INO-33`. All six repositories private.

| Repository | Purpose |
|---|---|
| RIDI_ANDROID8_MANIFEST | Pinned source combination, preparation and verification |
| RIDI_PAPER_PRO_ANDROID8 | Kernel and RIDI drivers |
| RIDI_PAPER_PRO_ANDROID8_DEVICE | Device settings, apps and required device assets |
| RIDI_ANDROID8_CHANGES | One package for 23 modified Android projects |
| RIDI_CHROMIUM_M58 | WebView source plus its Breakpad/SwiftShader change package |
| RIDI_ANDROID8_BUILD_TOOLS | Host assets, build scripts and updater producer |

The earlier 25 individual repositories are read-only archives. They are backups,
not dependencies of this checkpoint. Earlier source branches/tags remain intact.

## Restore Android

On Linux x86-64 with Git, Python 3, GitHub CLI and sufficient disk/RAM:

```sh
gh auth setup-git
gh repo clone INO-33/RIDI_ANDROID8_MANIFEST
cd RIDI_ANDROID8_MANIFEST
./prepare.sh /absolute/path/to/new-ridi-workspace
source /absolute/path/to/new-ridi-workspace/env.sh
"$ANDROID_BUILD_TOP/ridi-build-support/build.sh" check e70q10_reference-eng
"$ANDROID_BUILD_TOP/ridi-build-support/build.sh" build e70q10_reference-eng
```

The prepare script fetches immutable upstream Android revisions, the separate
RIDI kernel/device repositories, build support and the Android change package.
It applies the changes and checks complete Git tree hashes against the previous
source snapshots. Binary resources, executable modes and deletions are included.
Restored projects get detached local checkpoint commits; upstream refs are kept.
Existing/modified destinations are refused. No reset, clean or flash is performed.
Logs are in the workspace's `.orchestrator/logs`.

The host package inventory and materialized Java 8 runtime are in build support.
Emulator products: `e70q10_emulator-eng`, `e70q10_emulator_armv7-eng`.

## Restore WebView sources

Android uses the preserved device-local WebView APK; its SHA256 is pinned.
To separately restore the current M58 source checkpoint:

```sh
python3 prepare-chromium.py "$RIDI_WORKSPACE"
CHROMIUM_SRC_ROOT="$RIDI_WORKSPACE/chromium-m58/src" \
DEPOT_TOOLS_ROOT="$RIDI_WORKSPACE/depot_tools" \
"$RIDI_WORKSPACE/tools/chromium-m58-build/build_m58_xenial_arm.sh"
```

Preparation fetches pinned upstream dependencies and applies the Breakpad and
SwiftShader package from `RIDI_CHROMIUM_M58/ridi-dependencies`.
Docker is required; x86 uses `build_m58_xenial_x86.sh`.
The APK's match to a rebuild of these sources remains unverified.

## Validation and remaining work

The 23 Android and two Chromium dependency packages reconstruct the same Git
source trees as the previous snapshots. Archived repositories are not required.
The Chromium product source is unchanged by this reorganization.

No full Android/Chromium build in a new environment or physical validation was
run. Unmodified upstream sources, Chromium DEPS downloads and native/container
packages still require long-term mirroring and environment validation. Deleting
original sources should wait for full reconstruction/build validation.
Historical initial-installer scripts retain old backup/output references;
the updater owns its required assets.
