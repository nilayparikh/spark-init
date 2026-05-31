# Guides

Task-oriented recipes for common things you'll do with `.init`.

---

## Add a New GGUF Model

1. Place the `.gguf` file somewhere on your host
2. Add the path to `.env` (or add a new variable)
3. Create a new service in `interfaces/docker-compose.interface.yml` — copy the 27B block, swap the model path and port
4. If the model needs a different chat template, place it in `interfaces/config/`
5. Add a LiteLLM provider fragment in `interfaces/config/litellm/providers/` referencing the new upstream URL
6. `docker compose up -d --force-recreate <service-name>`

**Pro tip:** If the model uses a different prompt format, set `--jinja --chat-template-file` with the right template; otherwise llama.cpp uses its built-in default.

## Optimize GPU Performance

For consistent inference speed, apply these settings on the host:

```bash
# Keep the driver loaded (eliminates 5-15s cold start)
sudo nvidia-smi -pm 1

# Lock clock speeds to prevent thermal throttling
sudo nvidia-smi --lock-gpu-clocks=208,2418
```

To apply these on boot, create a systemd service or add the commands to `/etc/rc.local`.

## Add a Cloud Provider

1. Get an API key from the provider
2. Add it to `.env.secrets` (e.g., `NVIDIA_API_KEY=nvapi-...`)
3. The provider's YAML fragment in `interfaces/config/litellm/providers/` reads it from the environment variable
4. Restart LiteLLM: `docker compose restart litellm`
5. It shows up in `GET /v1/models` automatically

Available cloud providers are listed in the `.env.example` with their variable names and endpoints.

## Work with Claude Code

The easiest way is the `claude-code.sh` launcher — it reads your `.env` for model routing and auth, builds/pulls the container image, and starts an isolated Claude Code session routed through the local LiteLLM proxy:

```bash
./claude-code.sh
# /model .INIT/Pro    → use local 27B
# /model .INIT/Flash   → use local 35B A3B
# /model .INIT/Ultra   → use cloud OpenCode Zen (if configured)
```

You can also point a local `claude` CLI at the proxy directly:

```bash
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_AUTH_TOKEN="$LITELLM_MASTER_KEY"
export CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1

claude
```

## Use with VS Code / Cline / Continue

Configure any OpenAI-compatible extension:

```json
{
  "baseURL": "http://localhost:4000/v1",
  "apiKey": "<your-liteLLM-key>",
  "model": "DGX/Qwen3.6-27B"
}
```

## Troubleshooting

### GPU not found in container

The most common issue. Fix:

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Then verify: `docker run --rm --gpus all nvidia/cuda:13.1.2-devel-ubuntu24.04 nvidia-smi`

### Port already in use

```bash
sudo lsof -i :4000   # find what's using it
# Change LITELLM_PORT in .env and restart
```

### Model fails to load

```bash
# Check the path inside the container
docker exec llama-qwen-3-6-27b ls -la /models/

# Verify file integrity
xxd /path/to/model.gguf | head -1
# Should start with GGUF magic bytes
```

### LiteLLM returns 401

This is almost always timing — the proxy needs 10-30s for database migration on first start:

```bash
docker logs litellm --tail 50 | grep "Proxy is ready"
```

### Nothing works

```bash
docker compose logs --tail=100 <service-name>   # fastest debug tool
```

For detailed reference, see the inline comments in:

- `interfaces/docker-compose.interface.yml` — all llama.cpp flags documented
- `interfaces/config/litellm/config.yaml` — routing and alias configuration
- `observability/config/config.alloy` — scrape pipelines and label conventions
