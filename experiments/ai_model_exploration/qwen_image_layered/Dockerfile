# Qwen-Image-Layered Serverless Dockerfile for Runpod
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    git+https://github.com/huggingface/diffusers \
    transformers>=4.51.3 \
    torch \
    torchvision \
    runpod

# Copy handler
COPY runpod_handler.py /app/handler.py

# Run handler
CMD ["python", "/app/handler.py"]
