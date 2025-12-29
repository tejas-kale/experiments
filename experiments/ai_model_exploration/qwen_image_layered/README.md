# Qwen-Image-Layered on Runpod

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

## Requirements

### Local Machine (CLI)
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

## Installation & Setup

### 1. Clone and Navigate

```bash
cd experiments/ai_model_exploration/qwen_image_layered
```

### 2. Create Virtual Environment

```bash
# From repository root
source .venv/bin/activate

# Or create new environment
uv venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
uv pip install -r requirements.txt
```

### 4. Configure Runpod API Key

1. Get your API key from [Runpod Console](https://www.runpod.io/console/user/settings)
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your API key:
   ```
   RUNPOD_API_KEY=your_actual_api_key_here
   ```

### 5. Setup Runpod Template (One-Time Setup)

You need to create a custom Runpod template with the handler script:

1. Go to [Runpod Templates](https://www.runpod.io/console/serverless/user/templates)
2. Click "New Template"
3. Configure:
   - **Template Name**: `runpod-qwen-image-layered`
   - **Container Image**: `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04`
   - **Container Disk**: 20 GB
   - **Start Command**:
     ```bash
     pip install git+https://github.com/huggingface/diffusers transformers>=4.51.3 torch torchvision runpod && python runpod_handler.py
     ```
   - **Environment Variables**:
     - `MODEL_NAME`: `Qwen/Qwen-Image-Layered`
4. Upload `runpod_handler.py` to the template
5. Save template

---

## Usage

### Basic Command

```bash
python cli.py generate <image_path>
```

### Full Options

```bash
python cli.py generate <image_path> \
  --layers 4 \
  --resolution 640 \
  --steps 50 \
  --cfg-scale 4.0 \
  --output-dir ./my_output \
  --gpu "NVIDIA RTX 3090"
```

### Options Explained

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--layers` | `-l` | `4` | Number of layers (3, 4, or 8) |
| `--resolution` | `-r` | `640` | Output resolution (640 or 1024px) |
| `--steps` | `-s` | `50` | Inference steps (more = better quality, slower) |
| `--cfg-scale` | `-c` | `4.0` | Classifier-free guidance scale |
| `--output-dir` | `-o` | `./qwen_output` | Output directory for layers |
| `--gpu` | | `NVIDIA RTX 3090` | GPU type to use |

---

## Test Cases

### Test Case 1: Portrait Photo Layer Separation

**Objective**: Decompose a portrait photo into background, subject, and detail layers for easy background replacement.

**Input Image**: Portrait photo with clear subject-background separation (e.g., person against a landscape)

**Command**:
```bash
python cli.py generate portrait.jpg \
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
1. Open layers in an image editor (Photoshop, GIMP, Pixelmator)
2. Replace `layer_00.png` (background) with a different background
3. Adjust `layer_01.png` (subject) color/position independently
4. Delete `layer_03.png` to remove foreground elements

**Validation**:
- Each layer should have transparent regions (RGBA)
- Stacking all layers should reconstruct the original image
- Individual layers should be independently editable

---

### Test Case 2: Product Photography for E-commerce

**Objective**: Separate product from background for catalog use with different backgrounds.

**Input Image**: Product photo (e.g., shoe, gadget, furniture) with complex background

**Command**:
```bash
python cli.py generate product.jpg \
  --layers 3 \
  --resolution 1024 \
  --steps 50 \
  --output-dir ./test_product
```

**Expected Output**:
- `layer_00.png`: Background
- `layer_01.png`: Main product
- `layer_02.png`: Product shadows/reflections

**What to Try**:
1. Export `layer_01.png` (product) for use in e-commerce catalog
2. Create multiple variations by changing `layer_00.png` background
3. Adjust `layer_02.png` shadow opacity for different lighting effects
4. Batch process multiple products for consistent catalog images

**Validation**:
- Product edges should be clean and artifact-free
- Shadows/reflections should be separated from main product
- Product layer should work on white, colored, or gradient backgrounds

---

### Test Case 3: Complex Scene Decomposition

**Objective**: Decompose a multi-element scene (e.g., still life, street scene) into maximum layers for detailed editing.

**Input Image**: Complex scene with multiple objects at different depths (e.g., desk with laptop, coffee, plants)

**Command**:
```bash
python cli.py generate complex_scene.jpg \
  --layers 8 \
  --resolution 640 \
  --steps 50 \
  --cfg-scale 4.0 \
  --output-dir ./test_complex
```

**Expected Output**:
- 8 separate RGBA layers, each containing different scene elements
- Approximate layer separation by depth and object boundaries

**What to Try**:
1. Reorder layers to change depth perception
2. Selectively hide/show layers to remove objects
3. Apply different color grading to foreground vs background layers
4. Create a "focus stack" effect by blurring distant layers
5. Export individual objects by isolating specific layers

**Validation**:
- All 8 layers should have meaningful content
- Objects at different depths should be on different layers
- Stacking all layers should closely match original
- Individual layers should allow for creative recombination

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

1. **Endpoint Creation**: CLI creates a Runpod serverless endpoint with specified GPU
2. **Initialization**: Endpoint loads Qwen-Image-Layered model (~2-3 minutes first time)
3. **Image Upload**: Input image is base64-encoded and sent via HTTPS
4. **Inference**: Model generates specified number of layers (~1-3 minutes depending on resolution/steps)
5. **Download**: Layers are base64-encoded, sent back, and saved as PNG files
6. **Cleanup**: Endpoint is automatically deleted to stop billing

### Cost Estimation

- **Endpoint initialization**: 2-3 minutes
- **Inference (640px, 50 steps, 4 layers)**: 2-3 minutes
- **Total per image**: ~5-6 minutes
- **Cost per image (RTX 3090 @ $0.24/hr)**: ~$0.02-0.024
- **Images with $9 budget**: ~375-450 images

---

## Troubleshooting

### Issue: `RUNPOD_API_KEY not found`

**Solution**: Ensure `.env` file exists with your API key:
```bash
cp .env.example .env
# Edit .env and add your key
```

### Issue: `Failed to create endpoint`

**Solution**:
1. Verify API key is correct
2. Check Runpod account has sufficient credits
3. Ensure template `runpod-qwen-image-layered` exists
4. Try different GPU type with `--gpu` option

### Issue: `Timeout waiting for endpoint`

**Solution**:
1. First run takes longer (~5 minutes) to download model weights
2. Check Runpod console for endpoint status
3. Increase timeout in code if necessary
4. Try a less busy GPU type

### Issue: `Job failed during inference`

**Solution**:
1. Check input image is valid (JPEG/PNG)
2. Try smaller resolution (640 instead of 1024)
3. Reduce number of layers
4. Check Runpod endpoint logs in console

### Issue: `Out of memory error`

**Solution**:
1. Use RTX 4090 or A5000 instead of RTX 3090
2. Reduce resolution to 640
3. Model defaults to bfloat16; consider fp8 quantization for lower VRAM

---

## Advanced Configuration

### Using Different GPU Types

```bash
# Budget option
python cli.py generate image.jpg --gpu "NVIDIA RTX 3090"

# Performance option
python cli.py generate image.jpg --gpu "NVIDIA RTX 4090"

# Balanced option
python cli.py generate image.jpg --gpu "NVIDIA RTX A5000"
```

### High-Resolution Processing

```bash
# 1024px output (slower, better quality)
python cli.py generate image.jpg --resolution 1024 --steps 50
```

### Quick Preview Mode

```bash
# Faster inference (lower quality)
python cli.py generate image.jpg --steps 25 --layers 3
```

---

## Project Structure

```
qwen_image_layered/
├── cli.py                  # Local CLI client
├── runpod_handler.py       # Runpod serverless handler
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── .env                   # Your API key (gitignored)
└── README.md              # This file
```

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
