#!/bin/bash
set -euo pipefail
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ "$FILE_PATH" == *".env"* ]]; then
  echo "Blocked: .env files contain secrets. Use .env.example for template changes." >&2
  exit 2
fi

exit 0
