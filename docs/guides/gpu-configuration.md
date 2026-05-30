# GPU Configuration

This guide covers GPU passthrough for Docker containers, persistent performance settings, and DCGM exporter setup for monitoring NVIDIA GPUs on the `.init` stack.

## Prerequisites

- NVIDIA GPU with compute capability ≥ 8.0 (Hopper or Ada Lovelace architecture)
- NVIDIA driver ≥ 570
- `nvidia-container-toolkit` installed on the host
- Docker ≥ 27.x with NVIDIA runtime configured

## GPU Passthrough in Docker

The `.init` stack passes GPUs to containers via the `gpus` directive in Docker Compose. Two approaches are used:

### All GPUs (Default)

```yaml
# Pass all available GPUs to a container
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

This is the default for `llama-qwen-3-6-27b` and DCGM exporter services. It gives the container access to every GPU on the host.

### Specific GPUs

```yaml
# Pass only GPU 0 and 1
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          device_ids: ['0', '1']
          capabilities: [gpu]
```

Use this when you want to isolate workloads across GPUs or share the host with other processes.

### NVIDIA Runtime Configuration

Ensure the Docker daemon has `nvidia` set as the default runtime. On Ubuntu 24.04:

```bash
# Install nvidia-container-toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/$(arch)/ | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure Docker to use NVIDIA runtime
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Verify with:

```bash
docker run --rm --gpus all nvidia/cuda:13.1.2-base-ubuntu24.04 nvidia-smi
```

## Persistent GPU Settings

For consistent inference performance, apply persistent mode and locked clock speeds at boot. The script `scripts/gpu-persistent-setting.sh` applies two settings:

```bash
# Enable persistence mode (keeps driver loaded even when no process uses the GPU)
nvidia-smi -pm 1

# Lock graphics clock range (example: 208 to 2418 MHz)
nvidia-smi --lock-gpu-clocks=208,2418
```

### Why Persistence Mode Matters

Without persistence mode, the NVIDIA driver may unload when no GPU process is active. The next GPU workload then pays a 5–15 second initialization penalty as the driver reloads. Persistence mode eliminates this cold-start latency.

### Why Lock Clocks

Inference workloads benefit from stable clock speeds. Unlocked GPUs may downclock under thermal pressure, causing variable token throughput. Locking clocks ensures predictable latency for SLA-sensitive applications.

### Making Settings Persistent Across Reboots

Create a systemd service that applies these settings after the NVIDIA persistence daemon starts:

1. Copy the script to a system location:

   ```bash
   sudo cp scripts/gpu-persistent-setting.sh /usr/local/bin/gpu-persistent-settings.sh
   sudo chmod +x /usr/local/bin/gpu-persistent-settings.sh
   ```

2. Create the systemd service file:

   ```bash
   sudo nano /etc/systemd/system/nvidia-prop.service
   ```

   Paste:

   ```ini
   [Unit]
   Description=Apply Custom NVIDIA GPU Power and Clock Limits
   After=nvidia-persistenced.service
   Wants=nvidia-persistenced.service

   [Service]
   Type=oneshot
   RemainAfterExit=yes
   ExecStart=/usr/local/bin/gpu-persistent-settings.sh

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable nvidia-prop.service
   sudo systemctl start nvidia-prop.service
   ```

4. Verify:

   ```bash
   sudo systemctl status nvidia-prop.service
   nvidia-smi  # Check that persistence mode shows "Enabled"
   ```

## DCGM Exporter

The NVIDIA Data Center GPU Manager (DCGM) exporter exposes GPU telemetry as Prometheus metrics. The `.init` stack runs it as a sidecar container.

### What DCGM Reports

DCGM exposes 100+ metrics including:

| Metric Group | Key Metrics |
|-------------|-------------|
| Temperature | `DCGM_FI_DEV_GPU_TEMP`, `DCGM_FI_DEV_MEM_HOT_SPOT_TEMP` |
| Power | `DCGM_FI_DEV_POWER_USAGE`, `DCGM_FI_DEV_POWER_STATE` |
| Clocks | `DCGM_FI_DEV_SM_CLOCK`, `DCGM_FI_DEV_MEM_CLOCK` |
| Utilization | `DCGM_FI_DEV_SM_CLOCK`, `DCGM_FI_DEV_MEM_COPY_UTIL` |
| ECC | `DCGM_FI_DEV_ECC_SBE_HB_TOTAL`, `DCGM_FI_DEV_ECC_DBE_HB_TOTAL` |
| VRAM | `DCGM_FI_DEV_FB_USED`, `DCGM_FI_DEV_FB_FREE` |

### Configuration in the Stack

The DCGM exporter container is defined in the observability compose file:

```yaml
gpu-telemetry:
  image: nvcr.io/nvidia/k8s/dcgm-exporter:4.5.3-4.8.2-distroless
  container_name: gpu-telemetry
  profiles: [obs]
  gpus: all
  networks:
    - init_default
```

Alley scrapes DCGM at `gpu-telemetry:9400` every 5 seconds and forwards metrics to Mimir with `job="machine-gpu"` labels.

### Verifying DCGM

```bash
# Check the exporter is running
docker ps | grep gpu-telemetry

# Query metrics directly
curl http://localhost:9400/metrics | grep DCGM_FI_DEV_GPU_TEMP
```

## GPU Smoke Test

The stack includes a smoke test to verify end-to-end GPU functionality:

```bash
python3 scripts/spark-gpu-smoke-test.py
```

This script:
1. Checks `nvidia-smi` output for GPU presence
2. Verifies CUDA toolkit version compatibility
3. Confirms the NVIDIA container toolkit is functional
4. Reports GPU memory, temperature, and power state

## Troubleshooting GPU Issues

### "Could not initialize GPU device"

```bash
# Check driver is loaded
lsmod | grep nvidia

# Check container toolkit is configured
sudo nvidia-ctk info

# Restart Docker after toolkit changes
sudo systemctl restart docker
```

### Container Can't See GPU

```bash
# Verify gpus directive is in the compose file
docker compose config | grep -A 5 gpus

# Check NVIDIA runtime is default
docker info | grep -A 5 "Runtimes"
```

### GPU Memory Leaks Between Restarts

```bash
# Reset GPU state (requires stopping all GPU containers first)
docker compose down
nvidia-smi --gpu-reset
```

> **★ Insight**
> - Persistence mode (`nvidia-smi -pm 1`) eliminates 5–15s cold-start penalties when the driver reloads.
> - DCGM exporter runs as a distroless container — no shell, just metrics at `:9400`.
> - The `nvidia-ctk runtime configure` step is the most common gotcha: if Docker's default runtime isn't `nvidia`, `--gpus all` silently fails.
