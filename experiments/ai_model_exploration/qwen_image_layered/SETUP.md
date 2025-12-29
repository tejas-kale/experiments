# Qwen-Image-Layered - Runpod Setup Guide

This guide will walk you through setting up a Runpod endpoint for Qwen-Image-Layered.

## Prerequisites

- Runpod account with at least $9 in credits
- Runpod API key from [Settings](https://www.runpod.io/console/user/settings)

## Step 1: Create a Runpod Template

1. Go to [Runpod Templates](https://www.runpod.io/console/serverless/user/templates)
2. Click **"New Template"**
3. Configure the template:

   **Template Name**: `qwen-image-layered`

   **Container Image**: `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04`

   **Container Disk**: `25 GB`

   **Docker Command**: (leave empty)

   **Start Command**:
   ```bash
   pip install git+https://github.com/huggingface/diffusers transformers>=4.51.3 torch torchvision && wget -O handler.py https://raw.githubusercontent.com/tejas-kale/experiments/main/experiments/ai_model_exploration/qwen_image_layered/runpod_handler.py && python handler.py
   ```

   **Environment Variables**: (none required)

4. Click **"Save Template"**

## Step 2: Create a Serverless Endpoint

1. Go to [Runpod Serverless](https://www.runpod.io/console/serverless)
2. Click **"New Endpoint"**
3. Configure the endpoint:

   **Endpoint Name**: `qwen-image-layered` (or any name you prefer)

   **Select Template**: Choose the `qwen-image-layered` template you just created

   **GPU Type**: Select `NVIDIA RTX 3090` (recommended - requires 24GB VRAM)

   **Min Workers**: `0` (auto-scale from zero)

   **Max Workers**: `1`

   **Idle Timeout**: `5 seconds` (saves money)

   **Max Execution Time**: `600 seconds`

4. Click **"Deploy"**

## Step 3: Get Your Endpoint ID

1. After deployment, you'll see your endpoint listed
2. Click on the endpoint name
3. Copy the **Endpoint ID** (looks like `abc123def456`)
4. Also copy your **API Key** from [Settings](https://www.runpod.io/console/user/settings)

## Step 4: Configure Your Local Environment

1. Navigate to the qwen_image_layered directory:
   ```bash
   cd experiments/ai_model_exploration/qwen_image_layered
   ```

2. Copy the example env file:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and add your credentials:
   ```
   RUNPOD_API_KEY=your_actual_api_key_here
   RUNPOD_ENDPOINT_ID=your_actual_endpoint_id_here
   ```

## Step 5: Install Dependencies

```bash
# Activate virtual environment
source ../../../.venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

## Step 6: Test It!

```bash
python cli.py generate your_test_image.jpg --layers 4
```

## Cost Management

**Important**: Your endpoint is configured to auto-scale from 0 workers, which means:
- ✅ You're only charged when actively running inference
- ✅ Idle timeout of 5 seconds stops the worker when not in use
- ✅ No charges when not using the CLI

**Expected Costs**:
- RTX 3090: ~$0.24/hour
- Typical generation: ~5-6 minutes = ~$0.02-0.024 per image
- Your $9 budget: ~375-450 images

## GPU Options

| GPU | VRAM | Cost/Hour | Best For |
|-----|------|-----------|----------|
| RTX 3090 | 24GB | $0.24 | Recommended (best cost/performance) |
| RTX A5000 | 24GB | $0.34 | Alternative if 3090 unavailable |
| RTX 4090 | 24GB | $0.44 | Fastest, but more expensive |

## Troubleshooting

### First Run is Slow
The first request will take 5-10 minutes as Runpod downloads the Qwen-Image-Layered model (~10GB). Subsequent requests will be much faster (~2-3 minutes).

### "Endpoint not ready" Error
Wait a few minutes after creating the endpoint before running the CLI. The endpoint needs time to initialize.

### "Job failed" Error
Check the Runpod logs:
1. Go to your endpoint in the Runpod console
2. Click "Logs" tab
3. Look for error messages

Common issues:
- Model download failed (retry - Hugging Face can be slow)
- Out of memory (ensure you're using RTX 3090 or better with 24GB VRAM)
- Handler script download failed (check GitHub URL)
- transformers version too old (ensure >= 4.51.3)

### "Out of Memory" Error
The model requires 24GB VRAM minimum. Solutions:
- Ensure you selected RTX 3090, A5000, or 4090
- Try resolution 640 instead of 1024
- Contact Runpod support if issue persists

## Next Steps

See [README.md](README.md) for usage instructions and test cases!
