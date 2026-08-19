#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Install the bundled "Merge Info" VS Code extension into this dev container.
#
# The extension reads merge-info.json from the workspace root and shows hover
# popups over each block students merge during the labs' `code -d` steps.
# It is not on the Marketplace, so it cannot go in devcontainer.json's
# customizations.vscode.extensions list - it has to be installed from the
# .vsix that ships in this folder.
#
# Safe to run more than once, and never fails the container build.
# ---------------------------------------------------------------------------
set -uo pipefail

log() { echo "[merge-info] $*"; }

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VSIX="$(ls -1 "$HERE"/merge-info-*.vsix 2>/dev/null | sort -V | tail -n 1)"

if [ -z "${VSIX:-}" ]; then
    log "no merge-info-*.vsix in $HERE - skipping"
    exit 0
fi

VERSION="$(basename "$VSIX" .vsix | sed 's/^merge-info-//')"
EXT_ID="techupskills.merge-info-${VERSION}"

# Where the VS Code server keeps user extensions (Codespaces vs. local Remote)
EXT_DIR=""
for d in "$HOME/.vscode-remote/extensions" "$HOME/.vscode-server/extensions"; do
    if [ -d "$d" ]; then EXT_DIR="$d"; break; fi
done
[ -n "$EXT_DIR" ] || EXT_DIR="$HOME/.vscode-remote/extensions"
mkdir -p "$EXT_DIR"

# Already there - say nothing. This script can be re-run by hand at any time;
# silence on the no-op path keeps student terminals clean.
if compgen -G "$EXT_DIR/techupskills.merge-info-*" >/dev/null; then
    exit 0
fi

installed() { compgen -G "$EXT_DIR/techupskills.merge-info-*" >/dev/null; }

try_cli() {  # $1 = CLI path, remaining args passed through
    local cli="$1"; shift
    log "installing $(basename "$VSIX") with $cli"
    "$cli" --install-extension "$VSIX" --force "$@" 2>&1 | sed 's/^/[merge-info] /'
    installed
}

# 1) The server CLI - works with no editor window attached, which is the normal
#    situation during postCreateCommand.
for cli in \
    /vscode/bin/linux-*/*/bin/code-server \
    "$HOME"/.vscode-remote/bin/*/bin/code-server \
    "$HOME"/.vscode-server/bin/*/bin/code-server \
    "$HOME"/.vscode-server/cli/servers/*/server/bin/code-server ; do
    [ -x "$cli" ] || continue
    if try_cli "$cli" --extensions-dir "$EXT_DIR"; then
        log "installed into $EXT_DIR"
        exit 0
    fi
done

# 2) The plain `code` CLI - works when a window is already attached.
if command -v code >/dev/null 2>&1; then
    if try_cli "$(command -v code)"; then
        log "installed via code CLI"
        exit 0
    fi
fi

# 3) Last resort: unpack the .vsix into the extensions folder by hand. VS Code
#    scans that directory at startup, so the extension loads on next connect.
log "no VS Code CLI available - unpacking directly into $EXT_DIR"
TMP="$(mktemp -d)"
if command -v unzip >/dev/null 2>&1; then
    unzip -q "$VSIX" -d "$TMP"
else
    python3 -c "import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$VSIX" "$TMP"
fi

if [ -d "$TMP/extension" ]; then
    rm -rf "${EXT_DIR:?}/$EXT_ID"
    mv "$TMP/extension" "$EXT_DIR/$EXT_ID"
    rm -rf "$TMP"
    log "unpacked to $EXT_DIR/$EXT_ID"
else
    rm -rf "$TMP"
    log "FAILED to unpack $VSIX - merge popups will not be available"
    exit 0
fi

log "done - hover popups come from merge-info.json at the workspace root"
