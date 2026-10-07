#!/usr/bin/env bash
set -euo pipefail
manifest="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
workspace="${1:?Usage: prepare.sh /absolute/path/to/new-workspace}"
[[ "$workspace" == /* ]] || { echo 'Use an absolute workspace path' >&2; exit 2; }
source_tree="$workspace/android-sources/nxp-o8.0.0_1.0.0-ga"
[[ ! -e "$source_tree" ]] || { echo 'Source destination already exists; refusing to modify it' >&2; exit 1; }
mkdir -p "$source_tree" "$workspace/.orchestrator/logs"
log="$workspace/.orchestrator/logs/source-prepare-$(date +%Y%m%d-%H%M%S).log"
if (
    cd "$source_tree"
    python3 "$manifest/bin/repo" init \
        -u https://github.com/INO-33/RIDI_ANDROID8_MANIFEST.git \
        -b source-snapshot-20261007 -m default.xml \
        --repo-url=https://gerrit.googlesource.com/git-repo \
        --repo-rev=35bbf701d04de5c6a71937279bc3d16f6ce36808 \
        --depth=1 --no-clone-bundle
    python3 "$manifest/bin/repo" sync -c -j"${RIDI_SYNC_JOBS:-4}" --no-clone-bundle
    python3 "$manifest/configure_workspace.py" "$workspace"
    python3 "$source_tree/ridi-build-support/verify_assets.py"
    python3 "$manifest/verify_checkout.py" "$source_tree"
) >"$log" 2>&1; then
    echo "Sources restored and checked. Run: source $workspace/env.sh"
    echo "Log: $log"
else
    echo "Source preparation needs attention. Log: $log" >&2
    tail -15 "$log" >&2
    exit 1
fi
