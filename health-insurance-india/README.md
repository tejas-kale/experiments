# 🏥 Health Insurance India CLI

> Query and compare Indian health insurance policies using AI agents powered by Anthropic's Claude

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude%204-purple.svg)](https://www.anthropic.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🤖 **AI-Powered Agent**: Uses Anthropic's Claude with custom tools to answer policy questions
- 💬 **Interactive CLI**: Beautiful terminal interface built with Typer and Rich
- 🔌 **REST API**: Complete FastAPI backend for integration with web/mobile apps
- 📄 **Document Management**: Add your own insurance PDFs for analysis
- 🏢 **Multi-Insurer Support**: Pre-configured collectors for major Indian insurers
- ⚖️ **Policy Comparison**: Side-by-side comparison of multiple policies
- 💰 **Premium Calculation**: Estimate premiums based on age, coverage, and family size
- 🔍 **Smart Search**: Search across all policy documents with context
- 📊 **Section Extraction**: Extract specific sections (exclusions, coverage, etc.)

## 🏢 Supported Insurers

- SBI General Insurance
- HDFC ERGO Health Insurance
- ICICI Lombard Health Insurance
- Star Health Insurance
- Care Health Insurance (formerly Religare)

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Installation

```bash
# Clone the repository
cd health-insurance-india

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Initialize Database

```bash
python cli.py db init
```

### Collect Policy Documents

```bash
# Collect from all insurers
python cli.py collect --all

# Or collect from specific insurer
python cli.py collect --insurer sbi_general
```

## 💬 CLI Usage

### Interactive Chat

Start a conversation with the AI agent:

```bash
python cli.py chat
```

Example conversation:

```
You: What are the waiting periods in HDFC Optima Secure?

🤖 Agent: Let me check the HDFC Optima Secure policy for you...

Based on the policy document, HDFC Optima Secure has the following waiting periods:

• **Initial Waiting Period**: 30 days from policy inception
  - No claims except accident-related can be made during this period

• **Pre-Existing Diseases**: 24-48 months depending on condition
  - Conditions existing before policy purchase
  - Waiting period varies by specific condition

• **Specific Disease Waiting Period**: 24 months
  - Includes: Hernia, Cataract, Joint Replacements, etc.

**Important**: Accident-related claims are covered immediately with no waiting period.

Sources: HDFC Optima Secure Policy Wording (pages 8-9)
```

### Single Question

Ask a one-off question:

```bash
python cli.py ask "What is the room rent limit in SBI Arogya Premier?"
```

### Compare Policies

```bash
python cli.py compare "SBI Arogya Premier, HDFC Optima Secure" --aspects "waiting_periods, exclusions"
```

### Get Policy Summary

```bash
python cli.py summarize --policy "Care Supreme"
```

### List Commands

```bash
# List all policies in database
python cli.py list-policies

# List all documents
python cli.py list-documents

# List supported insurers
python cli.py list-insurers
```

### Add Your Own Document

```bash
# From local file
python cli.py add-document /path/to/your/policy.pdf --insurer "Your Insurer" --product "Policy Name"

# From URL
python cli.py add-document https://example.com/policy.pdf
```

### Database Management

```bash
# Check database status
python cli.py db status

# Reset database (WARNING: Deletes all data)
python cli.py db reset
```

## 🔌 API Usage

### Start API Server

```bash
# Production
python cli.py serve

# Development with auto-reload
python cli.py serve --reload --port 8000
```

### API Documentation

Once the server is running, visit:

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example API Calls

#### Chat with Agent

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the major exclusions in Star Comprehensive policy?",
    "conversation_id": "user123"
  }'
```

#### Compare Policies

```bash
curl -X POST "http://localhost:8000/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "policy_ids": ["SBI Arogya Premier", "HDFC Optima Secure"],
    "aspects": ["waiting_periods", "major_exclusions"]
  }'
```

#### Calculate Premium

```bash
curl -X POST "http://localhost:8000/calculate-premium" \
  -H "Content-Type: application/json" \
  -d '{
    "policy_id": "Care Supreme",
    "age": 35,
    "sum_insured": 1000000,
    "family_members": 2
  }'
```

#### List Policies

```bash
curl "http://localhost:8000/policies"

# Filter by insurer
curl "http://localhost:8000/policies?insurer=HDFC"
```

#### Upload Document

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@/path/to/policy.pdf" \
  -F "insurer=My Insurer" \
  -F "product=My Policy"
```

## 🏗️ Architecture

```
health-insurance-india/
├── cli.py                      # Main CLI entry point (Typer + Rich)
├── api.py                      # FastAPI application
├── agents/
│   ├── insurance_agent.py     # Main agent with Anthropic SDK
│   ├── tools.py               # Custom tools for agent
│   └── prompts.py             # System prompts
├── collectors/
│   ├── base_collector.py      # Abstract collector
│   ├── sbi_collector.py       # SBI General collector
│   ├── hdfc_collector.py      # HDFC ERGO collector
│   └── ...                    # Other insurers
├── models/
│   ├── database.py            # SQLAlchemy models
│   └── schemas.py             # Pydantic schemas
├── services/
│   ├── document_service.py    # Document management
│   ├── policy_service.py      # Policy CRUD operations
│   └── extraction_service.py  # LLM-based extraction
├── utils/
│   ├── config.py              # Configuration
│   ├── logger.py              # Logging setup
│   └── pdf_utils.py           # PDF processing
└── data/
    ├── documents/             # All insurance PDFs
    ├── metadata/              # Extracted metadata
    └── policies.db            # SQLite database
```

## 🤖 Agent Tools

The AI agent has access to these custom tools:

1. **list_all_policies**: Lists all available policies
2. **search_policy_document**: Search across policy documents
3. **get_policy_details**: Get complete policy information
4. **extract_section**: Extract specific sections (exclusions, coverage, etc.)
5. **compare_policies**: Compare multiple policies
6. **calculate_premium**: Estimate premium based on user details
7. **get_document_text**: Get document text (full or specific pages)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_api.py
```

## 📝 Environment Variables

Create a `.env` file with:

```env
# Required
ANTHROPIC_API_KEY=your_api_key_here

# Optional
DATABASE_URL=sqlite:///./data/policies.db
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

## 🐳 Docker Deployment

```bash
# Build image
docker build -t health-insurance-india .

# Run container
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=your_key health-insurance-india

# Or use docker-compose
docker-compose up
```

## 📖 How It Works

### 1. Document Collection

Collectors scrape or download policy documents from insurer websites. Documents are saved locally and indexed in SQLite database.

### 2. Text Extraction

PyMuPDF extracts text from PDFs. Full text is stored in the database for fast searching.

### 3. Agent Processing

When you ask a question:

1. Agent receives your question
2. Agent decides which tools to use
3. Tools query the database/documents
4. Agent synthesizes information
5. Agent provides a comprehensive answer with sources

### 4. Smart Search

The agent can:
- Search across all documents
- Extract specific sections
- Compare multiple policies
- Calculate premiums
- Explain complex terms

## 🎯 Use Cases

### For Consumers

- **Compare Policies**: "Compare waiting periods in SBI vs HDFC policies"
- **Understand Terms**: "What does 'sub-limit' mean in my policy?"
- **Find Coverage**: "Does Star Health cover maternity expenses?"
- **Check Exclusions**: "What is NOT covered in Care Supreme?"
- **Calculate Cost**: "What would be the premium for a family of 4?"

### For Agents/Brokers

- Quick policy comparisons for clients
- Extract key information for presentations
- Calculate premiums for quotations
- Answer client questions with source citations

### For Developers

- REST API for building insurance comparison websites
- Integration with existing platforms
- Chatbot backends
- Premium calculators

## ⚠️ Important Notes

### Disclaimer

- Premium calculations are **estimates only**
- Actual premiums depend on medical history, location, and other factors
- Always verify information with the insurer directly
- This tool is for informational purposes only

### Data Privacy

- All processing happens locally
- No user data is sent to third parties (except Anthropic for AI processing)
- Policy documents are stored locally
- User-uploaded documents are private

## 🛠️ Development

### Adding a New Insurer

1. Create a new collector in `collectors/`:

```python
# collectors/new_insurer_collector.py
from collectors.base_collector import BaseCollector

class NewInsurerCollector(BaseCollector):
    def get_insurer_name(self) -> str:
        return "New Insurer"

    def get_base_url(self) -> str:
        return "https://newinsurer.com"

    def find_policy_urls(self) -> List[Dict[str, str]]:
        # Implement scraping logic
        pass
```

2. Register in `CollectorFactory` in `base_collector.py`

3. Run collection: `python cli.py collect --insurer new_insurer`

### Adding a New Tool

1. Add function in `agents/tools.py`:

```python
def my_new_tool(param1: str, param2: int) -> Dict[str, Any]:
    # Implementation
    return {"result": "data"}
```

2. Add tool definition to `TOOL_DEFINITIONS`

3. Add to `TOOL_FUNCTIONS` mapping

The agent will automatically have access to the new tool!

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/health-insurance-india/issues)
- **Documentation**: See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions

## 🙏 Acknowledgments

- **Anthropic** for Claude AI
- **FastAPI** for the excellent web framework
- **Typer** and **Rich** for beautiful CLI
- **PyMuPDF** for PDF processing

---

Made with ❤️ for better health insurance transparency in India
