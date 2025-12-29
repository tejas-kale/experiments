# Chatterbox TTS Serverless Dockerfile for Runpod
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install Chatterbox TTS and huggingface-hub
RUN pip install --no-cache-dir chatterbox-tts runpod huggingface-hub

# Copy handler
COPY runpod_handler.py /app/handler.py

# Run handler
CMD ["python", "/app/handler.py"]
