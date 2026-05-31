#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# ==========================================
# CONFIGURATION VARIABLES
# ==========================================
REGISTRY="${CLAUDE_CODE_REGISTRY:-ghcr.io/nilayparikh}"
IMAGE_NAME="${CLAUDE_CODE_IMAGE_NAME:-claude-code}"
VERSION="${CLAUDE_CODE_IMAGE_TAG:-latest}"
CONTAINER_NAME="${CLAUDE_CODE_CONTAINER_NAME:-claude-dev-workspace}"
WORKSPACE_DIR="$(pwd)"

# ==========================================
# STEP 1: LOAD ENVIRONMENT SECRETS
# ==========================================
echo "📄 [ENV] Extracting configuration tokens..."

# 1a. Safely pull keys from ~/.env.secrets if it exists
SECRETS_FILE="${HOME}/.env.secrets"
if [ -f "$SECRETS_FILE" ]; then
    echo "  -> Parsing keys from ${SECRETS_FILE}..."
    set -a
    # shellcheck source=/dev/null
    source <(grep -v '^#' "$SECRETS_FILE")
    set +a
else
    echo "⚠️  [ENV] No global secrets file found at ${SECRETS_FILE}"
fi

# 1b. Parse workspace .env file if it exists (takes precedence over bashrc)
ENV_FILE="${WORKSPACE_DIR}/.env"
if [ -f "$ENV_FILE" ]; then
    echo "  -> Found local .env file in workspace root. Overlaying variables..."
    set -a
    # shellcheck source=/dev/null
    source <(grep -v '^#' "$ENV_FILE")
    set +a
fi

# 1c. Sanity checks for critical authentication tokens
if [ -z "$LITELLM_MASTER_KEY" ]; then
    echo "⚠️  [WARN] LITELLM_MASTER_KEY is empty. Proxy validation may fail."
fi

MODEL_BASE_URL="${CLAUDE_CODE_MODEL_BASE_URL:-http://barsana.local:4000}"

# Capture extra arguments that should be forwarded into the Claude CLI.
CLAUDE_ARGS=("$@")
if [ "${#CLAUDE_ARGS[@]}" -gt 0 ]; then
    echo "📥 [ARGS] Forwarding additional Claude flags: ${CLAUDE_ARGS[*]}"
fi

# ==========================================
# STEP 2: PULL THE IMAGE DIRECTLY FROM GHCR
# ==========================================
TARGET_IMAGE="${REGISTRY}/${IMAGE_NAME}:${VERSION}"

echo "📥 [IMAGE] Pulling '${TARGET_IMAGE}' from GHCR..."
if ! docker pull "${TARGET_IMAGE}"; then
    echo "⚠️ [IMAGE] Tag '${VERSION}' not found on GHCR. Falling back to 'latest'..."
    TARGET_IMAGE="${REGISTRY}/${IMAGE_NAME}:latest"
    echo "📥 [IMAGE] Pulling '${TARGET_IMAGE}' from GHCR..."
    docker pull "${TARGET_IMAGE}"
fi

# ==========================================
# STEP 3: REMOVE ANY STALE CONTAINERS
# ==========================================
if [ "$(docker ps -aq -f name=^${CONTAINER_NAME}$)" ]; then
    echo "🔄 [CLEAN] Found an existing container named '${CONTAINER_NAME}'. Removing..."
    docker rm -f "${CONTAINER_NAME}" > /dev/null
fi

# ==========================================
# STEP 4: RUN ISOLATED AGENT WITH MODEL ALIASES
# ==========================================
echo "📦 [RUN] Starting isolated container environment..."
echo "🌐 [RUN] Routing Claude Code through LiteLLM at: ${MODEL_BASE_URL}"

# Ensure home configuration folder exists locally so Docker doesn't create it as root
mkdir -p "${HOME}/.claude"
mkdir -p "${WORKSPACE_DIR}/.claude"

DOCKER_OPTS=(
  -it
  --rm
  --name "${CONTAINER_NAME}"
  --gpus all
  --network host
  -u "$(id -u):$(id -g)"
  --ipc=host
  
  # Work directories mapping
  -v "${WORKSPACE_DIR}:/workspace"
  -w /workspace
  -v "${HOME}/.gitconfig:/.gitconfig:ro"
  -v "${HOME}/.ssh:/.ssh:ro"

  # DUAL-SCOPE CONFIGURATION
  -v "${HOME}/.claude:/home/claude"
  -e HOME="/home/claude"

  # Maps your local project history and workspace settings
  -v "${WORKSPACE_DIR}/.claude:/workspace/.claude"

  # Enable gateway model discovery for LiteLLM proxy model routing
  -e CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY="1"
  -e COLUMNS="$(tput cols 2>/dev/null || echo ${CLAUDE_CODE_COLUMNS:-80})"
  -e LINES="$(tput lines 2>/dev/null || echo ${CLAUDE_CODE_LINES:-24})"

  # Set the custom model as the primary default engine loop
  -e CLAUDE_MODEL="${LITELLM_MODEL_ALIAS_FLASH:-.INIT/Flash}"
  -e IS_SANDBOX="1"

  # LiteLLM routing parameters (FIXED syntax variables mapping)
  -e ANTHROPIC_BASE_URL="${MODEL_BASE_URL}"
  -e ANTHROPIC_AUTH_TOKEN="${LITELLM_MASTER_KEY}"
  -e HF_TOKEN="${HF_TOKEN}"
  -e GH_TOKEN="${GH_TOKEN}"
  -e GITHUB_PERSONAL_ACCESS_TOKEN="${GITHUB_PERSONAL_ACCESS_TOKEN}"
  -e CLAUDE_CODE_ATTRIBUTION_HEADER="0"
  -e CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"

  # Suppress interactive prompts (onboarding, theme, trust, IDE install)
  -e CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL="1"
  -e CLAUDE_CODE_AUTO_CONNECT_IDE="false"
  -e CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL="1"
  -e CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS="1"
  -e DISABLE_INSTALLATION_CHECKS="1"

  # System fallbacks (FIXED quotes surrounding slashes)
  -e ANTHROPIC_CUSTOM_MODEL_OPTION=".INIT/Air"
  -e ANTHROPIC_CUSTOM_MODEL_OPTION_NAME="INIT/Air"
  -e ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION="Air via LiteLLM"

  # Model group defaults (Haiku, Sonnet, Opus)
  -e ANTHROPIC_DEFAULT_OPUS_MODEL=".INIT/Ultra"
  -e ANTHROPIC_DEFAULT_OPUS_MODEL_NAME="INIT/Ultra"
  -e ANTHROPIC_DEFAULT_OPUS_MODEL_DESCRIPTION="Ultra via LiteLLM"

  -e ANTHROPIC_DEFAULT_SONNET_MODEL=".INIT/Pro"
  -e ANTHROPIC_DEFAULT_SONNET_MODEL_NAME="INIT/Pro"
  -e ANTHROPIC_DEFAULT_SONNET_MODEL_DESCRIPTION="Pro via LiteLLM"

  -e ANTHROPIC_DEFAULT_HAIKU_MODEL=".INIT/Flash"
  -e ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME="INIT/Flash"
  -e ANTHROPIC_DEFAULT_HAIKU_MODEL_DESCRIPTION="Flash via LiteLLM"
)

# Launch standard execution cleanly without syntax crashes
docker run "${DOCKER_OPTS[@]}" "${TARGET_IMAGE}" claude --dangerously-skip-permissions "${CLAUDE_ARGS[@]}"
