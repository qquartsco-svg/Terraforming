#!/bin/bash
# 수정 후 GitHub 푸시 (setup_git_and_push.sh 와 동일)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec bash "$SCRIPT_DIR/setup_git_and_push.sh" "$@"
