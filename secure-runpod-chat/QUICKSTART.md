# Quick Start Guide

Get started with Secure RunPod Chat in 5 minutes!

## Step 1: Install

```bash
cd secure-runpod-chat
pip install -e .
```

## Step 2: Set API Key

Get your RunPod API key from [runpod.io](https://runpod.io), then:

```bash
export RUNPOD_API_KEY="your-api-key-here"
```

Or create a `.env` file:

```bash
echo "RUNPOD_API_KEY=your-api-key-here" > .env
```

## Step 3: Run Your First Chat

```bash
secure-runpod-chat --model meta-llama/Llama-3.2-3B-Instruct
```

That's it! The tool will:

1. Detect the best GPU for your model
2. Create a RunPod instance
3. Deploy the model
4. Start an interactive chat

## Example Chat Session

```
You: What is machine learning?
Assistant: Machine learning is a subset of artificial intelligence that enables 
computers to learn from data without being explicitly programmed...

You: /exit

Terminate instance and exit? (y/N): y
```

## Tips

- Use `--quantize` for large models to reduce VRAM requirements
- Set `--max-cost-per-hour` to avoid unexpected costs
- Chat history is automatically saved and encrypted
- Press Ctrl+C to interrupt long responses

## Next Steps

- Check out the full [README.md](README.md) for advanced usage
- Try vision-language models with `/image` command
- Upload files with `/upload` for analysis
- Explore different models from Hugging Face Hub

## Common Models to Try

```bash
# Small, fast model
secure-runpod-chat --model meta-llama/Llama-3.2-3B-Instruct

# Vision-language model
secure-runpod-chat --model meta-llama/Llama-3.2-11B-Vision-Instruct

# Larger, more capable model (with quantization)
secure-runpod-chat --model meta-llama/Llama-3.2-70B-Instruct --quantize
```

## Need Help?

- Run `secure-runpod-chat --help` for all options
- Type `/help` in the chat for available commands
- Check [README.md](README.md) for detailed documentation
