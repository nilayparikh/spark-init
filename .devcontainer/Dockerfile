# 1. Use the official ARM64/Blackwell-optimized PyTorch base image
FROM nvcr.io/nvidia/pytorch:26.04-py3

# Avoid interactive frontend prompts during package installations
ENV DEBIAN_FRONTEND=noninteractive

# 2. Fix Ubuntu package names, avoid recommended bloat, and clean cache in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 3. Securely fetch and run the official NodeSource script for Node.js LTS (v20)
# This handles the proper deb.nodesource.com routing and ARM64 setup automatically.
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# 4. Install Claude Code globally using npm
RUN npm install -g @anthropic-ai/claude-code

# 5. Create a non-root devcontainer user for the mounted workspace
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=1000

RUN set -eux; \
    group_name="$(getent group "${USER_GID}" | cut -d: -f1 || true)"; \
    if [ -z "${group_name}" ]; then \
        group_name="${USERNAME}"; \
        groupadd --gid "${USER_GID}" "${group_name}"; \
    fi; \
    useradd --non-unique --uid "${USER_UID}" --gid "${group_name}" -m -s /bin/bash "${USERNAME}"; \
    apt-get update; \
    apt-get install -y --no-install-recommends sudo; \
    echo "${USERNAME} ALL=(root) NOPASSWD:ALL" > "/etc/sudoers.d/${USERNAME}"; \
    chmod 0440 "/etc/sudoers.d/${USERNAME}"; \
    mkdir -p /workspace; \
    chown "${USER_UID}:${USER_GID}" /workspace; \
    rm -rf /var/lib/apt/lists/*

# 6. Inject optimization environment variables for Custom Models & Docker isolation
ENV CLAUDE_CODE_ATTRIBUTION_HEADER="0" \
    IS_SANDBOX="1" \
    CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL="1" \
    CLAUDE_CODE_AUTO_CONNECT_IDE="false" \
    CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL="1" \
    DISABLE_INSTALLATION_CHECKS="1" \
    HOME="/home/${USERNAME}"

# 7. Set up the active workspace
WORKDIR /workspace

# 8. Switch to the devcontainer user
USER ${USERNAME}

# 9. Add system metadata labels
LABEL maintainer="Nilay Parikh <nilay.parikh@gmail.com>" \
      version="0.1" \
      description="A Docker image for .init development with Claude Code and PyTorch on NVIDIA DGX Spark." \
      repository="https://github.com"
