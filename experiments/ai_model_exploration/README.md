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
- Automatic instance management (create, use, delete)
- Comprehensive documentation and test cases

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

**Quick Start**:
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

**Quick Start**:
```bash
cd chatterbox_tts
python cli.py speak "Hello! This is a test." --exaggeration 1.5
```

[→ Full Documentation](chatterbox_tts/README.md)

---

## Setup Guide

### Prerequisites

1. **Runpod Account**: Sign up at [runpod.io](https://www.runpod.io)
2. **API Key**: Get from [Runpod Console](https://www.runpod.io/console/user/settings)
3. **Credits**: Add at least $9 to your account
4. **Python 3.11+**: Required for local CLI

### Quick Setup (Both Projects)

```bash
# Navigate to repository root
cd experiments/

# Activate virtual environment
source .venv/bin/activate

# Setup Qwen-Image-Layered
cd ai_model_exploration/qwen_image_layered
uv pip install -r requirements.txt
cp .env.example .env
# Edit .env and add RUNPOD_API_KEY

# Setup Chatterbox TTS
cd ../chatterbox_tts
uv pip install -r requirements.txt
cp .env.example .env
# Edit .env and add RUNPOD_API_KEY
```

### One-Time Runpod Template Setup

Both projects require custom Runpod templates. Follow the setup instructions in each project's README:
- [Qwen Template Setup](qwen_image_layered/README.md#5-setup-runpod-template-one-time-setup)
- [Chatterbox Template Setup](chatterbox_tts/README.md#5-setup-runpod-template-one-time-setup)

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

Both projects follow the same client-server architecture:

```
┌──────────────────────────────────────────┐
│           Local Machine (CLI)            │
│  • Send requests (image/text)            │
│  • Manage Runpod instances               │
│  • Download results                       │
└──────────────┬───────────────────────────┘
               │
               │ HTTPS + Encryption
               │
┌──────────────▼───────────────────────────┐
│         Runpod GPU Instance              │
│  • Load model (cached)                   │
│  • Run inference                          │
│  • Return results                         │
└──────────────────────────────────────────┘
```

**Security**:
- All data transfer over HTTPS
- Base64 encoding for images/audio
- API key authentication
- Automatic instance cleanup

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
├── qwen_image_layered/
│   ├── cli.py                   # CLI client
│   ├── runpod_handler.py        # Runpod inference handler
│   ├── requirements.txt         # Dependencies
│   ├── .env.example            # Environment template
│   ├── .gitignore              # Git ignore rules
│   └── README.md               # Full documentation
└── chatterbox_tts/
    ├── cli.py                   # CLI client
    ├── runpod_handler.py        # Runpod inference handler
    ├── requirements.txt         # Dependencies
    ├── .env.example            # Environment template
    ├── .gitignore              # Git ignore rules
    └── README.md               # Full documentation
```

---

## Tips for Maximizing Your $9 Budget

1. **Delete endpoints immediately**: Both CLIs auto-delete, but double-check in Runpod console
2. **Batch your work**: Process multiple images/texts in one session
3. **Start with Chatterbox**: It's cheaper and faster for testing the setup
4. **Use recommended GPUs**: They offer the best cost/performance
5. **Monitor spending**: Check Runpod console regularly
6. **Test locally first**: Ensure inputs are valid before using GPU time

---

## Troubleshooting

### Both Projects

- **API Key Issues**: Ensure `.env` file has correct `RUNPOD_API_KEY`
- **Template Not Found**: Complete one-time template setup in Runpod console
- **No Credits**: Add funds to Runpod account
- **Endpoint Timeout**: First run takes 3-5 minutes to download models

### Project-Specific

See individual READMEs for detailed troubleshooting:
- [Qwen Troubleshooting](qwen_image_layered/README.md#troubleshooting)
- [Chatterbox Troubleshooting](chatterbox_tts/README.md#troubleshooting)

---

## Next Steps

1. **Complete setup** for both projects (install deps, configure API keys)
2. **Create Runpod templates** (one-time, ~10 minutes each)
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
- [Runpod Documentation](https://docs.runpod.io/)
- [Serverless Guide](https://docs.runpod.io/serverless/overview)
- [Pricing Calculator](https://www.runpod.io/pricing)

---

## License

- **Qwen-Image-Layered**: Apache 2.0
- **Chatterbox TTS**: MIT License
- **This Implementation**: Follows global CLAUDE.md guidelines
