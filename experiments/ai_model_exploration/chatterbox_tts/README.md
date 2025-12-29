# Chatterbox Turbo TTS on Runpod

A CLI tool for running Chatterbox Turbo TTS on Runpod GPU instances for high-quality text-to-speech synthesis.

## Features

- **Chatterbox Turbo Model**: 10x faster than standard model with same quality
- **Automatic Text Chunking**: Handles long text (splits at 100 token limit)
- **MP3 Export**: Convert output to MP3 with configurable bitrate
- **Speed Control**: Adjust playback speed (default: 0.85x for better comprehension)
- **Text Preprocessing**: Automatically cleans formatting issues from copied text
- **Runpod Integration**: Serverless GPU inference with auto-scaling

## Quick Start

### 1. Install Dependencies

```bash
cd experiments/ai_model_exploration/chatterbox_tts
uv pip install -r requirements.txt
```

### 2. Get Required Credentials

- **Runpod API Key**: Get from [Runpod Settings](https://www.runpod.io/console/user/settings)
- **Hugging Face Token**: Get from [HF Settings](https://huggingface.co/settings/tokens)

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your RUNPOD_API_KEY and RUNPOD_ENDPOINT_ID
```

### 4. Setup Runpod Endpoint

**Option A: GitHub Integration (Recommended)**

1. Go to [Runpod Serverless](https://www.runpod.io/console/serverless)
2. Click "New Endpoint" → "Connect GitHub"
3. Select `tejas-kale/experiments` repository
4. Configure:
   - **Endpoint Name**: `chatterbox-tts`
   - **Branch**: `main`
   - **Build Context**: `experiments/ai_model_exploration/chatterbox_tts`
   - **Dockerfile Path**: `experiments/ai_model_exploration/chatterbox_tts/Dockerfile`
   - **GPU**: RTX 3060 Ti (8GB)
   - **Workers**: Min=0, Max=1
   - **Environment Variables**:
     - Name: `HF_TOKEN`
     - Value: Your Hugging Face token
5. Deploy and copy the Endpoint ID to `.env`

**Option B: Manual Template**

See `GITHUB_SETUP.md` for detailed manual setup instructions.

## Usage

### Basic Example

```bash
python cli.py speak "Hello! This is a test of Chatterbox TTS."
```

### From File

```bash
python cli.py speak --file example.txt --format mp3 --output output.mp3
```

### Available Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--file` | `-F` | None | Read text from file |
| `--save-preprocessed` | | None | Save preprocessed text for review |
| `--speed` | `-s` | `0.85` | Playback speed (0.5-2.0) |
| `--format` | `-f` | `wav` | Output format (wav or mp3) |
| `--bitrate` | `-b` | `192k` | MP3 bitrate (128k, 192k, 320k) |
| `--output` | `-o` | Auto | Output file path |
| `--play/--no-play` | | `True` | Auto-play after generation |

### Preprocess Text

```bash
python cli.py preprocess input.txt cleaned.txt
```

## Model Details

### Chatterbox Turbo

- **Architecture**: 350M parameters, distilled from standard model
- **Speed**: 10x faster (1-step mel decoder vs 10-step)
- **Latency**: Sub-200ms
- **Token Limit**: 100 tokens per chunk (automatically handled)
- **Parameters**: No tuning parameters (exaggeration, cfg_weight not supported in Turbo)

### Text Processing

- Automatically chunks long text at sentence boundaries
- Preserves natural speech flow across chunks
- Cleans formatting issues (indentation, line breaks)
- Concatenates audio chunks seamlessly

## Cost Estimates

**Recommended GPU**: RTX 3060 Ti @ $0.14/hour

- Per clip (~30s): $0.001-0.002
- $9 budget: ~4,500-9,000 clips
- **Auto-scaling** (min=0): Only pay when generating audio

## Files

- `cli.py` - Command-line interface
- `runpod_handler.py` - Serverless worker for Runpod
- `Dockerfile` - Container configuration
- `requirements.txt` - Python dependencies
- `debug_chatterbox.ipynb` - Google Colab notebook for testing
- `GITHUB_SETUP.md` - Detailed setup guide

## Troubleshooting

### Token Errors

If you see "Token is required" errors:
1. Get HF token from https://huggingface.co/settings/tokens
2. Add `HF_TOKEN` environment variable to Runpod endpoint
3. Rebuild/restart endpoint

### Audio Quality Issues

- Use `--save-preprocessed` to review cleaned text
- The `preprocess` command lets you test text cleaning separately
- Short 6-second audio suggests text preprocessing issues

### Build Failures

- Verify Dockerfile path: `experiments/ai_model_exploration/chatterbox_tts/Dockerfile`
- Check build context matches Dockerfile directory
- First build takes 5-10 minutes (downloads model weights)

## Development

### Testing Locally (Google Colab)

1. Upload `debug_chatterbox.ipynb` to Google Colab
2. Set runtime to GPU (T4)
3. Run all cells to test chunking logic
4. Adjust `max_tokens` parameter to test different chunk sizes

### Modifying Token Limit

Edit `runpod_handler.py` and change `max_tokens` in:
- `split_text_into_chunks()` default parameter
- `generate_long_audio()` threshold and function call

Current setting: 100 tokens (for testing aggressive chunking)

## License

MIT License - Chatterbox model from Resemble AI

## Links

- [Chatterbox GitHub](https://github.com/resemble-ai/chatterbox)
- [Runpod Docs](https://docs.runpod.io/)
- [Hugging Face](https://huggingface.co/ResembleAI/chatterbox-turbo)
