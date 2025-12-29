# Indian Health Insurance Assistant

A CLI-based assistant to help navigate and understand health insurance options in India.

## Overview

This application provides an interactive command-line interface for users to ask questions about health insurance policies available in India. It aims to simplify the complex landscape of health insurance by providing clear, personalized guidance.

**Current Status**: Work in Progress (WIP)

## Features

- Beautiful CLI interface with formatted output
- Interactive chat-based interaction
- Simple and intuitive command structure

## Requirements

- Python 3.11 or higher
- macOS (developed and tested on macOS)

## Installation & Setup

### 1. Create Virtual Environment

```bash
uv venv
```

This creates a virtual environment in `./.venv`.

### 2. Activate Virtual Environment

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
uv pip install -r requirements.txt
```

## Testing the Application

### Quick Start

Once you've completed the installation steps above, run:

```bash
python cli.py
```

### What to Expect

1. **Application Banner**: You'll see a fancy banner displaying "Indian Health Insurance Assistant"
2. **Welcome Panel**: A green panel with information about the application
3. **Chat Prompt**: An interactive prompt where you can type messages

### Test Scenarios

#### Scenario 1: Basic Interaction

```bash
python cli.py
```

1. Type any question (e.g., "What is health insurance?")
2. The assistant will respond: "Hi Tejas. This application is still WIP."
3. Type another question to verify the chat loop works
4. Type `exit` or `quit` to close the application

#### Scenario 2: Exit Commands

Test the different ways to exit:

```bash
python cli.py
```

- Type `exit` and press Enter
- Or type `quit` and press Enter
- Or press `Ctrl+C` (keyboard interrupt)
- Or press `Ctrl+D` (EOF)

All should gracefully close the application.

#### Scenario 3: Empty Input

```bash
python cli.py
```

- Press Enter without typing anything
- The application should continue waiting for input (not crash or respond)

### Expected Output Example

```
╔═══════════════════════════════════════════════════╗
║                                                   ║
║     Indian Health Insurance Assistant     ║
║                                                   ║
╚═══════════════════════════════════════════════════╝

╭─────────────────────── About ───────────────────────╮
│ Welcome to your personal health insurance           │
│ assistant for India!                                │
│ Type your questions about health insurance          │
│ policies and get expert guidance.                   │
│                                                      │
│ Commands: Type 'exit' or 'quit' to leave           │
╰──────────────────────────────────────────────────────╯

You: What insurance should I buy?
Assistant: Hi Tejas. This application is still WIP.

You: exit
Thank you for using Indian Health Insurance Assistant. Goodbye!
```

## Troubleshooting

### Issue: ModuleNotFoundError: No module named 'rich'

**Solution**: Make sure you've activated the virtual environment and installed dependencies:
```bash
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Issue: Command not found: uv

**Solution**: Install uv package manager:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Issue: Python version too old

**Solution**: This application requires Python 3.11+. Check your version:
```bash
python --version
```

If it's older than 3.11, install a newer version using pyenv or your preferred Python version manager.

## Project Structure

```
indian_health_insurance_assistant/
├── cli.py              # Main CLI application
├── requirements.txt    # Python dependencies
├── CLAUDE.md          # Project-specific instructions for Claude
└── README.md          # This file
```

## Future Enhancements

- Integration with health insurance policy databases
- AI-powered policy comparison and recommendations
- Document analysis for policy terms and conditions
- Personalized suggestions based on user profile
- Support for multiple insurance providers

## Contributing

This is a personal project currently in early development.

## License

TBD
