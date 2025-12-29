# GitHub-Based Runpod Setup Guide

This guide uses Runpod's GitHub integration for the simplest setup experience.

## Prerequisites

- GitHub account with your experiments repo
- Runpod account with API key
- At least $9 in Runpod credits

---

## Setup Steps

### 1. Connect GitHub to Runpod (One-Time)

1. Go to [Runpod Serverless](https://www.runpod.io/console/serverless)
2. Click **"New Endpoint"**
3. Click **"Connect GitHub"** (blue button)
4. Authorize Runpod to access your GitHub account
5. Select your `experiments` repository

---

### 2. Deploy Chatterbox TTS

#### A. Create Endpoint from GitHub

1. After connecting GitHub, you'll see your repositories
2. Select `tejas-kale/experiments`
3. Configure the endpoint:

   **Endpoint Name**: `chatterbox-tts`

   **Branch**: `main`

   **Docker Build Context**: `experiments/ai_model_exploration/chatterbox_tts`

   **Dockerfile Path**: `experiments/ai_model_exploration/chatterbox_tts/Dockerfile`

#### B. Select GPU

**Recommended**: `NVIDIA RTX 3060 Ti (8GB)`
- Cost: ~$0.14/hour
- Perfect for Chatterbox TTS

#### C. Configure Scaling

**Workers**:
- Min: `0` (auto-scale from zero - saves money!)
- Max: `1`

**Timeouts**:
- Idle: `5 seconds`
- Execution: `600 seconds` (10 minutes)

#### D. Set Environment Variables

**IMPORTANT**: Chatterbox Turbo requires a Hugging Face token to download the model.

1. Get your Hugging Face token:
   - Go to https://huggingface.co/settings/tokens
   - Create a new token (read access is sufficient)
   - Copy the token

2. In the Runpod endpoint configuration, add environment variable:
   - **Name**: `HF_TOKEN`
   - **Value**: Your Hugging Face token (paste it here)

#### E. Deploy

1. Click **"Deploy"**
2. Wait 2-3 minutes for build (first time only)
3. Copy the **Endpoint ID** from the endpoint details page

#### F. Configure Local Environment

```bash
cd experiments/ai_model_exploration/chatterbox_tts
cp .env.example .env
```

Edit `.env`:
```
RUNPOD_API_KEY=your_api_key_here
RUNPOD_ENDPOINT_ID=your_endpoint_id_here
```

#### G. Test It

```bash
python cli.py speak "Hello! Testing Chatterbox TTS." --exaggeration 1.5
```

---

### 3. Deploy Qwen-Image-Layered

Repeat the same process:

#### A. Create New Endpoint

1. Click **"New Endpoint"**
2. Select `tejas-kale/experiments`
3. Configure:

   **Endpoint Name**: `qwen-image-layered`

   **Branch**: `main`

   **Docker Build Context**: `experiments/ai_model_exploration/qwen_image_layered`

   **Dockerfile Path**: `experiments/ai_model_exploration/qwen_image_layered/Dockerfile`

#### B. Select GPU

**Recommended**: `NVIDIA RTX 3090 (24GB)`
- Cost: ~$0.24/hour
- Required: 24GB VRAM minimum

#### C. Configure Scaling

Same as Chatterbox:
- Min Workers: `0`
- Max Workers: `1`
- Idle Timeout: `5 seconds`
- Execution Timeout: `600 seconds`

#### D. Deploy & Configure

```bash
cd experiments/ai_model_exploration/qwen_image_layered
cp .env.example .env
```

Edit `.env` with your endpoint ID.

#### E. Test It

```bash
python cli.py generate your_image.jpg --layers 4
```

---

## Advantages of GitHub Integration

✅ **Automatic Rebuilds**: Push to GitHub → Runpod rebuilds automatically
✅ **Version Control**: Each deployment tied to a git commit
✅ **No Manual Templates**: Runpod reads Dockerfile directly
✅ **Easier Updates**: Just push to GitHub and redeploy
✅ **Build Logs**: See full Docker build output in Runpod console

---

## GitHub Webhook (Optional)

Enable automatic redeployment on git push:

1. Go to endpoint settings
2. Enable **"Auto-deploy on push"**
3. Runpod adds webhook to your GitHub repo
4. Every push to `main` branch triggers rebuild

---

## Cost Comparison

### Chatterbox TTS
- GPU: RTX 3060 Ti @ $0.14/hour
- Per clip: ~$0.007-0.01
- $9 budget: ~900-1,285 clips

### Qwen-Image-Layered
- GPU: RTX 3090 @ $0.24/hour
- Per image: ~$0.02-0.024
- $9 budget: ~375-450 images

**With auto-scaling (min=0)**: Only pay when running inference!

---

## Troubleshooting

### Build Fails

**Check Dockerfile path**: Must be relative to repo root
- Correct: `experiments/ai_model_exploration/chatterbox_tts/Dockerfile`
- Wrong: `Dockerfile` or `chatterbox_tts/Dockerfile`

**Check build context**: Should match Dockerfile directory
- Context: `experiments/ai_model_exploration/chatterbox_tts`

### Endpoint Not Ready

First build takes 5-10 minutes (downloads models). Check build logs in Runpod console.

### Hugging Face Token Error

**Error**: `Token is required, but no token found`

**Solution**:
1. Verify HF_TOKEN is set in endpoint environment variables
2. Get token from https://huggingface.co/settings/tokens
3. In Runpod endpoint settings, add:
   - Name: `HF_TOKEN`
   - Value: Your Hugging Face token
4. Rebuild/restart the endpoint after adding the token

### GitHub Connection Issues

Revoke and reconnect:
1. GitHub Settings → Applications → Runpod
2. Revoke access
3. Reconnect in Runpod console

---

## Alternative: Docker Registry Method

If you prefer not to connect GitHub, use the **"Import from Docker Registry"** option and follow the original `SETUP.md` guides.

---

## Next Steps

1. Connect GitHub to Runpod
2. Deploy Chatterbox TTS endpoint
3. Deploy Qwen-Image-Layered endpoint
4. Run test cases from READMEs
5. Experiment with your own inputs!
