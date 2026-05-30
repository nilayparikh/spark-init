# Prerequisites

This page covers the system requirements and software prerequisites for running the `.init` stack.

## Hardware Requirements

### GPU

| Requirement             | Minimum                           | Recommended                     |
| ----------------------- | --------------------------------- | ------------------------------- |
| GPU Architecture        | NVIDIA Ada Lovelace (compute 9.0) | NVIDIA Blackwell (compute 12.0) |
| VRAM for 27B models     | 48 GB                             | 80+ GB (DGX Spark)              |
| VRAM for 35B A3B models | 80 GB                             | —                               |
| Driver Version          | ≥ 570 (Blackwell support)         | Latest stable driver            |

> **Why Blackwell/Ada?** The project is optimized for compute capability ≥9.0. The CUDA build targets architecture `12.1` (Blackwell). Older GPUs may work but won't benefit from the optimized kernels.

### System

| Component | Minimum                                  |
| --------- | ---------------------------------------- |
| OS        | Ubuntu 24.04 ARM64 (primary)             |
| CPU       | 8+ cores for host-side collection agents |
| RAM       | 32 GB system memory (separate from VRAM) |
| Disk      | 100+ GB free space for models and Docker images |

## Software Requirements

### Docker

```bash
# Verify Docker version
docker --version
# Should be ≥ 27.0

# Verify Compose plugin
docker compose version
```

If you need to install or upgrade:

```bash
# Add Docker's official GPG key and repository
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### NVIDIA Container Toolkit

The nvidia-container-toolkit enables Docker containers to access NVIDIA GPUs.

```bash
# Add the repository
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/$(dpkg --print-architecture)/list | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure Docker runtime
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Verify
docker run --rm --runtime=nvidia --gpus all nvidia/cuda:13.1.2-base-ubuntu24.04 nvidia-smi
```

### Git

```bash
git --version
# Should be ≥ 2.43
```

## Model Files

Model weights are **not included** directly in this repository, but are available as git submodules:

```bash
# Initialize all model submodules
git submodule update --init --recursive
```

This populates `models/qwen3.6-27b-text-nvfp4-mtp/` and `models/qwen3.6-35b-a3b-nvfp4-mtp/` with the GGUF weight files. The `.env.example` defaults point to these paths.

### Manual Download (Alternative)

If you prefer not to use submodules, download the GGUF files manually:

```bash
# Download the 27B model
wget <hf-url-to-gguf> -P /path/to/models/

# Download the 35B A3B model + multimodal projector
wget <hf-url-to-35b-gguf> -P /path/to/models/
wget <hf-url-to-mmproj> -P /path/to/models/

# Set in .env
LLAMA_QWEN_3_6_27B_GGUF_MODEL_PATH=/path/to/models/qwen3.6-27b-model.gguf
LLAMA_QWEN_3_6_35B_A3B_GGUF_MODEL_PATH=/path/to/models/qwen3.6-35b-a3b-model.gguf
LLAMA_QWEN_3_6_35B_A3B_MMPROJ_MODEL_PATH=/path/to/models/mmproj-BF16.gguf
```

> **Note:** Only llama.cpp is supported as the inference backend. vLLM is NOT supported on DGX Spark hardware due to SM120/SM121 limitations (missing TMEM, unoptimized kernels, MTP shape mismatch).

## Verify Your Setup

Run this checklist before starting the stack:

```bash
# 1. Docker is running
docker info > /dev/null 2>&1 && echo "✓ Docker OK" || echo "✗ Docker NOT OK"

# 2. Compose plugin available
docker compose version > /dev/null 2>&1 && echo "✓ Compose OK" || echo "✗ Compose NOT OK"

# 3. NVIDIA runtime configured
docker run --rm --runtime=nvidia --gpus all nvidia/cuda:13.1.2-base-ubuntu24.04 nvidia-smi > /dev/null 2>&1 && echo "✓ NVIDIA runtime OK" || echo "✗ NVIDIA runtime NOT OK"

# 4. Model file exists
[ -f "$LLAMA_QWEN_3_6_27B_GGUF_MODEL_PATH" ] && echo "✓ 27B model OK" || echo "✗ 27B model NOT FOUND"
```

## Platform Support

| Platform                     | Status          | Notes                                                                       |
| ---------------------------- | --------------- | --------------------------------------------------------------------------- |
| Ubuntu 24.04 ARM64 (aarch64) | ✅ Primary      | DGX Spark, Grace Blackwell systems. All features supported.                 |
| Ubuntu 24.04 x86_64 (amd64)  | ⚠️ Experimental | May work with NVIDIA GPUs but not all optimizations apply. Test thoroughly. |
| Other Linux distributions    | ❌ Not tested   | Contributions welcome for additional distro support.                        |
