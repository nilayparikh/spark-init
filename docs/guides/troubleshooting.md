# Troubleshooting

This guide covers common issues when running the `.init` stack, from CUDA stub linking failures to LiteLLM authentication problems.

## CUDA Stub Linking Failures

### Symptom

Container startup fails with errors like:

```
libcuda.so: cannot open shared object file: No such file or directory
```

or

```
Error: CUDA driver version is insufficient for CUDA runtime version
```

### Causes and Fixes

**1. NVIDIA Container Toolkit not configured**

The most common cause. Docker needs the NVIDIA runtime to inject CUDA libraries into containers.

```bash
# Install and configure
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Verify
docker run --rm --gpus all nvidia/cuda:13.1.2-base-ubuntu24.04 nvidia-smi
```

**2. Driver/Runtime version mismatch**

The llama.cpp Docker image is built against a specific CUDA version. If the host driver is too old, CUDA stubs won't link.

```bash
# Check host driver version
nvidia-smi | grep "Driver Version"

# Check image CUDA version
docker inspect nilayparikh/llama-cpp-dgx:cuda13.1.2-b9222 | grep -i cuda
```

Fix: Update the host NVIDIA driver to ≥ 570, or rebuild the image against the host's CUDA version.

**3. Missing `--gpus all` in compose file**

Verify the service definition includes GPU reservations:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

## Model Loading Failures

### Symptom

llama.cpp container starts but fails to load the model:

```
error: failed to load model: No such file or directory
```

### Causes and Fixes

**1. Model path not accessible from inside the container**

The `LLAMA_QWEN_3_6_27B_GGUF_MODEL_PATH` in `.env` must point to a path that is volume-mounted into the container. The compose file maps host paths to container paths:

```yaml
volumes:
  - /path/to/models:/models:ro
```

Ensure the model file exists at the expected path inside the container. Check with:

```bash
docker exec llama-qwen-3-6-27b ls -la /models/
```

**2. Model file is corrupted or incomplete**

Verify the GGUF file integrity:

```bash
# Check file size matches the repository
ls -lh /path/to/model.gguf

# Quick sanity check — the file should start with GGUF magic bytes
xxd /path/to/model.gguf | head -1
# Expected: 00000000: 6665 7567 3041 0000  ...
```

Re-download from Hugging Face if the file is truncated.

**3. Insufficient VRAM**

The model won't load if GPU memory is insufficient:

```
error: couldn't find a GPU backend with enough memory
```

Check available VRAM:

```bash
nvidia-smi | grep -i "fb"
```

Fix: Use a lower quantization (Q4_0 instead of Q8_0) or a smaller model.

## Port Conflicts

### Symptom

```
ERROR: for litellm  "listen tcp 0.0.0.0:4000: bind: address already in use"
```

### Common Port Conflicts

| Port | Service | Common Conflicts |
|------|---------|-----------------|
| 4000 | LiteLLM proxy | Other proxy services |
| 8000 | llama.cpp / vLLM | Other inference servers |
| 3000 | Grafana | Node.js dev servers |
| 5432 | PostgreSQL | Local PostgreSQL installations |
| 9400 | DCGM exporter | Uncommon |

### Fix

**Option A: Stop the conflicting service**

```bash
# Find what's using the port
sudo lsof -i :4000
# or
sudo ss -tlnp | grep 4000
```

**Option B: Change the port in the compose file**

Edit the relevant compose file to remap the host port:

```yaml
ports:
  - "4001:4000"  # Host:Container
```

Update `.env` variables that reference the port accordingly.

## LiteLLM Authentication Issues

### Symptom

```
401 Unauthorized
{"object":"error","message":"Invalid API key","type":"invalid_request_error"}
```

### Causes and Fixes

**1. Missing or incorrect `LITELLM_MASTER_KEY`**

The LiteLLM proxy requires the `Authorization: Bearer <key>` header. Verify the key in `.env`:

```bash
grep LITELLM_MASTER_KEY .env
```

Test with curl:

```bash
curl -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  http://localhost:4000/v1/models
```

**2. Key format mismatch**

LiteLLM expects the key prefixed with `Bearer` in the `Authorization` header. Some clients send `api-key` headers instead. Check your client configuration.

**3. LiteLLM container not ready yet**

LiteLLM may take 10–30 seconds to initialize on first start (database migration, model registration). Check logs:

```bash
docker logs litellm --tail 50
```

Look for `LiteLLM: Proxy is ready` before sending requests.

## Observability Issues

### No Metrics in Grafana

```bash
# Check Alloy is running and connected
docker logs alloy | tail -20

# Verify Mimir is receiving data
curl http://localhost:9009/api/v1/status/build

# Check Alloy can reach Mimir
docker exec alloy wget -q -O- http://mimir:9009/api/v1/status/build
```

### No Logs in Grafana

```bash
# Check Alloy log collection
docker logs alloy | grep -i loki

# Verify Loki is running
docker ps | grep loki

# Test log query in Grafana Explore
{container_name="litellm"}
```

### DCGM Exporter Not Reporting

```bash
# Check DCGM container
docker ps | grep gpu-telemetry

# Test metrics endpoint directly
docker exec gpu-telemetry wget -q -O- http://localhost:9400/metrics | head -5

# If empty, check GPU visibility inside the container
docker exec gpu-telemetry nvidia-smi
```

## Docker Compose Issues

### Service Won't Start After Config Change

```bash
# Rebuild and restart a specific service
docker compose up -d --force-recreate --build <service-name>

# Full stack restart
docker compose down
docker compose up -d
```

### Profile Not Applying

The `COMPOSE_PROFILES` variable in `.env` controls which services start. After changing it:

```bash
# Source the new profiles
docker compose up -d

# Verify active services
docker compose ps
```

Note: Changing `COMPOSE_PROFILES` requires `docker compose down` followed by `docker compose up -d` — simply running `up -d` won't start newly added profiles if containers from a previous run exist.

### Volume Permission Issues

```bash
# Fix ownership for mounted volumes
sudo chown -R 1000:1000 data/storage/
sudo chown -R 472:472 observability/volumes/grafana/
```

## Debug Checklist

When nothing works, work through this list top-to-bottom:

```bash
# 1. Docker is running
docker info

# 2. NVIDIA runtime is available
docker info | grep -A 5 "Runtimes"

# 3. GPU is visible to Docker
docker run --rm --gpus all nvidia/cuda:13.1.2-base-ubuntu24.04 nvidia-smi

# 4. Network is created
docker network ls | grep init_default

# 5. .env is loaded
cat .env | grep COMPOSE_PROFILES

# 6. Services are healthy
docker compose ps

# 7. Container logs for errors
docker compose logs --tail=50 <service-name>
```

> **★ Insight**
> - The #1 cause of "GPU not found" errors is forgetting `sudo nvidia-ctk runtime configure --runtime=docker` after toolkit installation.
> - LiteLLM's 401 errors are almost always a timing issue — the proxy needs 10–30s for DB migration on first start.
> - When in doubt, `docker compose logs --tail=100 <service>` is faster than guessing.
