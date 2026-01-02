# Dockerfile for Qwen-Image-Layered Runpod deployment
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    git+https://github.com/huggingface/diffusers \
    transformers>=4.51.3 \
    torch \
    torchvision \
    pillow \
    runpod

# Copy handler script
COPY handler.py /app/handler.py

# Set the entrypoint
CMD ["python", "-u", "handler.py"]
