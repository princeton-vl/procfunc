#!/bin/bash
# Wrapper that locates the Blender 3.6 binary installed by
# install_blendergym_bl36.sh and forwards all arguments to it.
# The install layout differs per OS:
#   Linux:  ./blender_3_6/blender
#   macOS:  ./blender_3_6/Contents/MacOS/Blender (.app bundle)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

LINUX_BIN="${SCRIPT_DIR}/blender_3_6/blender"
MACOS_BIN="${SCRIPT_DIR}/blender_3_6/Contents/MacOS/Blender"

if [ -x "${LINUX_BIN}" ]; then
    BLENDER="${LINUX_BIN}"
elif [ -x "${MACOS_BIN}" ]; then
    BLENDER="${MACOS_BIN}"
else
    echo "Could not find Blender 3.6 binary under ${SCRIPT_DIR}/blender_3_6/." >&2
    echo "Run install_blendergym_bl36.sh first." >&2
    exit 1
fi

exec "${BLENDER}" "$@"
