# Contributing to Secure RunPod Chat

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/secure-runpod-chat.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/secure-runpod-chat.git
cd secure-runpod-chat

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

## Code Style

We follow PEP 8 style guidelines with some modifications:

- Line length: 100 characters
- Use type hints where applicable
- Write docstrings for all public functions and classes

### Formatting

```bash
# Format code with black
black src/

# Check with ruff
ruff check src/

# Type checking with mypy
mypy src/
```

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=secure_runpod_chat tests/

# Run specific test
pytest tests/test_utils.py
```

## Pull Request Process

1. **Update Documentation**: Ensure README.md and other docs reflect your changes
2. **Add Tests**: Include tests for new functionality
3. **Update Changelog**: Add your changes to CHANGELOG.md (if exists)
4. **Follow Code Style**: Run black and ruff before submitting
5. **Write Clear Commits**: Use descriptive commit messages
6. **Small PRs**: Keep pull requests focused and manageable

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat: Add support for custom Docker images

Added --docker-image flag to allow users to specify custom
Docker images for RunPod instances.

Closes #123
```

## Areas for Contribution

### High Priority

- [ ] Add unit tests for all modules
- [ ] Improve error handling and recovery
- [ ] Add support for more cloud providers
- [ ] Implement cost tracking and budgets
- [ ] Add model caching to speed up deployments

### Nice to Have

- [ ] Web UI for chat interface
- [ ] Support for streaming responses
- [ ] Integration with LangChain
- [ ] Conversation export formats (Markdown, JSON)
- [ ] Multi-user support

### Documentation

- [ ] Video tutorials
- [ ] More example use cases
- [ ] API documentation
- [ ] Troubleshooting guide

## Reporting Bugs

When reporting bugs, please include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: Detailed steps to reproduce the bug
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**:
   - OS and version
   - Python version
   - Package versions (`pip list`)
6. **Logs**: Relevant error messages or logs
7. **Screenshots**: If applicable

## Suggesting Features

When suggesting features, please include:

1. **Use Case**: Why is this feature needed?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: Other solutions you've considered
4. **Additional Context**: Any other relevant information

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Our Standards

- Use welcoming and inclusive language
- Respect differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

### Enforcement

Unacceptable behavior may be reported to the project maintainers.

## Questions?

Feel free to open an issue with the `question` label or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
