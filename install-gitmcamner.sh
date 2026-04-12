#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="${HOME}/bin"
TARGET_PATH="${TARGET_DIR}/gitmcamner"
SOURCE_PATH="${REPO_ROOT}/bin/gitmcamner"

mkdir -p "$TARGET_DIR"
ln -sf "$SOURCE_PATH" "$TARGET_PATH"

cat <<EOF
Installed gitmcamner to:
  $TARGET_PATH

If "$TARGET_DIR" is in your PATH, you can now run:
  gitmcamner
EOF
