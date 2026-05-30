import os
from litellm import completion

# 1. Configure the API key and Base URL
os.environ["NVIDIA_NIM_API_KEY"] = "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"

# OPTIONAL: Only set this if you are self-hosting a local NIM endpoint.
# Default points to hosted NVIDIA API Catalog: https://integrate.api.nvidia.com/v1
# os.environ["NVIDIA_NIM_API_BASE"] = "http://localhost:8000/v1"

# 2. Add the 'nvidia_nim/' prefix to your target model
response = completion(
    model="nvidia_nim/minimaxai/minimax-m2.7",
    messages=[{"role": "user", "content": "Hello! How do I optimize code?"}],
)

print(response.choices[0].message.content)


# from openai import OpenAI

# client = OpenAI(
#     base_url="https://integrate.api.nvidia.com/v1",
#     api_key="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",
# )

# completion = client.chat.completions.create(
#     model="minimaxai/minimax-m2.7",
#     messages=[{"role": "user", "content": ""}],
#     temperature=1,
#     top_p=0.95,
#     max_tokens=8192,
#     stream=True,
# )

# for chunk in completion:
#     if not getattr(chunk, "choices", None):
#         continue
#     if chunk.choices[0].delta.content is not None:
#         print(chunk.choices[0].delta.content, end="")
