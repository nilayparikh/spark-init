# 1. Use the official ARM64/Blackwell-optimized PyTorch base image
FROM nvcr.io/nvidia/pytorch:26.04-py3

# Avoid interactive frontend prompts during package installations
ENV DEBIAN_FRONTEND=noninteractive

# 2. Fix Ubuntu package names, avoid recommended bloat, and clean cache in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    ca-certificates \
    shellcheck \
    fd-find \
    tree \
    ripgrep \
    jq \
    yq \
    zoxide \
    sd \
    unzip \
    openssh-client \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s $(which fdfind) /usr/local/bin/fd

# 3. Securely fetch and run the official NodeSource script for Node.js LTS (v20)
# This handles the proper deb.nodesource.com routing and ARM64 setup automatically.
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# 4. Install GitHub CLI using the official Debian repository
RUN mkdir -p /usr/share/keyrings \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
    > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

# 5. Install additional Claude Code productivity utilities
RUN set -eux; \
    curl -fsSL -o /tmp/ast-grep.zip \
      https://github.com/ast-grep/ast-grep/releases/latest/download/app-aarch64-unknown-linux-gnu.zip; \
    unzip /tmp/ast-grep.zip -d /tmp/ast-grep; \
    install -Dm755 /tmp/ast-grep/ast-grep /usr/local/bin/ast-grep; \
    curl -fsSL -o /tmp/difft.tar.gz \
      https://github.com/Wilfred/difftastic/releases/latest/download/difft-aarch64-unknown-linux-gnu.tar.gz; \
    tar -xzf /tmp/difft.tar.gz -C /tmp; \
    install -Dm755 /tmp/difft /usr/local/bin/difft; \
    ln -fs /usr/local/bin/difft /usr/local/bin/difftastic; \
    curl -fsSL -o /tmp/scc.tar.gz \
      https://github.com/boyter/scc/releases/latest/download/scc_Linux_arm64.tar.gz; \
    tar -xzf /tmp/scc.tar.gz -C /tmp; \
    install -Dm755 /tmp/scc /usr/local/bin/scc; \
    curl -fsSL -o /tmp/watchexec.deb \
      https://github.com/watchexec/watchexec/releases/latest/download/watchexec-2.5.1-aarch64-unknown-linux-gnu.deb; \
    apt-get update; \
    apt-get install -y --no-install-recommends /tmp/watchexec.deb; \
    rm -rf /tmp/* /var/lib/apt/lists/*

# 6. Install Claude Code globally using npm
RUN npm install -g @anthropic-ai/claude-code

# 7. Install Trivy security scanner (official Aqua Security repository)
RUN apt-get update && apt-get install -y --no-install-recommends wget gnupg \
    && wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | tee /usr/share/keyrings/trivy.gpg > /dev/null \
    && echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" > /etc/apt/sources.list.d/trivy.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends trivy \
    && rm -rf /var/lib/apt/lists/*

RUN trivy plugin install mcp

# 9. Create a non-root devcontainer user for the mounted workspace
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

# 10. Inject optimization environment variables for Custom Models & Docker isolation
ENV CLAUDE_CODE_ATTRIBUTION_HEADER="0" \
    IS_SANDBOX="1" \
    CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL="1" \
    CLAUDE_CODE_AUTO_CONNECT_IDE="false" \
    CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL="1" \
    DISABLE_INSTALLATION_CHECKS="1" \
    HOME="/home/${USERNAME}"

# 11. Set up the active workspace
WORKDIR /workspace

# 12. Switch to the devcontainer user
USER ${USERNAME}

# 13. Add OCI-compliant metadata labels
LABEL org.opencontainers.image.title="claude-code" \
      org.opencontainers.image.description="Claude Code dev container with NVIDIA PyTorch for DGX Spark" \
      org.opencontainers.image.url="https://github.com/nilayparikh/spark-init" \
      org.opencontainers.image.source="https://github.com/nilayparikh/spark-init" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.vendor="Nilay Parikh" \
      org.opencontainers.image.authors="Nilay Parikh <nilay.parikh@gmail.com>" \
      org.opencontainers.image.version="0.1" \
      org.opencontainers.image.ref.name="v0.0.1"
