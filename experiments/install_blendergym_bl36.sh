#!/bin/bash
# Installs a headless Blender 3.6 into ./blender_3_6/ and installs
# BlenderGym's Infinigen v1.2.5 fork into its bundled Python.
#
# Adapted from blendergym/infinigen/scripts/install/interactive_blender.sh.
# The upstream script ends with `pip install -e .`, which pulls bpy==3.6.0
# and fails inside Blender's own Python. We use --no-deps +
# infinigen125_requirements.txt (pyproject.toml deps minus bpy) instead.

set -e

if ! command -v wget &> /dev/null; then
    echo "wget not found. Install with 'sudo apt-get install wget' or 'brew install wget'."
    exit 1
fi

INFINIGEN_DIR="blendergym/infinigen"
if [ ! -d "${INFINIGEN_DIR}" ]; then
    echo "Expected ${INFINIGEN_DIR} to exist. Run the git clone step from EXPERIMENTS.md first."
    exit 1
fi

BLENDER_DIR="blender_3_6"
OS=$(uname -s)
ARCH=$(uname -m)

if [ "${OS}" = "Linux" ]; then
    BLENDER_WGET_LINK='https://download.blender.org/release/Blender3.6/blender-3.6.0-linux-x64.tar.xz'
    BLENDER_WGET_FILE='blender.tar.xz'
    BLENDER_UNTAR_DIR='blender-3.6.0-linux-x64'
    BLENDER_PYTHON="${BLENDER_DIR}/3.6/python/bin/python3.10"
elif [ "${OS}" = "Darwin" ]; then
    if [ "${ARCH}" = "arm64" ]; then
        BLENDER_WGET_LINK='https://download.blender.org/release/Blender3.6/blender-3.6.0-macos-arm64.dmg'
    else
        BLENDER_WGET_LINK='https://download.blender.org/release/Blender3.6/blender-3.6.0-macos-x64.dmg'
    fi
    BLENDER_WGET_FILE='blender.dmg'
    BLENDER_VOLM='/Volumes/Blender'
    BLENDER_PYTHON="${BLENDER_DIR}/Contents/Resources/3.6/python/bin/python3.10"
else
    echo "Unsupported OS: ${OS}"
    exit 1
fi

if [ ! -d "${BLENDER_DIR}" ]; then
    wget -O "${BLENDER_WGET_FILE}" "${BLENDER_WGET_LINK}"

    if [ "${OS}" = "Darwin" ]; then
        hdiutil attach "${BLENDER_WGET_FILE}"
        cp -r "${BLENDER_VOLM}/Blender.app" "${BLENDER_DIR}"
        hdiutil detach "${BLENDER_VOLM}"
    else
        tar -xf "${BLENDER_WGET_FILE}"
        mv "${BLENDER_UNTAR_DIR}" "${BLENDER_DIR}"
    fi

    rm "${BLENDER_WGET_FILE}"
fi

"${BLENDER_PYTHON}" -m ensurepip

ABS_BLENDER_PYTHON="$(cd "$(dirname "${BLENDER_PYTHON}")" && pwd)/$(basename "${BLENDER_PYTHON}")"

# Install runtime deps (bpy excluded) from our own requirements file
"${ABS_BLENDER_PYTHON}" -m pip install -r infinigen125_requirements.txt

# Install infinigen itself without pulling its declared deps (which include bpy)
CFLAGS="-I/usr/include/python3.10 ${CFLAGS}" INFINIGEN_MINIMAL_INSTALL=True \
    "${ABS_BLENDER_PYTHON}" -m pip install -e "${INFINIGEN_DIR}" --no-deps

echo "Done. Invoke Blender 3.6 via ./blender_3_6.sh (resolves the ${BLENDER_DIR}/blender or ${BLENDER_DIR}/Contents/MacOS/Blender path automatically)."
