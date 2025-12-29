# Indian Health Insurance Assistant - Project Instructions

## Project Overview

This is a CLI-based assistant for helping users understand and navigate health insurance options in India. The application is currently in early development (WIP).

## Project Structure

```
indian_health_insurance_assistant/
├── cli.py              # Main CLI application entry point
├── requirements.txt    # Python dependencies
├── CLAUDE.md          # This file - project-specific instructions
└── README.md          # User documentation and testing instructions
```

## Technology Stack

- **Python**: 3.11+
- **CLI Framework**: Rich (for beautiful terminal formatting)
- **Package Manager**: uv

## Virtual Environment

The virtual environment for this project should be created in the project directory:
- Location: `./.venv`
- Created with: `uv venv`
- Activated with: `source .venv/bin/activate`

## Development Guidelines

### Architecture

This is a simple CLI application that will eventually integrate with:
- Health insurance policy databases
- AI-powered assistance for policy comparison
- Document analysis capabilities

For now, the CLI provides a placeholder response while the core functionality is being developed.

### Code Organization

- `cli.py`: Main entry point with banner display and chat loop
- Keep the CLI simple and focused on user interaction
- Business logic (policy comparison, AI integration) will be added in separate modules

### Dependencies

All dependencies are managed in `requirements.txt`. To install:
```bash
uv pip install -r requirements.txt
```

DO NOT execute `uv` commands directly - notify Tejas if new packages need to be installed.

### Testing

When functionality is added, tests should be created in a `tests/` directory using pytest.

## Current Status

**Phase**: Initial CLI interface
**Status**: WIP - Only displays welcome message

## Next Steps (Future)

1. Add database integration for insurance policies
2. Implement AI-powered policy comparison
3. Add document parsing for policy documents
4. Create comprehensive test suite
5. Add logging and error handling

## Notes

- The application currently returns a placeholder message: "Hi Tejas. This application is still WIP."
- The CLI uses Rich library for fancy terminal formatting
- All code follows the global CLAUDE.md guidelines (PEP8, type hints, etc.)
