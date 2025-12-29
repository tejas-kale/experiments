# Chatterbox TTS - Runpod Setup Guide

This guide will walk you through setting up a Runpod endpoint for Chatterbox TTS.

## Prerequisites

- Runpod account with at least $9 in credits
- Runpod API key from [Settings](https://www.runpod.io/console/user/settings)

## Step 1: Create a Runpod Template

1. Go to [Runpod Templates](https://www.runpod.io/console/serverless/user/templates)
2. Click **"New Template"**
3. Configure the template:

   **Template Name**: `chatterbox-tts`

   **Container Image**: `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04`

   **Container Disk**: `15 GB`

   **Docker Command**: (leave empty)

   **Start Command**:
   ```bash
   pip install chatterbox-tts && wget -O handler.py https://raw.githubusercontent.com/tejas-kale/experiments/main/experiments/ai_model_exploration/chatterbox_tts/runpod_handler.py && python handler.py
   ```

   **Environment Variables**: (none required)

4. Click **"Save Template"**

## Step 2: Create a Serverless Endpoint

1. Go to [Runpod Serverless](https://www.runpod.io/console/serverless)
2. Click **"New Endpoint"**
3. Configure the endpoint:

   **Endpoint Name**: `chatterbox-tts` (or any name you prefer)

   **Select Template**: Choose the `chatterbox-tts` template you just created

   **GPU Type**: Select `NVIDIA RTX 3060 Ti` (recommended for cost/performance)

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

1. Navigate to the chatterbox_tts directory:
   ```bash
   cd experiments/ai_model_exploration/chatterbox_tts
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
python cli.py speak "Hello! This is a test of the Chatterbox TTS system." --exaggeration 1.5
```

## Cost Management

**Important**: Your endpoint is configured to auto-scale from 0 workers, which means:
- ✅ You're only charged when actively running inference
- ✅ Idle timeout of 5 seconds stops the worker when not in use
- ✅ No charges when not using the CLI

**Expected Costs**:
- RTX 3060 Ti: ~$0.14/hour
- Typical generation: ~3-4 minutes = ~$0.007-0.01 per clip
- Your $9 budget: ~900-1,285 speech clips

## Troubleshooting

### First Run is Slow
The first request will take 3-5 minutes as Runpod downloads the Chatterbox model. Subsequent requests will be much faster (~30 seconds).

### "Endpoint not ready" Error
Wait a few minutes after creating the endpoint before running the CLI. The endpoint needs time to initialize.

### "Job failed" Error
Check the Runpod logs:
1. Go to your endpoint in the Runpod console
2. Click "Logs" tab
3. Look for error messages

Common issues:
- Model download failed (retry)
- Out of memory (try different GPU)
- Handler script download failed (check GitHub URL)

## Next Steps

See [README.md](README.md) for usage instructions and test cases!
