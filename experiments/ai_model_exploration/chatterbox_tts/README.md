# Chatterbox Turbo TTS on Runpod

A CLI tool to run Chatterbox Turbo TTS on Runpod GPU instances for high-quality text-to-speech synthesis with emotion control and low latency.

## What is Chatterbox Turbo TTS?

Chatterbox Turbo is a state-of-the-art, optimized text-to-speech (TTS) model from Resemble AI. It's a distilled version of the original Chatterbox model, achieving 10x faster inference with the same high-quality output. The Turbo model supports emotion exaggeration control and native paralinguistic tags for realistic speech.

### Key Capabilities

- **Emotion Control**: Adjust emotion intensity from 0.25× (subdued) to 2.0× (exaggerated)
- **Voice Cloning**: Clone any voice with just a few seconds of reference audio (no training needed)
- **Multilingual Support**: 23 languages including:
  - European: English, Spanish, French, German, Italian, Portuguese, Dutch, Swedish, Norwegian, Danish, Finnish, Polish, Russian, Greek
  - Asian: Japanese, Korean, Chinese, Hindi, Malay
  - Middle Eastern: Arabic, Hebrew, Turkish
  - African: Swahili
- **Audio Watermarking**: Every generated file includes imperceptible neural watermarks that survive MP3 compression
- **High Quality**: Benchmarked favorably against closed-source systems like ElevenLabs

### Use Cases

- Audiobook production with emotional narration
- Voice cloning and voice conversion
- Multilingual content generation
- Podcast and media production
- Accessible content creation
- Interactive voice applications
- Character voices for games and storytelling

### Model Architecture

- **Model**: Chatterbox Turbo TTS (350M parameters, distilled)
- **Mel Decoder**: 1-step (vs 10-step in original) for 10x faster inference
- **Latency**: Sub-200ms for real-time applications
- **Framework**: PyTorch with custom architecture
- **License**: MIT License (fully open source)
- **Provider**: Resemble AI
- **Model ID**: `ResembleAI/chatterbox-turbo`

---

## Requirements

### Local Machine (CLI)
- Python 3.11+
- macOS (developed and tested)
- Runpod account with API key
- Hugging Face account with access token (for model download)
- ~$9 in Runpod credits (estimates below)
- Audio player (`afplay` on macOS, included by default)

### Runpod Instance
- **GPU**: RTX 3060 Ti (8GB VRAM) - **Recommended**
  - Cost: ~$0.14/hour
  - With $9: ~64 hours of usage
- **Alternative GPUs**:
  - RTX 4060 (8GB): ~$0.16/hour
  - RTX 3060 (12GB): ~$0.18/hour
- **VRAM Requirements**:
  - Minimum: 6-7GB
  - Recommended: 8GB+
  - Optimal: 16GB for higher concurrency

---

## Installation & Setup

### 1. Clone and Navigate

```bash
cd experiments/ai_model_exploration/chatterbox_tts
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

### 5. Get Hugging Face Token

**IMPORTANT**: Chatterbox Turbo requires authentication to download the model.

1. Go to [Hugging Face Settings - Tokens](https://huggingface.co/settings/tokens)
2. Create a new token (read access is sufficient)
3. Copy the token - you'll need it when setting up the Runpod endpoint

### 6. Setup Runpod Template (One-Time Setup)

You need to create a custom Runpod template with the handler script:

1. Go to [Runpod Templates](https://www.runpod.io/console/serverless/user/templates)
2. Click "New Template"
3. Configure:
   - **Template Name**: `runpod-chatterbox-tts`
   - **Container Image**: `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04`
   - **Container Disk**: 15 GB
   - **Start Command**:
     ```bash
     pip install chatterbox-tts runpod huggingface-hub && python runpod_handler.py
     ```
   - **Environment Variables**:
     - **Name**: `HF_TOKEN`
     - **Value**: Your Hugging Face token from step 5
4. Upload `runpod_handler.py` to the template
5. Save template

---

## Usage

### Basic Command

```bash
python cli.py speak "Hello! This is a test of the Chatterbox TTS system."
```

### Full Options

```bash
python cli.py speak "Your text here" \
  --exaggeration 1.5 \
  --cfg-weight 0.7 \
  --temperature 1.0 \
  --voice default \
  --output ./my_audio.wav \
  --play \
  --gpu "NVIDIA RTX 3060 Ti"
```

### Options Explained

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--exaggeration` | `-e` | `1.0` | Emotion intensity (0.25-2.0) |
| `--cfg-weight` | `-c` | `0.7` | Guidance weight (0.0-1.0) |
| `--temperature` | `-t` | `1.0` | Sampling randomness (0.05-5.0) |
| `--speed` | `-s` | `0.85` | Playback speed (0.5-2.0, slower for better comprehension) |
| `--voice` | `-v` | `default` | Voice name |
| `--output` | `-o` | `./chatterbox_output/speech_<timestamp>.wav` | Output file |
| `--format` | `-f` | `wav` | Output format (wav or mp3) |
| `--bitrate` | `-b` | `192k` | MP3 bitrate (e.g., 128k, 192k, 320k) |
| `--file` | `-F` | None | Read text from file instead of argument |
| `--save-preprocessed` | | None | Save preprocessed text to file for review |
| `--play/--no-play` | | `True` | Auto-play after generation |
| `--gpu` | | `NVIDIA RTX 3060 Ti` | GPU type to use |

### Parameter Guide

**Exaggeration** (0.25 - 2.0):
- `0.25`: Very subdued, minimal emotion
- `0.5`: Reduced emotion
- `1.0`: Natural emotion (default)
- `1.5`: Enhanced emotion
- `2.0`: Maximum emotion intensity

**CFG Weight** (0.0 - 1.0):
- `0.0`: No guidance (random)
- `0.5`: Balanced
- `0.7`: Recommended default
- `1.0`: Maximum guidance (most controlled)

**Temperature** (0.05 - 5.0):
- `0.05-0.5`: Very consistent, less varied
- `1.0`: Balanced (default)
- `1.5-3.0`: More varied, creative
- `3.0-5.0`: Very diverse, less predictable

---

## Test Cases

### Test Case 1: Emotional Narration for Audiobook

**Objective**: Generate expressive narration for a dramatic story passage with varying emotion levels.

**Text**:
```
"The ancient door creaked open, revealing a chamber bathed in golden light.
Sarah gasped. After years of searching, she had finally found it—the Lost Library of Alexandria."
```

**Commands**:

1. **Neutral narration** (baseline):
```bash
python cli.py speak "The ancient door creaked open, revealing a chamber bathed in golden light. Sarah gasped. After years of searching, she had finally found it—the Lost Library of Alexandria." \
  --exaggeration 1.0 \
  --output ./test1_neutral.wav
```

2. **Subdued, mysterious tone**:
```bash
python cli.py speak "The ancient door creaked open, revealing a chamber bathed in golden light. Sarah gasped. After years of searching, she had finally found it—the Lost Library of Alexandria." \
  --exaggeration 0.5 \
  --temperature 0.8 \
  --output ./test1_subdued.wav
```

3. **Highly dramatic, excited tone**:
```bash
python cli.py speak "The ancient door creaked open, revealing a chamber bathed in golden light. Sarah gasped. After years of searching, she had finally found it—the Lost Library of Alexandria." \
  --exaggeration 2.0 \
  --temperature 1.2 \
  --output ./test1_dramatic.wav
```

**What to Try**:
1. Listen to all three versions back-to-back
2. Notice how exaggeration affects emotional delivery
3. Compare pacing and emphasis differences
4. Use for audiobook chapter narration

**Validation**:
- `test1_neutral.wav`: Clear, balanced narration
- `test1_subdued.wav`: Quieter, more mysterious tone
- `test1_dramatic.wav`: Emphasized gasps, excitement, wonder

**Expected Differences**:
- Prosody (rhythm and intonation) should vary significantly
- Dramatic version should have more pronounced pauses
- Subdued version should be more monotone

---

### Test Case 2: Multilingual Product Announcement

**Objective**: Generate consistent product announcement in multiple languages for international marketing.

**Text** (same message in 3 languages):
- English: "Introducing the all-new SmartWatch Pro. Your health, fitness, and connectivity—all on your wrist."
- Spanish: "Presentamos el nuevo SmartWatch Pro. Tu salud, fitness y conectividad—todo en tu muñeca."
- Japanese: "全く新しいSmartWatch Proをご紹介します。健康、フィットネス、接続性、すべてあなたの手首に。"

**Commands**:

1. **English version**:
```bash
python cli.py speak "Introducing the all-new SmartWatch Pro. Your health, fitness, and connectivity—all on your wrist." \
  --exaggeration 1.3 \
  --cfg-weight 0.8 \
  --output ./test2_english.wav
```

2. **Spanish version**:
```bash
python cli.py speak "Presentamos el nuevo SmartWatch Pro. Tu salud, fitness y conectividad—todo en tu muñeca." \
  --exaggeration 1.3 \
  --cfg-weight 0.8 \
  --output ./test2_spanish.wav
```

3. **Japanese version**:
```bash
python cli.py speak "全く新しいSmartWatch Proをご紹介します。健康、フィットネス、接続性、すべてあなたの手首に。" \
  --exaggeration 1.3 \
  --cfg-weight 0.8 \
  --output ./test2_japanese.wav
```

**What to Try**:
1. Generate all three versions
2. Compare pronunciation quality across languages
3. Check for consistent energy/tone
4. Use for multilingual marketing campaigns

**Validation**:
- All languages should sound natural and native
- Pronunciation should be accurate
- Tone and energy should be consistent across languages
- No English accent in Spanish/Japanese versions

**Expected Output**:
- Professional, upbeat delivery
- Clear pronunciation of brand name "SmartWatch Pro"
- Appropriate emphasis on key features

---

### Test Case 3: Interactive Voice Assistant Responses

**Objective**: Generate varied responses for a voice assistant with different emotional contexts.

**Scenarios**:

1. **Helpful response** (neutral, informative):
```bash
python cli.py speak "I found 3 restaurants near you. The closest is Italian Kitchen, just 5 minutes away." \
  --exaggeration 1.0 \
  --cfg-weight 0.7 \
  --temperature 0.8 \
  --output ./test3_helpful.wav
```

2. **Apologetic response** (subdued, empathetic):
```bash
python cli.py speak "I'm sorry, I couldn't find any results for that search. Would you like me to try something else?" \
  --exaggeration 0.7 \
  --cfg-weight 0.8 \
  --temperature 0.6 \
  --output ./test3_apologetic.wav
```

3. **Enthusiastic response** (upbeat, encouraging):
```bash
python cli.py speak "Great job! You've completed your daily step goal for the 7th day in a row. Keep it up!" \
  --exaggeration 1.8 \
  --cfg-weight 0.7 \
  --temperature 1.3 \
  --output ./test3_enthusiastic.wav
```

**What to Try**:
1. Generate all three response types
2. Test different emotional contexts
3. Adjust parameters to match brand voice
4. Batch process multiple assistant responses
5. Create a response library for different scenarios

**Validation**:
- Helpful: Clear, friendly, professional tone
- Apologetic: Softer, empathetic, understanding tone
- Enthusiastic: Energetic, motivating, positive tone

**Expected Differences**:
- Pitch variation should reflect emotion
- Speaking rate should vary (faster for enthusiasm, slower for apology)
- Emphasis placement should feel natural

**Use Cases**:
- Voice assistant personalities
- Customer service bots
- Interactive tutorial narration
- App notifications and feedback

---

## How It Works

### Architecture

```
┌─────────────────┐
│  Local Machine  │
│   (CLI Client)  │
└────────┬────────┘
         │ 1. Send text + parameters
         ▼
┌─────────────────┐
│  Runpod Cloud   │
│   (GPU Server)  │
│                 │
│  ┌───────────┐  │
│  │  Handler  │  │ 2. Receive request
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │ 3. Load model
│  │Chatterbox │  │    (cached after first run)
│  │    TTS    │  │
│  └─────┬─────┘  │
│        │        │ 4. Synthesize speech
│        ▼        │
│  ┌───────────┐  │
│  │  WAV      │  │ 5. Encode to base64
│  │  Audio    │  │
│  └─────┬─────┘  │
└────────┼────────┘
         │ 6. Download audio
         ▼
┌─────────────────┐
│  Local Machine  │
│ (Save & Play)   │
└─────────────────┘
```

### Workflow

1. **Endpoint Creation**: CLI creates a Runpod serverless endpoint with specified GPU
2. **Initialization**: Endpoint loads Chatterbox TTS model (~2-3 minutes first time)
3. **Text Processing**: Input text is sent via HTTPS with synthesis parameters
4. **Inference**: Model generates speech (~10-30 seconds depending on text length)
5. **Download**: Audio is base64-encoded, sent back, and saved as WAV file
6. **Playback**: Audio automatically plays on macOS using `afplay`
7. **Cleanup**: Endpoint is automatically deleted to stop billing

### Cost Estimation

- **Endpoint initialization**: 2-3 minutes
- **Inference (100 words)**: 15-30 seconds
- **Total per generation**: ~3-4 minutes
- **Cost per generation (RTX 3060 Ti @ $0.14/hr)**: ~$0.007-0.01
- **Generations with $9 budget**: ~900-1,285 speech clips

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
3. Ensure template `runpod-chatterbox-tts` exists
4. Try different GPU type with `--gpu` option

### Issue: `Timeout waiting for endpoint`

**Solution**:
1. First run takes longer (~5 minutes) to download model weights
2. Check Runpod console for endpoint status
3. Try a less busy GPU type

### Issue: `Audio doesn't auto-play`

**Solution**:
- macOS: `afplay` should work by default
- Linux: Install `aplay` or use `--no-play` and manually open file
- Windows: Use `--no-play` and manually open WAV file
- Alternative: Play the saved WAV file manually

### Issue: `Job failed during inference`

**Solution**:
1. Check text length (very long text may need chunking)
2. Verify parameters are in valid ranges
3. Try reducing temperature or exaggeration
4. Check Runpod endpoint logs in console

### Issue: `Out of memory error`

**Solution**:
1. Use RTX 3060 (12GB) or RTX 4060 instead
2. Reduce text length (split into multiple requests)
3. Model should fit in 8GB; contact Runpod support if issues persist

---

## Advanced Configuration

### Using Different GPU Types

```bash
# Budget option (sufficient for most use cases)
python cli.py speak "Text" --gpu "NVIDIA RTX 3060 Ti"

# More headroom for longer text
python cli.py speak "Text" --gpu "NVIDIA RTX 3060"

# Performance option
python cli.py speak "Text" --gpu "NVIDIA RTX 4060"
```

### Batch Processing Multiple Texts

Create a script to process multiple lines:

```bash
#!/bin/bash
while IFS= read -r line; do
  python cli.py speak "$line" --no-play --output "./batch/$(echo $line | md5).wav"
done < input_texts.txt
```

### Fine-Tuning for Specific Use Cases

**For professional narration**:
```bash
python cli.py speak "Text" -e 0.8 -c 0.8 -t 0.7
```

**For character voices**:
```bash
python cli.py speak "Text" -e 1.5 -c 0.6 -t 1.3
```

**For news/announcements**:
```bash
python cli.py speak "Text" -e 1.0 -c 0.8 -t 0.8
```

---

## Project Structure

```
chatterbox_tts/
├── cli.py                  # Local CLI client
├── runpod_handler.py       # Runpod serverless handler
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── .env                   # Your API key (gitignored)
└── README.md              # This file
```

---

## Performance Tips

1. **Reuse endpoints**: If doing multiple generations, modify CLI to keep endpoint alive
2. **Optimal text length**: 50-200 words per request for best quality/cost ratio
3. **Parameter presets**: Save favorite parameter combinations
4. **GPU selection**: RTX 3060 Ti offers best price/performance for TTS
5. **Batch processing**: Process multiple texts in one endpoint session to save initialization time

---

## References

- [Chatterbox GitHub Repository](https://github.com/resemble-ai/chatterbox)
- [Resemble AI Official Page](https://www.resemble.ai/chatterbox/)
- [Chatterbox on Hugging Face](https://huggingface.co/ResembleAI/chatterbox)
- [Runpod Documentation](https://docs.runpod.io/)
- [Runpod Serverless Guide](https://docs.runpod.io/serverless/overview)

---

## License

This project wraps the Chatterbox TTS model (MIT license) for Runpod deployment.
