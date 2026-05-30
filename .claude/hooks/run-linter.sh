#!/bin/bash
set -euo pipefail
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

if [[ "$FILE_PATH" == *"docker-compose"* ]] && [[ "$FILE_PATH" == *.yml ]]; then
  yamllint -d "{extends: default, rules: {line-length: disable, truthy: disable}}" "$FILE_PATH"
elif [[ "$FILE_PATH" == *.sh ]]; then
  shellcheck -e SC1091 -e SC2154 -e SC2317 -S warning "$FILE_PATH"
elif [[ "$FILE_PATH" == *.py ]]; then
  python3 -m py_compile "$FILE_PATH"
fi
