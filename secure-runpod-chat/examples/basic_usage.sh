#!/bin/bash

# Basic usage examples for secure-runpod-chat

echo "=== Example 1: Small, fast model ===" # Good for testing and simple tasks
secure-runpod-chat --model meta-llama/Llama-3.2-3B-Instruct

echo "=== Example 2: Vision-language model ==="
# Supports both text and image inputs
secure-runpod-chat --model meta-llama/Llama-3.2-11B-Vision-Instruct

echo "=== Example 3: Large model with quantization ==="
# Reduces VRAM requirements by ~75%
secure-runpod-chat --model meta-llama/Llama-3.2-70B-Instruct --quantize

echo "=== Example 4: Set cost limit ==="
# Prevents creating instances above cost threshold
secure-runpod-chat --model meta-llama/Llama-3.2-3B-Instruct --max-cost-per-hour 0.50

echo "=== Example 5: Custom GPU selection ==="
# Manually specify GPU type
secure-runpod-chat --model meta-llama/Llama-3.2-3B-Instruct --gpu-type "NVIDIA A40"

echo "=== Example 6: Large disk size ==="
# Useful for models with many files
secure-runpod-chat --model meta-llama/Llama-3.2-70B-Instruct --disk-size 100

echo "=== Example 7: No chat history ==="
# Disable encrypted chat history saving
secure-runpod-chat --model meta-llama/Llama-3.2-3B-Instruct --no-history

echo "=== Example 8: Use transformers instead of vLLM ==="
# Some models work better with transformers
secure-runpod-chat --model meta-llama/Llama-3.2-3B-Instruct --no-vllm
