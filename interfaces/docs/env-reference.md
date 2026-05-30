# Interface Env Reference

The interface compose file now carries inline defaults for every supported override.
Keep only the values you actually want to change in the root `.env`; `.env.example`
intentionally lists the smaller set of common overrides and secrets. The tables
below remain a full reference for supported interface env vars.

## Compose Profile Switchboard

| Variable           | Default                                 | Used by         | Meaning                                                                                                    |
| ------------------ | --------------------------------------- | --------------- | ---------------------------------------------------------------------------------------------------------- |
| `COMPOSE_PROFILES` | `data,obs,interface,llama-qwen-3-6-27b` | root compose UX | Full active stack shape selected by the root `.env`. Set this once, then use plain `docker compose up -d`. |

## LiteLLM Proxy

| Variable                          | Default                                    | Used by                                | Meaning                                                                                                                  |
| --------------------------------- | ------------------------------------------ | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `LITELLM_IMAGE`                   | `docker.litellm.ai/berriai/litellm:latest` | compose                                | LiteLLM container image.                                                                                                 |
| `LITELLM_CONTAINER_NAME`          | `litellm`                                  | compose                                | Container name for the proxy.                                                                                            |
| `LITELLM_BIND_HOST`               | `0.0.0.0`                                  | compose                                | Host bind address for the proxy port.                                                                                    |
| `LITELLM_PORT`                    | `4000`                                     | compose                                | External and internal proxy port.                                                                                        |
| `LITELLM_LOG_LEVEL`               | `INFO`                                     | compose                                | LiteLLM logging level.                                                                                                   |
| `LITELLM_MASTER_KEY`              | `sk-interface-ui-local`                    | compose, clients                       | Admin / bearer key for authenticated proxy access. Clients must send the raw `sk-...` key, not a hashed dashboard token. |
| `INTERFACE_DATABASE_URL`          | `postgresql://.../litellm_interface`       | compose -> `DATABASE_URL`              | Postgres connection string that compose maps into LiteLLM's canonical `DATABASE_URL` env var.                            |
| `INTERFACE_QWEN_3_6_27B_BASE_URL` | `http://host.docker.internal:8000/v1`      | compose -> `QWEN3_6_27B_BASE_URL`      | Upstream OpenAI-compatible URL for the active 27B backend.                                                               |
| `INTERFACE_QWEN_3_6_27B_API_KEY`  | `sk-dummy`                                 | compose -> `QWEN3_6_27B_API_KEY`       | Placeholder upstream API key accepted by the local backends.                                                             |
| `INTERFACE_QWEN_3_6_27B_MODEL`    | `openai/qwen3.6_27b`                       | compose -> `QWEN3_6_27B_SERVING_MODEL` | Upstream model identifier LiteLLM will call.                                                                             |

## LiteLLM Hosted Models

| Variable                           | Default                             | Used by            | Meaning                                                         |
| ---------------------------------- | ----------------------------------- | ------------------ | --------------------------------------------------------------- |
| `DEEPSEEK_V4_FLASH_API_BASE`       | unset                               | compose -> LiteLLM | OpenAI-compatible base URL for `deepseek-ai/deepseek-v4-flash`. |
| `DEEPSEEK_V4_FLASH_API_KEY`        | unset                               | compose -> LiteLLM | API key for DeepSeek Flash.                                     |
| `DEEPSEEK_V4_FLASH_MODEL`          | `deepseek-ai/deepseek-v4-flash`     | compose -> LiteLLM | Model identifier for DeepSeek Flash.                            |
| `GEMMA_4_31B_IT_API_BASE`          | unset                               | compose -> LiteLLM | OpenAI-compatible base URL for `google/gemma-4-31b-it`.         |
| `GEMMA_4_31B_IT_API_KEY`           | unset                               | compose -> LiteLLM | API key for Gemma.                                              |
| `GEMMA_4_31B_IT_MODEL`             | `google/gemma-4-31b-it`             | compose -> LiteLLM | Model identifier for Gemma 4 31B IT.                            |
| `QWEN_3_5_397B_A17B_API_BASE`      | unset                               | compose -> LiteLLM | OpenAI-compatible base URL for `qwen/qwen3.5-397b-a17b`.        |
| `QWEN_3_5_397B_A17B_API_KEY`       | unset                               | compose -> LiteLLM | API key for Qwen 3.5.                                           |
| `QWEN_3_5_397B_A17B_MODEL`         | `qwen/qwen3.5-397b-a17b`            | compose -> LiteLLM | Model identifier for Qwen 3.5.                                  |
| `MINIMAX_M2_7_API_BASE`            | unset                               | compose -> LiteLLM | OpenAI-compatible base URL for `minimaxai/minimax-m2.7`.        |
| `MINIMAX_M2_7_API_KEY`             | unset                               | compose -> LiteLLM | API key for MiniMax.                                            |
| `MINIMAX_M2_7_MODEL`               | `minimaxai/minimax-m2.7`            | compose -> LiteLLM | Model identifier for MiniMax M2.7.                              |
| `KIMI_K2_6_API_BASE`               | unset                               | compose -> LiteLLM | OpenAI-compatible base URL for `moonshotai/kimi-k2.6`.          |
| `KIMI_K2_6_API_KEY`                | unset                               | compose -> LiteLLM | API key for Kimi K2.6.                                          |
| `KIMI_K2_6_MODEL`                  | `moonshotai/kimi-k2.6`              | compose -> LiteLLM | Model identifier for Kimi K2.6.                                 |
| `NEMOTRON_3_SUPER_120B_A12B_MODEL` | `nvidia/nemotron-3-super-120b-a12b` | compose -> LiteLLM | Model identifier for Nemotron 3 Super 120B A12B.                |

## Microsoft Foundry Orchestrator Model

| Variable                     | Default                                        | Used by        | Meaning                                     |
| ---------------------------- | ---------------------------------------------- | -------------- | ------------------------------------------- |
| `MICROSOFT_FOUNDRY_API_BASE` | `https://tuts.services.ai.azure.com/openai/v1` | LiteLLM config | Remote endpoint for the orchestrator model. |
| `MICROSOFT_FOUNDRY_API_KEY`  | empty in `.env.example`                        | LiteLLM config | Remote API key.                             |
| `AZURE_ORCHESTRATOR_MODEL`   | `openai/Kimi-K2.6-1`                           | LiteLLM config | Remote model identifier.                    |

## llama-qwen-3-6-27b

| Variable                                                              | Default                     | Meaning                                                   |
| --------------------------------------------------------------------- | --------------------------- | --------------------------------------------------------- |
| `LLAMA_CPP_TAG`                                                       | `b9222`                     | Upstream llama.cpp tag used by the Docker build.          |
| `LLAMA_QWEN_3_6_27B_IMAGE_REPO`                                       | `nilayparikh/llama-cpp-dgx` | Image repository prefix for the composed llama.cpp image. |
| `LLAMA_QWEN_3_6_27B_CONTAINER_NAME`                                   | `localm-llama-qwen-3-6-27b` | Container name.                                           |
| `LLAMA_QWEN_3_6_27B_GGUF_MODEL_PATH`                                  | local GGUF path             | Mounted model file path.                                  |
| `LLAMA_QWEN_3_6_27B_BINARY_PATH`                                      | local llama-server path     | Host-side binary path used by `llama-mtp.sh`.             |
| `LLAMA_QWEN_3_6_27B_BIND_HOST`                                        | `0.0.0.0`                   | Host bind address for the containerized backend.          |
| `LLAMA_QWEN_3_6_27B_HOST`                                             | `0.0.0.0`                   | Listen address passed into `llama-server`.                |
| `LLAMA_QWEN_3_6_27B_HOST_PORT`                                        | `8000`                      | Host port exposed by compose.                             |
| `LLAMA_QWEN_3_6_27B_CONTAINER_PORT`                                   | `8080`                      | Port the containerized backend listens on internally.     |
| `LLAMA_QWEN_3_6_27B_SCRIPT_PORT`                                      | `8000`                      | Port used by the host-side launcher script.               |
| `LLAMA_QWEN_3_6_27B_SERVED_MODEL_NAME`                                | `qwen3.6_27b`               | OpenAI-compatible served model name.                      |
| `LLAMA_QWEN_3_6_27B_REASONING`                                        | `on`                        | Enables reasoning mode.                                   |
| `LLAMA_QWEN_3_6_27B_TEMPERATURE`                                      | `0.15`                      | Sampling temperature.                                     |
| `LLAMA_QWEN_3_6_27B_TOP_P`                                            | `0.92`                      | Top-p sampling value.                                     |
| `LLAMA_QWEN_3_6_27B_TOP_K`                                            | `10`                        | Top-k sampling value.                                     |
| `LLAMA_QWEN_3_6_27B_PRESENCE_PENALTY`                                 | `0.0`                       | Presence penalty.                                         |
| `LLAMA_QWEN_3_6_27B_FREQUENCY_PENALTY`                                | `1.03`                      | Frequency penalty.                                        |
| `LLAMA_QWEN_3_6_27B_MIN_P`                                            | `0.05`                      | Minimum probability cutoff.                               |
| `LLAMA_QWEN_3_6_27B_SPEC_TYPE`                                        | `draft-mtp`                 | Speculative decoding mode.                                |
| `LLAMA_QWEN_3_6_27B_SPEC_DRAFT_N_MAX`                                 | `3`                         | Max speculative draft tokens.                             |
| `LLAMA_QWEN_3_6_27B_SPEC_DRAFT_P_MIN`                                 | `0.75`                      | Draft acceptance floor.                                   |
| `LLAMA_QWEN_3_6_27B_CACHE_TYPE_K` / `LLAMA_QWEN_3_6_27B_CACHE_TYPE_V` | `q8_0`                      | KV cache quantization.                                    |
| `LLAMA_QWEN_3_6_27B_GPU_LAYERS`                                       | `all`                       | GPU layer offload setting.                                |
| `LLAMA_QWEN_3_6_27B_FLASH_ATTN`                                       | `on`                        | Flash attention toggle.                                   |
| `LLAMA_QWEN_3_6_27B_SPLIT_MODE`                                       | `none`                      | Multi-GPU split mode.                                     |
| `LLAMA_QWEN_3_6_27B_FAKE_PROMPT`                                      | `off`                       | `-fit` flag value.                                        |
| `LLAMA_QWEN_3_6_27B_CONTEXT_SIZE`                                     | `131072`                    | Advertised context length.                                |
| `LLAMA_QWEN_3_6_27B_BATCH_SIZE`                                       | `3072`                      | Batch size.                                               |
| `LLAMA_QWEN_3_6_27B_UBATCH_SIZE`                                      | `768`                       | Micro-batch size.                                         |
| `LLAMA_QWEN_3_6_27B_PARALLEL`                                         | `1`                         | Concurrent slot count.                                    |
| `LLAMA_QWEN_3_6_27B_CACHE_REUSE`                                      | `64`                        | Prompt cache reuse depth.                                 |
| `LLAMA_QWEN_3_6_27B_THREADS` / `LLAMA_QWEN_3_6_27B_THREADS_BATCH`     | `4`                         | CPU thread counts.                                        |
| `LLAMA_QWEN_3_6_27B_TIMEOUT`                                          | `120`                       | Request timeout in seconds.                               |

## Shared vLLM Runtime

| Variable                                  | Default                      | Meaning                                                      |
| ----------------------------------------- | ---------------------------- | ------------------------------------------------------------ |
| `VLLM_RUNTIME_ALLOW_LONG_MAX_MODEL_LEN`   | `1`                          | Enables long max-model-len support.                          |
| `VLLM_RUNTIME_TORCH_CUDA_ARCH_LIST`       | `12.1f`                      | CUDA architecture list.                                      |
| `VLLM_RUNTIME_PYTORCH_CUDA_ALLOC_CONF`    | `expandable_segments:True`   | PyTorch allocator setting.                                   |
| `VLLM_RUNTIME_NVIDIA_FORWARD_COMPAT`      | `1`                          | Enables NVIDIA forward compatibility checks bypass.          |
| `VLLM_RUNTIME_NVIDIA_DISABLE_REQUIRE`     | `1`                          | Disables strict NVIDIA image require checks.                 |
| `VLLM_RUNTIME_NVIDIA_VISIBLE_DEVICES`     | `all`                        | NVIDIA visible devices passed into container.                |
| `VLLM_RUNTIME_NVIDIA_DRIVER_CAPABILITIES` | `compute,utility`            | Required NVIDIA driver capabilities.                         |
| `VLLM_RUNTIME_USE_TRITON_FLASH_ATTN`      | `0`                          | Keeps Triton flash attention disabled when using FlashInfer. |
| `VLLM_RUNTIME_TORCH_MATMUL_PRECISION`     | `high`                       | Matmul precision preference.                                 |
| `VLLM_RUNTIME_HF_CACHE_HOST_PATH`         | `${HOME}/.cache/huggingface` | Host Hugging Face cache directory.                           |
| `VLLM_RUNTIME_HF_CACHE_DIR`               | `/root/.cache/huggingface`   | Container Hugging Face cache path.                           |
| `VLLM_RUNTIME_FLASHINFER_CACHE_HOST_PATH` | `${HOME}/.cache/flashinfer`  | Host FlashInfer cache directory.                             |
| `VLLM_RUNTIME_FLASHINFER_CACHE_DIR`       | `/root/.cache/flashinfer`    | Container FlashInfer cache path.                             |
| `VLLM_RUNTIME_TRITON_CACHE_HOST_PATH`     | local cache path             | Host Triton cache directory.                                 |
| `VLLM_RUNTIME_CACHE_HOST_PATH`            | local cache path             | Host vLLM cache directory.                                   |
| `VLLM_RUNTIME_TRITON_CACHE_MOUNT_DIR`     | `/root/.triton`              | Container Triton mount root path.                            |
| `VLLM_RUNTIME_TRITON_CACHE_DIR`           | `/root/.triton/cache`        | Container Triton cache path.                                 |
| `VLLM_RUNTIME_XDG_CACHE_HOME`             | `/root/.cache`               | Container cache home.                                        |
| `VLLM_RUNTIME_CACHE_DIR`                  | `/root/.cache/vllm`          | Container vLLM cache path.                                   |
| `VLLM_ENGINE_ITERATION_TIMEOUT_S`         | `300`                        | Engine iteration timeout.                                    |

## vllm-qwen-3-6-27b

This profile is pinned to the `spark-vllm-docker` `qwen3.6-27b-fp8-mtp` recipe defaults:
`rdtand/Qwen3.6-27B-PrismaQuant-5.5bit-vllm`, `nilayparikh/vllm-spark:v05-26`, `instanttensor`,
`flashinfer`, FP8 KV cache, `max-model-len 65536`, `max-num-batched-tokens 32768`,
`max-num-seqs 4`, `gpu-memory-utilization 0.80`, chunked prefill enabled, and an MTP speculative
config defaulting to two speculative tokens. The fixed chat template is mounted from
`../fixed_chat_template.jinja` to `/workspace/fixed_chat_template.user.jinja`.

| Variable                                 | Default                         | Meaning                                   |
| ---------------------------------------- | ------------------------------- | ----------------------------------------- |
| `VLLM_QWEN_3_6_27B_IMAGE`                | `nilayparikh/vllm-spark:v05-26` | Image tag for the pinned 27B runtime.     |
| `VLLM_QWEN_3_6_27B_CONTAINER_NAME`       | `localm-vllm-qwen-3-6-27b`      | Container name.                           |
| `VLLM_QWEN_3_6_27B_MAX_NUM_SEQS`         | `4`                             | Maximum concurrent requests/sequences.    |
| `VLLM_QWEN_3_6_27B_CUDA_VISIBLE_DEVICES` | unset                           | Optional GPU pinning for shared-GPU mode. |

## vllm-qwen-3-6-35b-a3b

This profile is pinned to the `spark-vllm-docker` `qwen3.6-35b-a3b-fp8` recipe defaults,
with MTP speculative decoding enabled and a compose-level memory cap of `49g`.

| Variable                                       | Default                                       | Meaning                                     |
| ---------------------------------------------- | --------------------------------------------- | ------------------------------------------- |
| `VLLM_QWEN_3_6_35B_A3B_CONTAINER_NAME`         | `localm-vllm-qwen-3-6-35b-a3b`                | Container name.                             |
| `VLLM_QWEN_3_6_35B_A3B_IMAGE`                  | `nilayparikh/vllm-spark:v05-26`               | Image tag for the 35B runtime.              |
| `VLLM_QWEN_3_6_35B_A3B_MODEL`                  | `Qwen/Qwen3.6-35B-A3B-FP8`                    | Hugging Face model id used by the launcher. |
| `VLLM_QWEN_3_6_35B_A3B_SERVED_MODEL_NAME`      | `qwen3.6_35b_a3b`                             | Served model name.                          |
| `VLLM_QWEN_3_6_35B_A3B_PORT`                   | `8001`                                        | Host-network port.                          |
| `VLLM_QWEN_3_6_35B_A3B_TENSOR_PARALLEL_SIZE`   | `1`                                           | Tensor parallel degree.                     |
| `VLLM_QWEN_3_6_35B_A3B_DTYPE`                  | `auto`                                        | Runtime dtype.                              |
| `VLLM_QWEN_3_6_35B_A3B_MAX_MODEL_LEN`          | `100352`                                      | Maximum model length.                       |
| `VLLM_QWEN_3_6_35B_A3B_MAX_NUM_BATCHED_TOKENS` | `32768`                                       | Batched token cap.                          |
| `VLLM_QWEN_3_6_35B_A3B_GPU_MEMORY_UTILIZATION` | `0.385`                                       | GPU memory target.                          |
| `VLLM_QWEN_3_6_35B_A3B_LOAD_FORMAT`            | `fastsafetensors`                             | Model loading format.                       |
| `VLLM_QWEN_3_6_35B_A3B_ATTENTION_BACKEND`      | `flash_attn`                                  | Attention backend CLI flag.                 |
| `VLLM_QWEN_3_6_35B_A3B_TOOL_CALL_PARSER`       | `qwen3_xml`                                   | Tool-call parser.                           |
| `VLLM_QWEN_3_6_35B_A3B_REASONING_PARSER`       | `qwen3`                                       | Reasoning parser.                           |
| `VLLM_QWEN_3_6_35B_A3B_CHAT_TEMPLATE`          | `fixed_chat_template.jinja`                   | Chat template used by the launcher.         |
| `VLLM_QWEN_3_6_35B_A3B_SPECULATIVE_CONFIG`     | `{"method":"mtp","num_speculative_tokens":2}` | Speculative decoding config JSON.           |
| `VLLM_QWEN_3_6_35B_A3B_CUDA_VISIBLE_DEVICES`   | unset                                         | Optional GPU pinning for shared-GPU mode.   |
| `VLLM_QWEN_3_6_35B_A3B_NVIDIA_FORWARD_COMPAT`  | `1`                                           | Forward compatibility toggle.               |
| `VLLM_QWEN_3_6_35B_A3B_NVIDIA_DISABLE_REQUIRE` | `1`                                           | Disables strict driver requirement checks.  |
| `VLLM_QWEN_3_6_35B_A3B_ENABLE_NVFP4_SM100`     | `0`                                           | NVFP4 SM100 toggle.                         |
| `VLLM_QWEN_3_6_35B_A3B_USE_FLASHINFER_MOE_FP4` | `0`                                           | FlashInfer MoE FP4 path toggle.             |
| `VLLM_QWEN_3_6_35B_A3B_TEST_FORCE_FP8_MARLIN`  | `0`                                           | FP8 Marlin force flag.                      |

If either backend is pinned to a single visible GPU through its `*_CUDA_VISIBLE_DEVICES` setting,
the launcher keeps the same model behavior but automatically drops the 35B backend to `tp=1` and
omits Ray so both services can share one GPU when necessary.
| `VLLM_QWEN_3_6_35B_A3B_USE_FLASHINFER_SAMPLER` | `1` | FlashInfer sampler toggle. |
| `VLLM_QWEN_3_6_35B_A3B_NVFP4_GEMM_BACKEND` | `flashinfer-cutlass` | GEMM backend selection. |

## Host Runtime Safeguards

The vLLM/Docker settings above reduce kernel and allocator instability, but a subset of
`Failed to initialize NVML: Unknown Error` failures come from host runtime drift (outside compose).
For DGX Spark hosts, check these items before changing model/runtime flags:

1. Recreate missing NVIDIA `/dev/char` links after driver or toolkit upgrades:
   `sudo nvidia-ctk system create-dev-char-symlinks --create-all`
2. Ensure Docker and NVIDIA runtime cgroup settings are consistent with your host `systemd` setup.
3. Keep `nvidia-container-toolkit` and driver versions aligned with your deployed CUDA stack.
