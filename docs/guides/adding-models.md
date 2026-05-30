# Adding Models

This guide covers how to add new GGUF models to the `.init` stack and wire them into the LiteLLM proxy.

## Supported Model Formats

The `.init` stack uses llama.cpp for inference, which requires models in **GGUF format**. Common quantization schemes:

| Quantization | VRAM (27B) | Quality   | Use Case                                    |
| ------------ | ---------- | --------- | ------------------------------------------- |
| Q8_0         | ~30 GB     | Highest   | Production, best quality                    |
| Q6_K         | ~25 GB     | Very High | Balanced production use                     |
| Q4_K_M       | ~16 GB     | High      | Default — best balance of speed and quality |
| Q4_0         | ~15 GB     | Good      | Lower VRAM systems                          |

## Downloading Models

### From Hugging Face

```bash
# Install huggingface-cli
pip install -U "huggingface_hub[cli]"

# Download a GGUF model
hf download <repo-id> --include "*.gguf" --local-dir /path/to/models/
```

### Manual Download

1. Navigate to the model repository on Hugging Face
2. Find the GGUF quantized files
3. Download using `wget` or browser
4. Place in your models directory

## Configuring a New Model

### Step 1: Set the Model Path

Add the model path to your `.env`:

```bash
# For Standard model
LLAMA_QWEN_3_6_27B_GGUF_MODEL_PATH=/path/to/model.gguf
```

### Step 2: Configure LiteLLM

Edit `interfaces/config/litellm/config.yaml` to add the model routing:

```yaml
model_list:
  - model_name: openai/your-model
    litellm_params:
      model: openai/qwen3.6_27b
      api_base: http://host.docker.internal:8000
      api_key: "not-needed"
```

### Step 3: Update Chat Template

If the model uses a different chat template, place it in `interfaces/config/`:

```
./config/your-model/chat_template.jinja:/workspace/chat_template.jinja:ro
```

## Converting Models to GGUF

If you have a model in safetensors format, convert it using llama.cpp tools:

```bash
# From third-party/llama.cpp/
python3 convert_hf_to_gguf.py /path/to/model --outfile /path/to/output.gguf
```

## Testing the Model

After configuration, test the model through LiteLLM:

```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -d '{
    "model": "openai/your-model",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 50
  }' | python3 -m json.tool | head -30
```

## Model Storage Best Practices

- Store models on a fast local disk (NVMe recommended)
- Keep models outside the Docker volumes for persistence
- Use bind mounts to make models available to containers
- Document model sources and licenses in your deployment notes
