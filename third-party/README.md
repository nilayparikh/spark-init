# Third-Party — Vendored Dependencies

External dependencies vendored as git submodules for the `.init` stack.

## Contents

| Path | Upstream | License | Purpose |
|---|---|---|---|
| `llama.cpp/` | [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp) | MIT | GPU-accelerated LLM inference backend |

## llama.cpp

The inference engine that runs Qwen 3.6 models on the DGX Spark. All inference in `.init` routes through llama.cpp.

### Why llama.cpp (Not vLLM)

DGX Spark (GB10, SM120/SM121) is an edge-tier Blackwell chip. vLLM's optimized NVFP4 kernels require:

- **TMEM** (Tensor Memory) — 256 KB per SM, found only in datacenter SM100+. DGX Spark doesn't have it.
- **Driver ≥ 595** — DGX Spark ships with 580.x. Forcing an upgrade can break the unified memory fabric.

llama.cpp works on DGX Spark because GGUF format loads weights directly into GPU memory — no layout transformations, no kernel fallbacks, no TMEM dependency.

### Building for DGX Spark

Build llama.cpp with CUDA support targeting SM121 (Blackwell on DGX Spark):

```bash
cd third-party/llama.cpp
mkdir build && cd build

cmake .. \
  -DGGML_CUDA=ON \
  -DCMAKE_CUDA_ARCHITECTURES="121" \
  -DLLAMA_CURL=OFF \
  -DCMAKE_BUILD_TYPE=Release

make -j16
```

Key flags explained:

| Flag | Value | Why |
|---|---|---|
| `-DGGML_CUDA=ON` | — | Enables CUDA backend for GPU inference |
| `-DCMAKE_CUDA_ARCHITECTURES="121"` | SM121 | Targets DGX Spark's Blackwell GPU. **Do not use "all"** — building for every arch bloats the binary and may invoke incompatible kernels. |
| `-DLLAMA_CURL=OFF` | — | Disables remote model download (models are local submodules) |
| `DCMAKE_BUILD_TYPE=Release` | — | Optimized binary |

### Docker Build

The CI and dockerfiles build the image using these same flags. See `interfaces/dockerfiles/Dockerfile` for the production build.

### Updating

```bash
git submodule update --init --recursive
cd third-party/llama.cpp
git fetch origin
git checkout <desired-tag-or-commit>
cd ../..
git add third-party/llama.cpp
git commit -m "chore: update llama.cpp to <tag>"
```

### Notes

- This is a read-only submodule. Changes to llama.cpp source should be contributed upstream at [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp).
- The upstream project does not accept AI-generated PRs. See their `AGENTS.md` and `CONTRIBUTING.md` before contributing.
- The `.init` stack pins a specific llama.cpp commit tag via `LLAMA_CPP_TAG` in `.env`.
