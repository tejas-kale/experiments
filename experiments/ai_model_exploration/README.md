# AI Model Exploration

Experiments with cutting-edge AI models deployed on Runpod GPU instances.

## Overview

This directory contains two complete experimentation setups for state-of-the-art AI models:

1. **Qwen-Image-Layered**: Image layer decomposition for non-destructive editing
2. **Chatterbox TTS**: Text-to-speech with emotion control and multilingual support

Both projects include:
- Full CLI interfaces for local control
- Runpod integration for GPU-accelerated inference
- Secure data transfer with encryption
- Automatic instance management
- Comprehensive documentation and test cases
- **NEW**: Automated setup CLI for templates and endpoints

---

## Quick Start

### **Option 1: Automated Setup (Recommended)**

Use the setup CLI to create templates and endpoints automatically:

```bash
cd experiments/ai_model_exploration

# Install dependencies
source ../../.venv/bin/activate
uv pip install click rich requests python-dotenv

# Set up Chatterbox TTS
python setup_cli.py setup-chatterbox

# Or set up Qwen-Image-Layered
python setup_cli.py setup-qwen
```

The setup CLI will:
1. Create Runpod template via API
2. Create serverless endpoint with auto-scaling
3. Save credentials to `.env` file
4. Show you the test command

### **Option 2: Manual Setup**

Follow the detailed SETUP.md guides:
- [Chatterbox TTS Setup](chatterbox_tts/SETUP.md)
- [Qwen-Image-Layered Setup](qwen_image_layered/SETUP.md)

---

## Projects

### 1. Qwen-Image-Layered (`qwen_image_layered/`)

**What it does**: Decomposes images into multiple RGBA layers for independent editing.

**Key Features**:
- Generate 3, 4, or 8 layers from any image
- Each layer is independently editable (move, resize, recolor, delete)
- Recursive decomposition support
- High-fidelity separation

**GPU Requirements**: RTX 3090 (24GB) @ ~$0.24/hour

**Cost with $9 budget**: ~375-450 images

**Quick Test**:
```bash
cd qwen_image_layered
python cli.py generate your_image.jpg --layers 4
```

[→ Full Documentation](qwen_image_layered/README.md)

---

### 2. Chatterbox TTS (`chatterbox_tts/`)

**What it does**: Synthesizes natural speech from text with emotion control.

**Key Features**:
- Emotion exaggeration control (0.25× to 2.0×)
- 23 language support
- Voice cloning capability
- Audio watermarking
- High-quality synthesis

**GPU Requirements**: RTX 3060 Ti (8GB) @ ~$0.14/hour

**Cost with $9 budget**: ~900-1,285 speech clips

**Quick Test**:
```bash
cd chatterbox_tts
python cli.py speak "Hello! This is a test." --exaggeration 1.5
```

[→ Full Documentation](chatterbox_tts/README.md)

---

## Setup CLI Commands

### Create Templates and Endpoints

```bash
# Chatterbox TTS
python setup_cli.py setup-chatterbox

# Qwen-Image-Layered
python setup_cli.py setup-qwen
```

### List Existing Resources

```bash
# List all templates
python setup_cli.py list-templates

# List all endpoints
python setup_cli.py list-endpoints
```

---

## Cost Breakdown

### Qwen-Image-Layered

| GPU | VRAM | Cost/Hour | Images/$9 | Best For |
|-----|------|-----------|-----------|----------|
| RTX 3090 | 24GB | $0.24 | ~375 | Budget (recommended) |
| RTX A5000 | 24GB | $0.34 | ~265 | Balanced |
| RTX 4090 | 24GB | $0.44 | ~205 | Performance |

**Recommended**: RTX 3090 for best cost/performance

### Chatterbox TTS

| GPU | VRAM | Cost/Hour | Clips/$9 | Best For |
|-----|------|-----------|----------|----------|
| RTX 3060 Ti | 8GB | $0.14 | ~1,285 | Budget (recommended) |
| RTX 3060 | 12GB | $0.18 | ~1,000 | Extra headroom |
| RTX 4060 | 8GB | $0.16 | ~1,125 | Performance |

**Recommended**: RTX 3060 Ti for best cost/performance

---

## Architecture

Both projects follow a REST API client-server architecture:

```
┌──────────────────────────────────────────┐
│           Local Machine (CLI)            │
│  • Submit jobs to endpoint               │
│  • Poll for results                      │
│  • Download and save outputs             │
└──────────────┬───────────────────────────┘
               │
               │ HTTPS REST API
               │ POST /run (submit job)
               │ GET /status/{job_id}
               │
┌──────────────▼───────────────────────────┐
│         Runpod GPU Instance              │
│  • Auto-scales from 0 workers            │
│  • Loads model (cached)                  │
│  • Runs inference                        │
│  • Returns results                       │
└──────────────────────────────────────────┘
```

**Security**:
- All data transfer over HTTPS
- Base64 encoding for images/audio
- API key authentication (Bearer token)
- Auto-scaling endpoints (no lingering costs)

---

## Sample Test Cases

### Qwen-Image-Layered

1. **Portrait Background Removal**: Separate subject from background in photos
2. **Product Photography**: Isolate products for e-commerce
3. **Complex Scene Editing**: Decompose multi-element scenes into 8 layers

[→ See full test cases](qwen_image_layered/README.md#test-cases)

### Chatterbox TTS

1. **Emotional Audiobook Narration**: Generate expressive story narration
2. **Multilingual Announcements**: Create consistent messages in 3+ languages
3. **Voice Assistant Responses**: Different tones (helpful, apologetic, enthusiastic)

[→ See full test cases](chatterbox_tts/README.md#test-cases)

---

## Project Structure

```
ai_model_exploration/
├── README.md                    # This file
├── API_VALIDATION.md            # Implementation validation against API docs
├── setup_cli.py                 # Automated template/endpoint creation
├── qwen_image_layered/
│   ├── cli.py                   # CLI client (REST API)
│   ├── runpod_handler.py        # Runpod inference handler
│   ├── requirements.txt         # Dependencies
│   ├── .env.example            # Environment template
│   ├── .gitignore              # Git ignore rules
│   ├── SETUP.md                # Manual setup guide
│   └── README.md               # Full documentation
└── chatterbox_tts/
    ├── cli.py                   # CLI client (REST API)
    ├── runpod_handler.py        # Runpod inference handler
    ├── requirements.txt         # Dependencies
    ├── .env.example            # Environment template
    ├── .gitignore              # Git ignore rules
    ├── SETUP.md                # Manual setup guide
    └── README.md               # Full documentation
```

---

## API Implementation

All implementations validated against official Runpod API documentation.

**REST API Endpoints Used**:
- `POST /v2/{endpoint_id}/run` - Submit async job
- `GET /v2/{endpoint_id}/status/{job_id}` - Check status

**GraphQL API** (setup CLI only):
- `mutation SaveTemplate` - Create templates
- `mutation SaveEndpoint` - Create endpoints
- `query myself` - List resources

See [API_VALIDATION.md](API_VALIDATION.md) for detailed validation.

---

## Tips for Maximizing Your $9 Budget

1. **Use automated setup**: Faster and less error-prone
2. **Auto-scaling endpoints**: No charges when idle (5-second timeout)
3. **Start with Chatterbox**: It's cheaper and faster for testing
4. **Use recommended GPUs**: Best cost/performance ratios
5. **Monitor spending**: Check Runpod console regularly
6. **Test locally first**: Validate inputs before using GPU time

---

## Troubleshooting

### Setup CLI Issues

**GraphQL errors**: Ensure your API key has correct permissions

**Template creation fails**: Check Docker image name and start command

**Endpoint creation fails**: Verify template ID exists

### CLI Issues

**"Endpoint not ready"**: Wait 2-3 minutes after creation

**First run slow**: Model downloads take 3-10 minutes (one-time)

**Job failed**: Check Runpod endpoint logs in console

### Project-Specific

See individual READMEs for detailed troubleshooting:
- [Qwen Troubleshooting](qwen_image_layered/README.md#troubleshooting)
- [Chatterbox Troubleshooting](chatterbox_tts/README.md#troubleshooting)

---

## Next Steps

1. **Automated setup** (recommended):
   ```bash
   python setup_cli.py setup-chatterbox
   ```

2. **Or manual setup** following SETUP.md guides

3. **Run test cases** to validate setup

4. **Experiment** with your own use cases!

---

## References

### Qwen-Image-Layered
- [Hugging Face Model](https://huggingface.co/Qwen/Qwen-Image-Layered)
- [GitHub Repository](https://github.com/QwenLM/Qwen-Image-Layered)
- [Research Paper](https://arxiv.org/abs/2512.15603)

### Chatterbox TTS
- [GitHub Repository](https://github.com/resemble-ai/chatterbox)
- [Resemble AI Official](https://www.resemble.ai/chatterbox/)
- [Hugging Face Model](https://huggingface.co/ResembleAI/chatterbox)

### Runpod
- [Runpod API Documentation](https://docs.runpod.io/api-reference/overview)
- [Serverless Guide](https://docs.runpod.io/serverless/endpoints/get-started)
- [Pricing Calculator](https://www.runpod.io/pricing)

---

## License

- **Qwen-Image-Layered**: Apache 2.0
- **Chatterbox TTS**: MIT License
- **This Implementation**: Follows global CLAUDE.md guidelines
