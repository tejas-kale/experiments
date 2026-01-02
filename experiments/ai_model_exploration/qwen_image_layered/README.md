# Qwen-Image-Layered on Runpod

> **⚠️ STATUS: EXPERIMENTAL & UNSTABLE**
> 
> **Current Issues (Jan 2026):**
> 1. **PyTorch Version Conflict:** The `diffusers` library (via `transformers`) requires PyTorch 2.3+ for `enable_gqa` support, but the Runpod environment may persistently default to PyTorch 2.1.0 despite upgrade attempts. This causes `unexpected keyword argument 'enable_gqa'` errors.
> 2. **Environment Persistence:** Upgrading the base Docker image in the template does not always guarantee a fresh environment on the endpoint due to caching.
> 3. **Workarounds Applied:**
>    - Explicitly forcing `torch>=2.4.0` installation in the handler.
>    - Using `enable_sequential_cpu_offload()` to mitigate VRAM limits.
>    - Increasing container disk to 80GB to avoid storage I/O errors.
>
> **Recommended Fix:** If errors persist, delete the template and endpoint entirely from the Runpod console and re-run `configure` to force a clean slate.

A CLI tool to run Qwen-Image-Layered on Runpod GPU instances for image layer decomposition.

## What is Qwen-Image-Layered?

Qwen-Image-Layered is a state-of-the-art image decomposition model that takes images and breaks them down into multiple independent RGBA layers with transparency. Each layer can be manipulated independently, enabling powerful non-destructive editing workflows.

### Key Capabilities

- **Variable Layer Decomposition**: Generate 3, 4, or 8 layers from any image
- **Recursive Decomposition**: Further decompose any individual layer infinitely
- **Independent Layer Editing**: Each layer can be:
  - Recolored
  - Repositioned
  - Resized
  - Deleted without affecting other layers
- **High-Fidelity Separation**: Maintains visual quality through intelligent layer separation

### Use Cases

- Automated image editing and composition
- Design tool integration (PowerPoint, graphics software)
- Content creation and manipulation
- Non-destructive image processing
- Layer-based creative workflows

### Model Architecture

- **Base**: Qwen-Image foundation model
- **Vision Component**: Qwen2.5-VL (7B parameters)
- **Framework**: Hugging Face Diffusers (diffusion-based architecture)
- **License**: Apache 2.0 (free for commercial use)

---

## Installation

### Option 1: Install as a uv Tool (Recommended)

Install directly using uv:

```bash
uv tool install qwen-image-layered
```

Or install from source:

```bash
git clone https://github.com/tejas-kale/experiments.git
cd experiments/experiments/ai_model_exploration/qwen_image_layered
uv tool install .
```

### Option 2: Install in a Virtual Environment

```bash
# Clone the repository
git clone https://github.com/tejas-kale/experiments.git
cd experiments/experiments/ai_model_exploration/qwen_image_layered

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On macOS/Linux

# Install the package
uv pip install -e .
```

---

## Quick Start

### 1. Configure Runpod (One-Time Setup)

Set your Runpod API key and run the configure command:

```bash
export RUNPOD_API_KEY=your_api_key_here
qwen-image-layered configure
```

This will:
- Create a Runpod template with the Qwen-Image-Layered handler
- Deploy a serverless endpoint (RTX 3090 by default)
- Save configuration to `~/.qwen-image-layered/config.json`

**Get your API key**: [Runpod Console → Settings](https://www.runpod.io/console/user/settings)

### 2. Generate Layers

```bash
qwen-image-layered generate image.jpg
```

That's it! The layers will be saved to `./qwen_output/` by default.

---

## Usage

### Configure Command

```bash
# Basic configuration (uses RTX 3090)
qwen-image-layered configure

# Use a different GPU
qwen-image-layered configure --gpu-type "NVIDIA RTX 4090"

# Specify custom Docker image
qwen-image-layered configure --docker-image custom/image:tag
```

**Options**:
- `--api-key`: Runpod API key (or set `RUNPOD_API_KEY` env var)
- `--docker-image`: Base Docker image (default: `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04`)
- `--gpu-type`: GPU type (default: `NVIDIA RTX 3090`)

### Generate Command

```bash
# Basic usage
qwen-image-layered generate image.jpg

# Customize parameters
qwen-image-layered generate image.jpg \
  --layers 8 \
  --resolution 1024 \
  --steps 50 \
  --cfg-scale 4.0 \
  --output-dir ./my_output
```

**Options**:
- `--layers`, `-l`: Number of layers (3, 4, or 8) - default: 4
- `--resolution`, `-r`: Output resolution (640 or 1024) - default: 640
- `--steps`, `-s`: Inference steps - default: 50
- `--cfg-scale`, `-c`: CFG scale - default: 4.0
- `--output-dir`, `-o`: Output directory - default: `./qwen_output`

### Info Command

View your current configuration:

```bash
qwen-image-layered info
```

---

## Requirements

### Local Machine
- Python 3.11+
- macOS (developed and tested)
- Runpod account with API key
- ~$9 in Runpod credits (estimates below)

### Runpod Instance
- **GPU**: RTX 3090 (24GB VRAM) - **Recommended**
  - Cost: ~$0.24/hour
  - With $9: ~37 hours of usage
- **Alternative GPUs**:
  - RTX 4090 (24GB): ~$0.44/hour
  - RTX A5000 (24GB): ~$0.34/hour
- **VRAM Requirements**:
  - bfloat16 (full precision): 24-40GB
  - fp8mixed (quantized): 12-16GB

---

## How It Works

### Architecture

```
┌─────────────────┐
│  Local Machine  │
│   (CLI Client)  │
└────────┬────────┘
         │ 1. Upload image (base64)
         │    + parameters
         ▼
┌─────────────────┐
│  Runpod Cloud   │
│   (GPU Server)  │
│                 │
│  ┌───────────┐  │
│  │  Handler  │  │ 2. Decode image
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │ 3. Load model
│  │  Qwen-IL  │  │    (cached after first run)
│  │   Model   │  │
│  └─────┬─────┘  │
│        │        │ 4. Generate layers
│        ▼        │
│  ┌───────────┐  │
│  │  Layers   │  │ 5. Encode to base64
│  │  (RGBA)   │  │
│  └─────┬─────┘  │
└────────┼────────┘
         │ 6. Download layers
         ▼
┌─────────────────┐
│  Local Machine  │
│  (Save PNGs)    │
└─────────────────┘
```

### Workflow

1. **Configuration**: CLI creates Runpod template and endpoint via GraphQL API
2. **Initialization**: Endpoint loads Qwen-Image-Layered model (~2-3 minutes first time)
3. **Image Upload**: Input image is base64-encoded and sent via HTTPS
4. **Inference**: Model generates specified number of layers (~2-3 minutes)
5. **Download**: Layers are base64-encoded, sent back, and saved as PNG files

### Cost Estimation

- **Endpoint initialization**: 2-3 minutes
- **Inference (640px, 50 steps, 4 layers)**: 2-3 minutes
- **Total per image**: ~5-6 minutes
- **Cost per image (RTX 3090 @ $0.24/hr)**: ~$0.02-0.024
- **Images with $9 budget**: ~375-450 images

---

## Test Cases

### Test Case 1: Portrait Photo Layer Separation

**Objective**: Decompose a portrait photo into background, subject, and detail layers.

```bash
qwen-image-layered generate portrait.jpg \
  --layers 4 \
  --resolution 640 \
  --output-dir ./test_portrait
```

**Expected Output**:
- `layer_00.png`: Background layer
- `layer_01.png`: Main subject (person)
- `layer_02.png`: Hair/detail elements
- `layer_03.png`: Foreground elements

**What to Try**:
1. Replace background (`layer_00.png`) with a different image
2. Adjust subject color/position independently
3. Delete foreground elements

### Test Case 2: Product Photography

**Objective**: Separate product from background for e-commerce.

```bash
qwen-image-layered generate product.jpg \
  --layers 3 \
  --resolution 1024 \
  --steps 50 \
  --output-dir ./test_product
```

**Expected Output**:
- `layer_00.png`: Background
- `layer_01.png`: Main product
- `layer_02.png`: Shadows/reflections

### Test Case 3: Complex Scene Decomposition

**Objective**: Decompose a multi-element scene into maximum layers.

```bash
qwen-image-layered generate complex_scene.jpg \
  --layers 8 \
  --resolution 640 \
  --steps 50 \
  --output-dir ./test_complex
```

**Expected Output**: 8 separate RGBA layers with different scene elements

---

## Troubleshooting

### Issue: "Not configured yet"

**Solution**: Run the configure command first:
```bash
export RUNPOD_API_KEY=your_key
qwen-image-layered configure
```

### Issue: Configuration fails

**Solution**:
1. Verify API key is correct
2. Check Runpod account has sufficient credits
3. Try different GPU type: `--gpu-type "NVIDIA RTX A5000"`

### Issue: First generation is slow

**Solution**: This is normal! The first request takes 5-10 minutes to download the model (~10GB). Subsequent requests are much faster (~2-3 minutes).

### Issue: Job failed during inference

**Solution**:
1. Check input image is valid (JPEG/PNG)
2. Try smaller resolution: `--resolution 640`
3. Reduce number of layers: `--layers 3`
4. Check Runpod logs in the [Runpod Console](https://www.runpod.io/console/serverless)

### Issue: Out of memory error

**Solution**:
1. Reconfigure with RTX 4090: `qwen-image-layered configure --gpu-type "NVIDIA RTX 4090"`
2. Reduce resolution to 640
3. Model defaults to bfloat16 (requires 24GB VRAM)

---

## Project Structure

```
qwen_image_layered/
├── src/qwen_image_layered/
│   ├── __init__.py         # Package initialization
│   ├── cli.py              # CLI commands
│   ├── config.py           # Configuration management
│   ├── client.py           # Runpod client
│   └── runpod_manager.py   # Runpod API integration
├── runpod_deployments/
│   └── qwen_image_layered/
│       ├── handler.py      # Serverless handler
│       ├── Dockerfile      # Container config
│       └── requirements.txt
├── pyproject.toml          # Package configuration
└── README.md               # This file
```

---

## Advanced Configuration

### Using Different GPU Types

```bash
# Budget option
qwen-image-layered configure --gpu-type "NVIDIA RTX 3090"

# Performance option
qwen-image-layered configure --gpu-type "NVIDIA RTX 4090"

# Balanced option
qwen-image-layered configure --gpu-type "NVIDIA RTX A5000"
```

### Environment Variables

You can override configuration file settings using environment variables:

- `RUNPOD_API_KEY`: Runpod API key
- `RUNPOD_ENDPOINT_ID`: Endpoint ID (overrides configured endpoint)
- `RUNPOD_TEMPLATE_ID`: Template ID (overrides configured template)
- `RUNPOD_GPU_TYPE`: GPU type (overrides configured GPU)

---

## References

- [Qwen-Image-Layered on Hugging Face](https://huggingface.co/Qwen/Qwen-Image-Layered)
- [GitHub Repository](https://github.com/QwenLM/Qwen-Image-Layered)
- [Research Paper (arXiv)](https://arxiv.org/abs/2512.15603)
- [Runpod Documentation](https://docs.runpod.io/)
- [Runpod Serverless Guide](https://docs.runpod.io/serverless/overview)

---

## License

This project wraps the Qwen-Image-Layered model (Apache 2.0 license) for Runpod deployment.
