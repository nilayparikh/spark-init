mkdir build && cd build

cmake .. \
 -DGGML_CUDA=ON \
 -DCMAKE_CUDA_ARCHITECTURES="121" \
 -DLLAMA_CURL=OFF \
 -DCMAKE_BUILD_TYPE=Release

make -j16
