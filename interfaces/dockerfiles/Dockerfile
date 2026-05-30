# syntax=docker/dockerfile:1.7

FROM nvcr.io/nvidia/cuda:13.1.2-cudnn-devel-ubuntu24.04 AS builder

ARG LLAMA_CPP_TAG=master
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        cmake \
        git \
        libssl-dev \
        pkg-config && \
    rm -rf /var/lib/apt/lists/*

ENV CUDA_STUB=/usr/local/cuda/targets/sbsa-linux/lib/stubs
ENV LD_LIBRARY_PATH=${CUDA_STUB}:${LD_LIBRARY_PATH:-}
ENV LIBRARY_PATH=${CUDA_STUB}:${LIBRARY_PATH:-}

RUN ln -sf "${CUDA_STUB}/libcuda.so" "${CUDA_STUB}/libcuda.so.1"

WORKDIR /src

RUN git clone --depth 1 https://github.com/ggml-org/llama.cpp.git . && \
    if [ "${LLAMA_CPP_TAG}" != "master" ]; then \
      git fetch --depth 1 origin "refs/tags/${LLAMA_CPP_TAG}:refs/tags/${LLAMA_CPP_TAG}" && \
      git checkout "${LLAMA_CPP_TAG}"; \
    fi

RUN mkdir build && cd build && \
    cmake .. -DGGML_CUDA=ON \
             -DCMAKE_CUDA_ARCHITECTURES="121" \
             -DLLAMA_CURL=OFF \
             -DCMAKE_EXE_LINKER_FLAGS="-Wl,--allow-shlib-undefined -L${CUDA_STUB}" \
             -DCMAKE_SHARED_LINKER_FLAGS="-L${CUDA_STUB}" && \
    make -j"$(nproc)" llama-server && \
    mkdir -p /opt/llama-runtime && \
    cp -a \
        bin/llama-server \
        bin/libggml*.so* \
        bin/libllama*.so* \
        bin/libmtmd*.so* \
        /opt/llama-runtime/

FROM nvcr.io/nvidia/cuda:13.1.2-cudnn-runtime-ubuntu24.04 AS runtime

ENV DEBIAN_FRONTEND=noninteractive \
    LD_LIBRARY_PATH=/opt/llama-runtime:${LD_LIBRARY_PATH:-}

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        libgomp1 \
        libssl3 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt/llama-runtime

COPY --from=builder /opt/llama-runtime/ /opt/llama-runtime/

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD ["curl", "-f", "http://localhost:8080/health"]

ENTRYPOINT ["./llama-server"]