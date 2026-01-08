# Architecture Overview

## System Architecture

The Health Insurance India CLI is built with a modular, layered architecture:

```
┌─────────────────────────────────────────────────────┐
│                  User Interfaces                     │
│  ┌──────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   CLI (Typer)│  │  REST API   │  │   Future    │ │
│  │   + Rich     │  │  (FastAPI)  │  │   Web UI    │ │
│  └──────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              AI Agent Layer                         │
│  ┌────────────────────────────────────────────────┐ │
│  │   InsuranceAgent (Anthropic Agents SDK)        │ │
│  │   - Conversation Management                    │ │
│  │   - Tool Orchestration                         │ │
│  │   - Response Generation                        │ │
│  └────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                   Tools Layer                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │  List    │  │  Search  │  │ Extract  │  ...     │
│  │ Policies │  │ Documents│  │ Sections │          │
│  └──────────┘  └──────────┘  └──────────┘          │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                 Service Layer                        │
│  ┌──────────────────┐  ┌──────────────────────┐    │
│  │  PolicyService   │  │  DocumentService     │    │
│  │  - CRUD          │  │  - CRUD              │    │
│  │  - Search        │  │  - PDF Processing    │    │
│  │  - Comparison    │  │  - Search            │    │
│  └──────────────────┘  └──────────────────────┘    │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                 Data Layer                           │
│  ┌────────────────────────────────────────────────┐ │
│  │          SQLAlchemy ORM                        │ │
│  │  ┌──────────────┐  ┌──────────────────────┐   │ │
│  │  │ Policy Model │  │  Document Model      │   │ │
│  │  └──────────────┘  └──────────────────────┘   │ │
│  └────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────┐ │
│  │          SQLite Database                       │ │
│  └────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## Component Details

### 1. User Interfaces

#### CLI (cli.py)
- Built with **Typer** for command structure
- Uses **Rich** for beautiful terminal output
- Commands:
  - `chat`: Interactive chat mode
  - `ask`: Single question mode
  - `list-policies`: Display all policies
  - `compare`: Compare policies
  - `summarize`: Get policy summary
  - `add-document`: Upload user documents
  - `db`: Database operations

#### REST API (api.py)
- Built with **FastAPI**
- Auto-generated OpenAPI docs at `/docs`
- Endpoints:
  - `GET /policies`: List policies
  - `GET /policies/{id}`: Get policy details
  - `POST /chat`: Chat with agent
  - `POST /compare`: Compare policies
  - `GET /documents`: List documents

### 2. AI Agent Layer

#### InsuranceAgent (agents/insurance_agent.py)
- Uses **Anthropic Claude** with Agents SDK
- Model: `claude-sonnet-4-20250514`
- Features:
  - Multi-turn conversations
  - Tool use and orchestration
  - Context management
  - Source citation

#### System Prompt
The agent is instructed to:
- Use tools for accurate information
- Explain terms in simple English
- Cite sources (policy name, section, page)
- Highlight warnings and exclusions
- Compare policies when asked
- Be conversational but precise

### 3. Tools Layer

All tools are defined in `agents/tools.py`:

1. **list_all_policies**: Returns all policies with basic info
2. **search_policy_document**: Full-text search across documents
3. **get_policy_details**: Complete policy information
4. **extract_section**: Extract specific document sections
5. **compare_policies**: Side-by-side policy comparison
6. **calculate_premium**: Premium estimation
7. **get_document_text**: Raw document text access

### 4. Service Layer

#### PolicyService (services/policy_service.py)
- CRUD operations for policies
- Search by ID, UIN, or name
- Flexible retrieval with `get_by_id_or_name()`
- Policy counting and listing

#### DocumentService (services/document_service.py)
- Document CRUD operations
- PDF processing with PyMuPDF
- Text extraction and indexing
- Search functionality
- User document uploads

### 5. Data Layer

#### Database Models (models/database.py)

**Policy Model:**
- Basic info: insurer, product name, UIN
- Coverage: sum insured ranges
- Eligibility: age ranges
- JSON fields: waiting periods, features, exclusions, etc.

**Document Model:**
- Metadata: insurer, product, type
- File info: path, name, page count
- Content: full text, sections
- User upload flag

#### Database
- **SQLite** for simplicity and portability
- **SQLAlchemy** ORM for flexibility
- Located at `data/policies.db`

## Data Flow

### Example: User asks "What policies are available?"

1. **CLI/API** receives user input
2. **InsuranceAgent** processes the message
3. Agent decides to use **list_all_policies** tool
4. Tool calls **PolicyService.list_all()**
5. **PolicyService** queries **SQLAlchemy**
6. **SQLite** returns policy records
7. Data flows back up through layers
8. **Agent** formats response in natural language
9. **CLI/API** displays formatted output to user

### Example: Agent comparison workflow

```
User: "Compare Star Comprehensive and HDFC Optima Secure"
  ↓
Agent receives request
  ↓
Agent uses compare_policies tool with policy_ids=["Star Comprehensive", "HDFC Optima Secure"]
  ↓
Tool uses PolicyService to fetch both policies
  ↓
Tool extracts comparison aspects (waiting_periods, exclusions, etc.)
  ↓
Tool returns structured comparison data
  ↓
Agent formats into readable comparison table
  ↓
User sees formatted comparison with highlights
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| AI | Anthropic Claude (Agents SDK) | Natural language understanding and generation |
| CLI | Typer | Command-line interface framework |
| UI | Rich | Beautiful terminal formatting |
| API | FastAPI | REST API framework |
| ORM | SQLAlchemy | Database abstraction |
| Database | SQLite | Data persistence |
| PDF | PyMuPDF | PDF text extraction |
| Web | BeautifulSoup4, Requests | Document collection (future) |

## Key Design Decisions

### 1. Anthropic Agents SDK
- **Why**: Native tool use, better context management, cleaner code
- **Alternative**: OpenAI Functions or LangChain
- **Benefit**: Simpler implementation, better tool orchestration

### 2. SQLite
- **Why**: Simplicity, portability, no server required
- **Alternative**: PostgreSQL or MongoDB
- **Benefit**: Easy deployment, file-based, perfect for CLI tool

### 3. Typer + Rich
- **Why**: Modern CLI experience, beautiful output
- **Alternative**: Click, argparse
- **Benefit**: Type hints, auto-completion, colored output

### 4. FastAPI
- **Why**: Modern, fast, auto-docs, type validation
- **Alternative**: Flask or Django
- **Benefit**: Built-in OpenAPI docs, async support

### 5. Modular Architecture
- **Why**: Separation of concerns, testability
- **Benefit**: Easy to extend, maintain, and test

## Extension Points

### Adding New Insurers
1. Create collector in `collectors/`
2. Inherit from `BaseCollector`
3. Implement `find_policy_urls()`
4. Run collector to populate database

### Adding New Tools
1. Add function in `agents/tools.py`
2. Update tool definitions in `agents/insurance_agent.py`
3. Agent automatically gets access to new capability

### Adding New Data Sources
1. Extend `Document` model if needed
2. Update `DocumentService` for new format
3. Tools automatically work with new data

## Security Considerations

1. **API Keys**: Stored in environment variables, never in code
2. **User Uploads**: Validated for file type and size
3. **SQL Injection**: Protected by SQLAlchemy ORM
4. **XSS**: Not applicable for CLI, API uses Pydantic validation

## Performance

- **Database**: Indexed by policy ID and UIN
- **Search**: Simple text search (can upgrade to FTS5)
- **Caching**: Agent conversation history in memory
- **API**: Async-capable with FastAPI

## Future Enhancements

1. **Full-text search**: SQLite FTS5 or Elasticsearch
2. **Vector embeddings**: Semantic search with embeddings
3. **OCR**: Extract text from scanned PDFs
4. **Web UI**: React/Next.js frontend
5. **Multi-language**: Support for regional languages
6. **Real-time updates**: WebSocket for chat
7. **Analytics**: Usage tracking and insights

## Deployment Options

### Local Development
```bash
python cli.py chat
```

### Docker
```bash
docker-compose up
```

### Cloud Deployment
- **Render/Railway**: Docker deployment
- **Vercel**: API only (serverless)
- **AWS Lambda**: Serverless API
- **Heroku**: Full stack deployment

## Testing Strategy

1. **Unit Tests**: Service and model layer
2. **Integration Tests**: Tool and agent layer
3. **CLI Tests**: Command validation
4. **API Tests**: Endpoint validation

Current test coverage focuses on core functionality:
- Database operations
- Service layer
- Tool execution

## Monitoring and Logging

- **Logging**: Python `logging` module
- **Errors**: Graceful error handling with user-friendly messages
- **API**: Request/response logging with uvicorn
- **Agent**: Conversation history tracking

## Conclusion

This architecture provides:
- ✅ Clean separation of concerns
- ✅ Easy to extend and maintain
- ✅ Multiple interface options (CLI, API)
- ✅ Powerful AI capabilities
- ✅ Simple deployment
- ✅ Good developer experience
