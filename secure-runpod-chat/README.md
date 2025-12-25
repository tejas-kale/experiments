# Secure RunPod Chat

A privacy-focused CLI tool that allows you to run Hugging Face models on RunPod GPU instances with automatic lifecycle management.

## Features

- **Automatic GPU Selection**: Intelligently determines the best GPU type based on model size
- **Privacy-Focused**: All communication via SSH, encrypted local chat history, automatic cleanup
- **Multi-Modal Support**: Handles both text-only and vision-language models
- **Optimized Inference**: Uses vLLM for compatible models, falls back to transformers
- **Interactive Chat**: Rich terminal UI with command support
- **File Management**: Upload/download files and images
- **Auto Cleanup**: Automatically terminates instances and clears remote data on exit
- **Cost Transparency**: Shows estimated and actual costs before and during usage

## Installation

### Prerequisites

- Python 3.8 or higher
- RunPod API key ([Get one here](https://runpod.io))
- pip or pipx for installation

### Install from Source

```bash
# Clone or navigate to the project directory
cd secure-runpod-chat

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

### Install with pipx (Recommended)

```bash
# Install with pipx for isolated environment
pipx install .
```

## Configuration

Set your RunPod API key as an environment variable:

```bash
export RUNPOD_API_KEY="your-api-key-here"
```

Or create a `.env` file in your working directory:

```
RUNPOD_API_KEY=your-api-key-here
```

## Usage

### Basic Usage

```bash
secure-runpod-chat --model meta-llama/Llama-3.2-3B-Instruct
```

### With Options

```bash
# Use specific GPU type
secure-runpod-chat --model meta-llama/Llama-3.2-11B-Vision-Instruct --gpu-type "NVIDIA A40"

# Set maximum cost per hour
secure-runpod-chat --model meta-llama/Llama-3.2-3B-Instruct --max-cost-per-hour 0.50

# Use quantization to reduce GPU requirements
secure-runpod-chat --model meta-llama/Llama-3.2-11B-Vision-Instruct --quantize

# Increase disk size
secure-runpod-chat --model meta-llama/Llama-3.2-3B-Instruct --disk-size 100

# Disable chat history saving
secure-runpod-chat --model meta-llama/Llama-3.2-3B-Instruct --no-history
```

### CLI Options

```
Options:
  -m, --model TEXT              HuggingFace model ID [required]
  -g, --gpu-type TEXT           GPU type to use (auto-detected if not specified)
  -c, --max-cost-per-hour FLOAT Maximum cost per hour in dollars
  -d, --disk-size INTEGER       Disk size in GB (default: 50)
  -q, --quantize                Use 4-bit quantization to reduce GPU requirements
  --no-history                  Disable encrypted chat history saving
  --use-vllm / --no-vllm        Use vLLM for optimized inference (default: True)
  --help                        Show help message and exit
```

## Interactive Commands

Once in the chat interface, you can use these commands:

- `/help` - Show help message
- `/upload <local_path>` - Upload a file to the instance
- `/download <remote_path> [local_path]` - Download a file from the instance
- `/image <path>` - Include an image in your message (vision models only)
- `/clear` - Clear chat history
- `/exit` or `/quit` - Exit and terminate the instance

## Examples

### Text-Only Model

```bash
$ secure-runpod-chat --model meta-llama/Llama-3.2-3B-Instruct

You: What is the capital of France?
Assistant: The capital of France is Paris.

You: /exit
```

### Vision-Language Model

```bash
$ secure-runpod-chat --model meta-llama/Llama-3.2-11B-Vision-Instruct

You: /image ~/Pictures/dog.jpg
You: What's in this image?
Assistant: This image shows a golden retriever dog sitting in a grassy field...

You: /exit
```

### With Quantization

```bash
# Run a large model with 4-bit quantization to reduce VRAM usage
secure-runpod-chat --model meta-llama/Llama-3.2-70B-Instruct --quantize
```

## How It Works

1. **Model Analysis**: Fetches model information from Hugging Face Hub and estimates size
2. **GPU Selection**: Automatically determines the best GPU type and count based on requirements
3. **Instance Creation**: Spins up a RunPod GPU instance with PyTorch and CUDA pre-installed
4. **SSH Connection**: Establishes secure SSH connection to the instance
5. **Model Deployment**: Deploys the model using vLLM (for compatible models) or transformers
6. **Interactive Chat**: Provides a rich terminal interface for chatting with the model
7. **Auto Cleanup**: On exit, clears all logs/temp files and terminates the instance

## Privacy & Security

### Data Protection

- All communication with the RunPod instance is via SSH (encrypted)
- Chat history is encrypted using Fernet (symmetric encryption) before saving locally
- Encryption key is stored in `~/.secure-runpod-chat/history/.key` with restricted permissions
- No data is sent to third-party services except RunPod

### Cleanup Process

When you exit, the tool automatically:

1. Clears remote logs and temporary files
2. Removes uploaded files and images
3. Clears Hugging Face cache
4. Terminates the RunPod instance
5. Verifies instance termination

### Security Best Practices

- Never commit your RunPod API key to version control
- Use environment variables or `.env` files for API keys
- Review costs before confirming instance creation
- Always exit properly to ensure cleanup
- Keep chat history encryption key secure

## File Management

### Uploading Files

```bash
You: /upload /path/to/local/file.txt
```

Files are uploaded to `/root/uploads/` on the instance.

### Downloading Files

```bash
You: /download /root/outputs/result.txt ./result.txt
```

If no local path is specified, the file is downloaded to the current directory.

### Using Images with Vision Models

```bash
You: /image /path/to/image.jpg
You: Describe this image in detail
```

Images are uploaded to `/root/images/` on the instance.

## Cost Estimation

The tool provides cost estimates before creating instances:

- **Estimated Cost**: Based on GPU type and count
- **Actual Cost**: Retrieved from RunPod API after instance creation

Example GPU costs (approximate):

- NVIDIA RTX A4000 (16GB): ~$0.34/hour
- NVIDIA RTX A5000 (24GB): ~$0.44/hour
- NVIDIA A40 (48GB): ~$0.79/hour
- NVIDIA RTX A6000 (48GB): ~$0.79/hour
- NVIDIA A100 80GB: ~$2.19/hour

Costs may vary based on availability and RunPod pricing.

## Troubleshooting

### Connection Issues

If SSH connection fails:

1. Wait a minute for the instance to fully start
2. Check that port 22 is exposed in RunPod settings
3. Verify your RunPod account has sufficient credits

### Model Loading Errors

If the model fails to load:

1. Check that you have enough disk space (increase with `--disk-size`)
2. Try using quantization (`--quantize`) for large models
3. Verify the model ID is correct on Hugging Face Hub

### Instance Not Terminating

If the instance doesn't terminate:

1. Check the RunPod dashboard
2. Manually terminate the instance if necessary
3. Report the issue with logs

## Chat History

Chat histories are saved to `~/.secure-runpod-chat/history/` in encrypted format.

### Viewing Chat History

To decrypt and view a chat history:

```python
from cryptography.fernet import Fernet
import json
from pathlib import Path

# Read encryption key
key_file = Path.home() / ".secure-runpod-chat/history/.key"
key = key_file.read_bytes()

# Read and decrypt history
history_file = Path.home() / ".secure-runpod-chat/history/your-history-file.enc"
encrypted_data = history_file.read_bytes()

fernet = Fernet(key)
decrypted_data = fernet.decrypt(encrypted_data)
history = json.loads(decrypted_data)

print(json.dumps(history, indent=2))
```

## Advanced Usage

### Custom Docker Image

Edit `runpod_manager.py` to specify a custom Docker image:

```python
docker_image="your-custom-image:tag"
```

### Multiple GPUs

The tool automatically determines GPU count based on model size, but you can modify the logic in `utils.py`:

```python
def determine_gpu_requirements(model_size_gb: float, is_vision: bool = False):
    # Your custom logic here
    ...
```

### Custom Model Server

You can modify the model server scripts in `model_deployer.py` to customize inference parameters, add custom preprocessing, etc.

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
ruff check src/
```

### Type Checking

```bash
mypy src/
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Disclaimer

This tool creates GPU instances on RunPod which incur costs. Always monitor your usage and ensure instances are properly terminated. The authors are not responsible for any charges incurred.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Acknowledgments

- Built with [RunPod](https://runpod.io) for GPU infrastructure
- Uses [vLLM](https://github.com/vllm-project/vllm) for optimized inference
- Uses [transformers](https://github.com/huggingface/transformers) from Hugging Face
- Terminal UI powered by [Rich](https://github.com/Textualize/rich)
