# Health Insurance India CLI 🏥

> An AI-powered CLI tool to query and understand health insurance policies in India using Anthropic's Claude Agents SDK.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude--4-purple.svg)](https://www.anthropic.com/)

Ask questions, compare policies, and get instant answers about health insurance in India - all from your terminal or API.

## ✨ Features

- 🤖 **AI Agent**: Powered by Anthropic Claude with Agents SDK
- 💬 **Interactive Chat**: Natural language conversations about insurance
- 📊 **Policy Comparison**: Side-by-side comparison of multiple policies
- 🔍 **Smart Search**: Search across policy documents with context
- 📈 **Premium Calculation**: Get estimated premium quotes
- 📄 **Document Management**: Upload and manage your insurance documents
- 🎨 **Beautiful CLI**: Rich terminal UI with colors and tables
- 🌐 **REST API**: FastAPI server for web/mobile integration
- 🐳 **Docker Ready**: Easy deployment with Docker Compose

## Architecture 🏗️

```
health-insurance-india/
├── agents/           # AI agent implementation
│   ├── insurance_agent.py  # Main agent using Anthropic SDK
│   └── tools.py            # Agent tools (search, compare, etc.)
├── models/           # Database models
│   └── database.py         # SQLAlchemy models
├── services/         # Business logic
│   ├── policy_service.py   # Policy management
│   └── document_service.py # Document management
├── utils/            # Utilities
│   └── config.py           # Configuration
├── cli.py            # Typer CLI interface
├── api.py            # FastAPI server
└── requirements.txt  # Dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- [Anthropic API key](https://console.anthropic.com/) (for AI features)

### Installation

```bash
# Navigate to the project directory
cd health-insurance-india

# Install dependencies
pip install -r requirements.txt

# Set your API key (optional, but required for AI features)
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# Initialize the database
python cli.py db init

# Add sample policies for testing
python cli.py db add-sample

# Start using!
python cli.py list-policies
```

### Quick Demo (No API Key Required)

```bash
# List available policies
python cli.py list-policies

# Check database status
python cli.py db status
```

### With AI Agent (API Key Required)

```bash
# Interactive chat
python cli.py chat

# Ask a single question
python cli.py ask "What are the waiting periods for pre-existing diseases?"

# Compare policies
python cli.py compare "Star Comprehensive,HDFC Optima Secure"
```

## Usage 📖

### CLI Commands

#### Interactive Chat
```bash
python cli.py chat
```

Start an interactive conversation with the insurance agent.

#### Ask a Single Question
```bash
python cli.py ask "What are the waiting periods for Star Comprehensive?"
```

#### List Policies
```bash
python cli.py list-policies
```

#### Compare Policies
```bash
python cli.py compare "Star Comprehensive,HDFC Optima Secure"
```

#### Summarize a Policy
```bash
python cli.py summarize --policy "Star Comprehensive"
```

#### Add Your Document
```bash
python cli.py add-document /path/to/policy.pdf --insurer "Star Health" --product "My Policy"
```

#### List Documents
```bash
python cli.py list-documents
```

#### Database Operations
```bash
# Initialize database
python cli.py db init

# Check database status
python cli.py db status

# Add sample policies
python cli.py db add-sample
```

### API Server

Start the FastAPI server:
```bash
python cli.py serve
# Or directly:
uvicorn api:app --reload
```

API will be available at http://localhost:8000

Interactive docs at http://localhost:8000/docs

#### API Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `GET /policies` - List all policies
- `GET /policies/{policy_id}` - Get policy details
- `POST /chat` - Chat with agent
- `POST /query` - Query policies
- `POST /compare` - Compare policies
- `GET /documents` - List documents

Example API usage:
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the best policies for a family?"}'
```

## Agent Tools 🛠️

The AI agent has access to the following tools:

1. **list_all_policies**: List all available insurance policies
2. **search_policy_document**: Search across policy documents
3. **get_policy_details**: Get complete policy details
4. **extract_section**: Extract specific sections from policies
5. **compare_policies**: Compare multiple policies
6. **calculate_premium**: Calculate estimated premiums
7. **get_document_text**: Get document text

## Examples 💡

### Example 1: Finding the Best Policy
```bash
python cli.py ask "What's the best health insurance policy for a 35-year-old family of 4?"
```

### Example 2: Understanding Waiting Periods
```bash
python cli.py chat
> What are the waiting periods for pre-existing diseases across all policies?
```

### Example 3: Policy Comparison
```bash
python cli.py compare "Star Comprehensive,HDFC Optima Secure" --aspects "waiting_periods,exclusions"
```

### Example 4: Premium Estimation
```bash
python cli.py chat
> Calculate the premium for Star Comprehensive for age 40 with 10L sum insured
```

## Configuration ⚙️

Create a `.env` file:

```env
ANTHROPIC_API_KEY=your_api_key_here
```

## Development 🔧

### Project Structure

- **agents/**: AI agent implementation using Anthropic SDK
- **models/**: SQLAlchemy database models
- **services/**: Business logic layer
- **utils/**: Utilities and configuration
- **cli.py**: Typer-based CLI interface
- **api.py**: FastAPI server

### Adding New Insurers

To add support for new insurers, create a collector in `collectors/`:

```python
from collectors.base_collector import BaseCollector

class NewInsurerCollector(BaseCollector):
    def get_insurer_name(self) -> str:
        return "New Insurer"
    
    def get_base_url(self) -> str:
        return "https://newinsurer.com"
    
    def find_policy_urls(self) -> List[Dict[str, str]]:
        # Implementation
        pass
```

### Extending Tools

Add new tools in `agents/tools.py` and update the tool definitions in `agents/insurance_agent.py`.

## Testing 🧪

The application includes sample data for testing:

```bash
# Add sample policies
python cli.py db add-sample

# Test chat
python cli.py chat
```

## Deployment 🌐

### Local Development
```bash
python cli.py serve
```

### Production
```bash
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Tech Stack 💻

- **AI**: Anthropic Claude (Agents SDK)
- **CLI**: Typer + Rich
- **API**: FastAPI
- **Database**: SQLAlchemy + SQLite
- **PDF**: PyMuPDF
- **Web Scraping**: BeautifulSoup4 + Requests

## Roadmap 🗺️

- [ ] Add more insurers
- [ ] Implement autonomous collectors
- [ ] Add premium calculation from rate cards
- [ ] Web UI (React/Next.js)
- [ ] Multi-language support
- [ ] OCR for scanned documents
- [ ] Email integration for policy updates

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

MIT License

## Support 💬

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ using Anthropic Claude Agents SDK
