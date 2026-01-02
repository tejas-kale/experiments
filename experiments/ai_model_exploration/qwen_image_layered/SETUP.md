# Qwen-Image-Layered - Setup Guide

This guide will walk you through installing and configuring the Qwen-Image-Layered CLI tool.

## Prerequisites

- Python 3.11+
- macOS (developed and tested)
- Runpod account with at least $9 in credits
- Runpod API key from [Settings](https://www.runpod.io/console/user/settings)

---

## Step 1: Install the CLI Tool

### Option A: Install as a uv Tool (Recommended)

This is the simplest method and makes the tool available globally:

```bash
uv tool install qwen-image-layered
```

Or install from source:

```bash
git clone https://github.com/tejas-kale/experiments.git
cd experiments/experiments/ai_model_exploration/qwen_image_layered
uv tool install .
```

### Option B: Install in a Virtual Environment

If you prefer to use a virtual environment:

```bash
# Clone the repository
git clone https://github.com/tejas-kale/experiments.git
cd experiments/experiments/ai_model_exploration/qwen_image_layered

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On macOS/Linux

# Install the package in editable mode
uv pip install -e .
```

---

## Step 2: Configure Runpod

The configure command will automatically create a Runpod template and endpoint for you.

### Get Your API Key

1. Go to [Runpod Console → Settings](https://www.runpod.io/console/user/settings)
2. Copy your API key

### Run the Configure Command

```bash
export RUNPOD_API_KEY=your_actual_api_key_here
qwen-image-layered configure
```

This will:
1. Create a Runpod template named `qwen-image-layered` with:
   - Base image: `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04`
   - Container disk: 25 GB
   - Required dependencies (diffusers, transformers, torch, etc.)
2. Deploy a serverless endpoint named `qwen-image-layered` with:
   - GPU: RTX 3090 (24GB VRAM)
   - Min workers: 0 (auto-scaling)
   - Max workers: 1
   - Idle timeout: 5 seconds
   - Max execution time: 600 seconds
3. Save configuration to `~/.qwen-image-layered/config.json`

### Customize Configuration (Optional)

You can customize the GPU type or Docker image:

```bash
# Use a different GPU
qwen-image-layered configure --gpu-type "NVIDIA RTX 4090"

# Use a custom Docker image
qwen-image-layered configure --docker-image custom/image:tag

# Combine options
qwen-image-layered configure \
  --gpu-type "NVIDIA RTX A5000" \
  --docker-image runpod/pytorch:latest
```

---

## Step 3: Verify Configuration

Check that everything is set up correctly:

```bash
qwen-image-layered info
```

You should see:
- API Key (partially masked)
- Endpoint ID
- Template ID
- Docker Image
- GPU Type
- Config file location

---

## Step 4: Test It!

Generate your first set of layers:

```bash
# Download a test image or use your own
qwen-image-layered generate your_test_image.jpg --layers 4
```

The first generation will take 5-10 minutes as the model (~10GB) is downloaded. Subsequent generations will be much faster (~2-3 minutes).

---

## What Gets Created on Runpod/

### Template

A Runpod template is created with:
- **Name**: `qwen-image-layered`
- **Purpose**: Defines the container image and dependencies
- **Location**: [Runpod Templates](https://www.runpod.io/console/serverless/user/templates)

### Endpoint

A serverless endpoint is created with:
- **Name**: `qwen-image-layered`
- **Purpose**: Runs inference jobs on-demand
- **Location**: [Runpod Serverless](https://www.runpod.io/console/serverless)

### Auto-Scaling Behavior

The endpoint is configured to auto-scale from 0 workers, which means:
- ✅ You're only charged when actively running inference
- ✅ Idle timeout of 5 seconds stops the worker when not in use
- ✅ No charges when the CLI is not in use

---

## Configuration File

The configuration is stored at `~/.qwen-image-layered/config.json` and contains:

```json
{
  "api_key": "your_runpod_api_key",
  "endpoint_id": "abc123def456",
  "template_id": "xyz789uvw012",
  "docker_image": "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04",
  "gpu_type": "NVIDIA RTX 3090"
}
```

You can manually edit this file if needed, or reconfigure using:

```bash
qwen-image-layered configure
```

---

## Cost Management

### Expected Costs

- **RTX 3090**: ~$0.24/hour
  - Typical generation: ~5-6 minutes
  - Cost per image: ~$0.02-0.024
  - Your $9 budget: ~375-450 images

- **RTX 4090**: ~$0.44/hour (faster, more expensive)
- **RTX A5000**: ~$0.34/hour (balanced)

### Tips to Minimize Costs

1. Use RTX 3090 (best cost/performance ratio)
2. The endpoint auto-scales to 0 workers when idle
3. 5-second idle timeout minimizes waste
4. Only process images when needed (no always-on costs)

---

## GPU Options

| GPU | VRAM | Cost/Hour | Best For |
|-----|------|-----------|----------|
| RTX 3090 | 24GB | $0.24 | Recommended (best cost/performance) |
| RTX A5000 | 24GB | $0.34 | Alternative if 3090 unavailable |
| RTX 4090 | 24GB | $0.44 | Fastest, but more expensive |

All GPUs support:
- bfloat16 precision (default)
- 640px and 1024px resolutions
- 3, 4, or 8 layers

---

## Troubleshooting

### "RUNPOD_API_KEY not found"

**Solution**: Set the environment variable before running configure:
```bash
export RUNPOD_API_KEY=your_key
qwen-image-layered configure
```

### Configuration fails with "insufficient credits"

**Solution**:
1. Check your Runpod account balance
2. Add credits at [Runpod Console → Billing](https://www.runpod.io/console/user/billing)
3. Retry the configure command

### Template or endpoint creation fails

**Solution**:
1. Check Runpod API status
2. Try a different GPU type: `--gpu-type "NVIDIA RTX A5000"`
3. Check the [Runpod Console](https://www.runpod.io/console/serverless) for error messages
4. Delete any partially created resources and retry

### "Not configured yet" when running generate

**Solution**: Run the configure command first:
```bash
export RUNPOD_API_KEY=your_key
qwen-image-layered configure
```

### Want to start over?

Delete the configuration and reconfigure:

```bash
rm -rf ~/.qwen-image-layered
qwen-image-layered configure
```

---

## Environment Variables

You can override configuration file settings using environment variables:

- `RUNPOD_API_KEY`: Runpod API key (required for configure)
- `RUNPOD_ENDPOINT_ID`: Override configured endpoint
- `RUNPOD_TEMPLATE_ID`: Override configured template
- `RUNPOD_GPU_TYPE`: Override configured GPU type

---

## Next Steps

See [README.md](README.md) for usage instructions, test cases, and examples!

### Quick Commands

```bash
# View configuration
qwen-image-layered info

# Generate layers from an image
qwen-image-layered generate image.jpg

# Customize generation
qwen-image-layered generate image.jpg \
  --layers 8 \
  --resolution 1024 \
  --steps 50 \
  --output-dir ./my_layers
```
