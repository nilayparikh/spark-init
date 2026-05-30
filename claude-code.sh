#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# ==========================================
# CONFIGURATION VARIABLES
# ==========================================
REGISTRY="nilayparikh"
IMAGE_NAME="dgx-dev"
VERSION="v0.0.1"
CONTAINER_NAME="claude-dev-workspace"
WORKSPACE_DIR="$(pwd)"

# ==========================================
# STEP 1: PARSE .ENV FILE IN THE ROOT FOLDER
# ==========================================
ENV_FILE="${WORKSPACE_DIR}/.env"

if [ -f "$ENV_FILE" ]; then
    echo "📄 [ENV] Found .env file in workspace root. Parsing keys..."
    set -a
    # shellcheck source=/dev/null
    source <(grep -v '^#' "$ENV_FILE")
    set +a
else
    echo "⚠️ [ENV] No .env file found at ${ENV_FILE}. Falling back to default values."
fi

# Ensure Hugging Face and GitHub auth tokens are available in the container.
HF_TOKEN="${HF_TOKEN:-${HUGGINGFACE_TOKEN:-}}"
HUGGINGFACE_TOKEN="${HUGGINGFACE_TOKEN:-${HF_TOKEN:-}}"
GH_TOKEN="${GH_TOKEN:-${GITHUB_PERSONAL_ACCESS_TOKEN:-}}"
GITHUB_PERSONAL_ACCESS_TOKEN="${GITHUB_PERSONAL_ACCESS_TOKEN:-${GH_TOKEN:-}}"

# Configure environment and model routing for the container.
LITELLM_MASTER_KEY="${LITELLM_MASTER_KEY:-your-default-master-key}"
MODEL_BASE_URL="http://barsana.local:4000"

# ==========================================
# STEP 2: CONDITIONALLY BUILD THE MULTI-TAG IMAGE
# ==========================================
TARGET_IMAGE="${REGISTRY}/${IMAGE_NAME}:${VERSION}"

if docker image inspect "$TARGET_IMAGE" >/dev/null 2>&1; then
    echo "⏭️ [BUILD] Image '${TARGET_IMAGE}' already exists locally. Skipping build phase."
else
    echo "🚀 [BUILD] '${TARGET_IMAGE}' not found. Compiling container layers..."
    docker build \
      -f .devcontainer/Dockerfile \
      -t "${REGISTRY}/${IMAGE_NAME}:${VERSION}" \
      -t "${REGISTRY}/${IMAGE_NAME}:latest" .
    echo "✅ [BUILD] Successfully built and tagged both versions."
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

  # Verified working configuration directory mounts
  -v "${WORKSPACE_DIR}/.claude:/workspace/.claude"
  -v "${WORKSPACE_DIR}/.claude.json:/workspace/.claude.json"
  -e HOME="/workspace"
  -e CLAUDE_CONFIG_DIR="/workspace/.claude"
  
  # Set the custom model as the primary default engine loop
  -e CLAUDE_MODEL="dgx-qwen3-6-27b-swe"
  -e IS_SANDBOX="1"

  # LiteLLM routing parameters
  -e ANTHROPIC_BASE_URL="${MODEL_BASE_URL}"
  -e ANTHROPIC_AUTH_TOKEN="${LITELLM_MASTER_KEY}"
  -e HF_TOKEN="${HF_TOKEN}"
  -e GH_TOKEN="${GH_TOKEN}"
  -e GITHUB_PERSONAL_ACCESS_TOKEN="${GITHUB_PERSONAL_ACCESS_TOKEN}"
  -e CLAUDE_CODE_ATTRIBUTION_HEADER="0"
  -e CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"

  # Suppress interactive prompts (onboarding, theme, trust, IDE install)
  -e IS_DEMO="1"
  -e CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL="1"
  -e CLAUDE_CODE_AUTO_CONNECT_IDE="false"
  -e CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL="1"
  -e CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS="1"
  -e DISABLE_INSTALLATION_CHECKS="1"

  # System fallbacks
  -e ANTHROPIC_CUSTOM_MODEL_OPTION="dgx-qwen3-6-27b-swe"
  -e ANTHROPIC_CUSTOM_MODEL_OPTION_NAME="DGX/Qwen3.6-27B/SWE"
  -e ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION="DGX/Anthropic"
  -e ANTHROPIC_DEFAULT_HAIKU_MODEL="dgx-qwen3-6-35b-a3b"
)

# Launch standard execution cleanly without syntax crashes
docker run "${DOCKER_OPTS[@]}" "${TARGET_IMAGE}" claude --dangerously-skip-permissions

