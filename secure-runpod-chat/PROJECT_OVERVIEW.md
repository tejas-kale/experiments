# Secure RunPod Chat - Project Overview

## Project Structure

```
secure-runpod-chat/
├── src/
│   └── secure_runpod_chat/
│       ├── __init__.py           # Package initialization
│       ├── __main__.py            # Entry point for python -m
│       ├── cli.py                 # CLI interface and main logic
│       ├── runpod_manager.py      # RunPod instance lifecycle management
│       ├── ssh_client.py          # SSH connection and file transfer
│       ├── model_deployer.py      # Model deployment (vLLM/transformers)
│       ├── chat_interface.py      # Interactive chat UI
│       └── utils.py               # Utility functions
├── examples/
│   ├── basic_usage.sh             # Basic usage examples
│   ├── vision_model_example.md    # Vision model examples
│   └── file_management.md         # File upload/download examples
├── pyproject.toml                 # Project metadata and dependencies
├── requirements.txt               # Python dependencies
├── README.md                      # Main documentation
├── QUICKSTART.md                  # Quick start guide
├── CONTRIBUTING.md                # Contribution guidelines
├── SECURITY.md                    # Security policy
├── LICENSE                        # MIT License
├── .gitignore                     # Git ignore rules
└── .env.example                   # Example environment file
```

## Module Descriptions

### `cli.py` - Command Line Interface

**Purpose**: Main entry point for the application

**Key Functions**:
- `main()`: CLI command handler with click decorators
- `cleanup_handler()`: Cleanup on exit or interrupt

**Features**:
- Argument parsing with click
- Environment variable loading
- Signal handling for graceful shutdown
- Cost estimation and confirmation
- Orchestrates all other modules

### `runpod_manager.py` - RunPod Instance Management

**Purpose**: Manages RunPod GPU instance lifecycle

**Key Features**:
- Create instances with specific GPU types
- Wait for instance readiness
- Monitor instance status
- Terminate and verify deletion
- Display instance information

**Methods**:
- `create_instance()`: Create RunPod GPU instance
- `get_ssh_connection_info()`: Get SSH connection details
- `terminate_instance()`: Terminate instance
- `verify_termination()`: Verify instance deleted

### `ssh_client.py` - SSH Communication

**Purpose**: Secure SSH communication with RunPod instances

**Key Features**:
- SSH connection with retries
- Command execution (with/without streaming)
- File upload/download with progress bars
- Remote file management
- Automatic cleanup

**Methods**:
- `connect()`: Connect to SSH server
- `execute_command()`: Run commands
- `upload_file()`: Upload files with progress
- `download_file()`: Download files with progress
- `cleanup_remote_files()`: Clean up remote data

### `model_deployer.py` - Model Deployment

**Purpose**: Deploy and manage Hugging Face models

**Key Features**:
- Environment setup
- vLLM or transformers deployment
- Model server management
- Inference handling

**Methods**:
- `setup_environment()`: Install dependencies
- `install_vllm()`: Install vLLM
- `deploy_model()`: Deploy model (vLLM or transformers)
- `start_model_server()`: Start model server
- `send_chat_message()`: Send inference requests

**Deployment Strategies**:
1. **vLLM**: For text-only models (faster, more efficient)
2. **Transformers**: For vision models or fallback

### `chat_interface.py` - Interactive Chat

**Purpose**: Rich terminal chat interface

**Key Features**:
- Interactive chat with model
- Command handling (/help, /upload, /download, etc.)
- Encrypted chat history
- Rich terminal UI

**Commands**:
- `/help`: Show help
- `/upload <path>`: Upload file
- `/download <remote> [local]`: Download file
- `/image <path>`: Upload image (vision models)
- `/clear`: Clear history
- `/exit`: Exit and cleanup

**Methods**:
- `run()`: Main chat loop
- `handle_upload_command()`: File uploads
- `handle_download_command()`: File downloads
- `handle_image_command()`: Image uploads

### `utils.py` - Utility Functions

**Purpose**: Common utility functions

**Functions**:
- `get_model_info()`: Fetch model info from HF Hub
- `estimate_model_size_gb()`: Estimate model size
- `determine_gpu_requirements()`: Auto-select GPU
- `is_vision_model()`: Detect vision models
- `validate_api_key()`: Validate RunPod API key
- `confirm_action()`: User confirmation prompts
- `sanitize_path()`: Prevent path traversal

## Architecture

### High-Level Flow

```
1. CLI Start (cli.py)
   ↓
2. Validate API Key
   ↓
3. Fetch Model Info (utils.py)
   ↓
4. Determine GPU Requirements (utils.py)
   ↓
5. Create RunPod Instance (runpod_manager.py)
   ↓
6. Connect via SSH (ssh_client.py)
   ↓
7. Deploy Model (model_deployer.py)
   ├── Setup Environment
   ├── Install vLLM/transformers
   └── Start Model Server
   ↓
8. Start Chat Interface (chat_interface.py)
   ├── User Input Loop
   ├── Command Handling
   └── Model Inference
   ↓
9. Cleanup on Exit (cli.py)
   ├── Clear Remote Files (ssh_client.py)
   ├── Terminate Instance (runpod_manager.py)
   └── Verify Deletion
```

### Data Flow

```
User Input
   ↓
CLI (click) → Chat Interface
                    ↓
              Command Parser
                    ↓
         ┌──────────┴──────────┐
         ↓                     ↓
    File Upload          Chat Message
         ↓                     ↓
    SSH Client          Model Deployer
         ↓                     ↓
    RunPod Instance ← SSH Client
         ↓
    Model Response
         ↓
    Chat Interface
         ↓
    Display to User
```

## Security Architecture

### Layers of Protection

1. **Transport Security**:
   - SSH encryption for all communication
   - No plain-text data transmission

2. **Data Protection**:
   - Local chat history encrypted with Fernet
   - Encryption key stored with restricted permissions (0600)

3. **Cleanup**:
   - Automatic cleanup on exit
   - Signal handlers for interrupts
   - Verification of instance termination

4. **Input Validation**:
   - Path sanitization
   - API key validation
   - Parameter validation

## Key Technologies

- **Click**: CLI argument parsing
- **Rich**: Terminal UI and formatting
- **Paramiko**: SSH client library
- **RunPod SDK**: RunPod API integration
- **Cryptography**: Chat history encryption
- **Hugging Face Hub**: Model information and downloads
- **vLLM**: Optimized inference (when applicable)
- **Transformers**: Model inference (fallback)

## Configuration

### Environment Variables

- `RUNPOD_API_KEY`: RunPod API key (required)

### CLI Options

- `--model`: Hugging Face model ID (required)
- `--gpu-type`: GPU type (optional, auto-detected)
- `--max-cost-per-hour`: Cost limit (optional)
- `--disk-size`: Disk size in GB (default: 50)
- `--quantize`: Use 4-bit quantization
- `--no-history`: Disable chat history
- `--use-vllm/--no-vllm`: Use vLLM (default: True)

## Development Guidelines

### Adding New Features

1. **New Commands**: Add to `chat_interface.py`
2. **GPU Support**: Update `utils.py` GPU mapping
3. **Model Types**: Extend `model_deployer.py`
4. **Cloud Providers**: Create new manager (similar to `runpod_manager.py`)

### Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

### Code Style

- Follow PEP 8
- Line length: 100 characters
- Use type hints
- Write docstrings
- Use Rich console for output

## Future Enhancements

### Planned Features

- [ ] Streaming responses
- [ ] Multi-cloud support (AWS, GCP, Azure)
- [ ] Web UI
- [ ] Model caching
- [ ] Conversation export
- [ ] Cost tracking and budgets
- [ ] Multi-user support
- [ ] LangChain integration

### Performance Improvements

- [ ] Parallel model loading
- [ ] Connection pooling
- [ ] Caching model metadata
- [ ] Optimized file transfers

## Troubleshooting

### Common Issues

1. **SSH Connection Fails**:
   - Solution: Wait for instance to fully start
   - Check: RunPod dashboard for instance status

2. **Model Loading Fails**:
   - Solution: Increase disk size with `--disk-size`
   - Try: Use `--quantize` for large models

3. **Instance Not Terminating**:
   - Solution: Manually terminate in RunPod dashboard
   - Check: `verify_termination()` output

4. **Cost Higher Than Expected**:
   - Solution: Set `--max-cost-per-hour` limit
   - Check: RunPod pricing page

## Resources

- [RunPod Documentation](https://docs.runpod.io)
- [Hugging Face Hub](https://huggingface.co)
- [vLLM Documentation](https://docs.vllm.ai)
- [Paramiko Documentation](https://docs.paramiko.org)
- [Rich Documentation](https://rich.readthedocs.io)

## License

MIT License - See LICENSE file for details
