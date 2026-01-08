# Usage Examples

This document provides detailed examples of using the Health Insurance India CLI and API.

## CLI Examples

### 1. Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python cli.py db init

# Add sample policies for testing
python cli.py db add-sample

# Check database status
python cli.py db status
```

### 2. Exploring Policies

```bash
# List all available policies
python cli.py list-policies

# Output:
# Insurance Policies                                      
# ┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
# ┃ ID ┃ Insurer               ┃ Product            ┃
# ┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
# │ 1  │ Star Health Insurance │ Star Comprehensive │
# │ 2  │ HDFC ERGO             │ Optima Secure      │
# └────┴───────────────────────┴────────────────────┘
```

### 3. Document Management

```bash
# List all documents
python cli.py list-documents

# Add your own document
python cli.py add-document ~/Downloads/my-policy.pdf \
  --insurer "Star Health" \
  --product "My Health Plan"
```

### 4. Using the AI Agent (Requires API Key)

Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

#### Single Question Mode
```bash
# Ask a specific question
python cli.py ask "What are the waiting periods for pre-existing diseases?"

# Compare policies
python cli.py compare "Star Comprehensive,HDFC Optima Secure"

# Get a policy summary
python cli.py summarize --policy "Star Comprehensive"
```

#### Interactive Chat Mode
```bash
python cli.py chat
```

Example chat session:
```
╭─────────────────────────────────────────╮
│  Health Insurance Agent                 │
│  Powered by Anthropic Agents SDK        │
╰─────────────────────────────────────────╯

You: List all available policies

Agent: I'll check what policies are available in our database.

Based on the available policies, I found 2 health insurance options:

1. **Star Comprehensive** by Star Health Insurance
   - UIN: SHAHLIP21374V022021
   - Coverage Range: ₹5 Lakh to ₹25 Lakh
   - Age Eligibility: 18-65 years

2. **Optima Secure** by HDFC ERGO
   - UIN: HDFHLIP21374V012021
   - Coverage Range: ₹3 Lakh to ₹50 Lakh
   - Age Eligibility: 18-65 years

Would you like more details about any specific policy?

You: Compare the waiting periods

Agent: Let me compare the waiting periods for both policies.

**Waiting Period Comparison:**

**Star Comprehensive:**
- Initial waiting period: 30 days
- Pre-existing diseases: 48 months
- Specific diseases: 24 months

**HDFC Optima Secure:**
- Initial waiting period: 30 days
- Pre-existing diseases: 36 months
- Specific diseases: 24 months

**Key Difference:** HDFC Optima Secure has a shorter waiting period for 
pre-existing diseases (36 months vs 48 months), which could be beneficial 
if you have any pre-existing conditions.

You: What about exclusions?

Agent: I'll retrieve the major exclusions for both policies.

**Common Exclusions in Both Policies:**
- Cosmetic surgery
- Experimental treatments
- Self-inflicted injuries
- War and terrorism

**Star Comprehensive Specific:**
- Obesity treatment

**HDFC Optima Secure Specific:**
- Drug abuse
- Adventure sports

Both policies exclude pre-existing diseases for the initial waiting period.

You: exit
```

### 5. Database Operations

```bash
# Check database statistics
python cli.py db status

# Output:
# Database Status       
# ┏━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
# ┃ Metric        ┃    Value ┃
# ┡━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
# │ Policies      │        2 │
# │ Documents     │        0 │
# │ Database Size │ 16.00 KB │
# └───────────────┴──────────┘
```

## API Examples

### 1. Starting the Server

```bash
# Start with CLI
python cli.py serve

# Or directly with uvicorn
uvicorn api:app --reload

# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 2. Using the REST API

#### List All Policies
```bash
curl http://localhost:8000/policies
```

Response:
```json
{
  "count": 2,
  "policies": [
    {
      "id": 1,
      "insurer": "Star Health Insurance",
      "product": "Star Comprehensive",
      "uin": "SHAHLIP21374V022021",
      "sum_insured_range": {
        "min": 500000,
        "max": 2500000
      }
    },
    {
      "id": 2,
      "insurer": "HDFC ERGO",
      "product": "Optima Secure",
      "uin": "HDFHLIP21374V012021",
      "sum_insured_range": {
        "min": 300000,
        "max": 5000000
      }
    }
  ]
}
```

#### Get Policy Details
```bash
curl http://localhost:8000/policies/1
```

Response:
```json
{
  "id": 1,
  "insurer": "Star Health Insurance",
  "product": "Star Comprehensive",
  "details": {
    "id": 1,
    "insurer_name": "Star Health Insurance",
    "product_name": "Star Comprehensive",
    "uin_number": "SHAHLIP21374V022021",
    "min_sum_insured": 500000,
    "max_sum_insured": 2500000,
    "min_age": 18,
    "max_age": 65,
    "waiting_periods": {
      "initial": "30 days",
      "pre_existing": "48 months",
      "specific_diseases": "24 months"
    },
    "key_features": [
      "Cashless treatment at network hospitals",
      "Pre and post hospitalization coverage",
      "No room rent capping",
      "Annual health checkup"
    ],
    "major_exclusions": [
      "Pre-existing diseases (first 48 months)",
      "Cosmetic surgery",
      "Obesity treatment",
      "Experimental treatments"
    ]
  }
}
```

#### Chat with Agent
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the best policy for a family of 4?",
    "conversation_id": "session123"
  }'
```

Response:
```json
{
  "response": "For a family of 4, I'd recommend considering both policies...",
  "sources": [],
  "conversation_id": "session123"
}
```

#### Compare Policies
```bash
curl -X POST http://localhost:8000/compare \
  -H "Content-Type: application/json" \
  -d '{
    "policy_ids": ["1", "2"],
    "aspects": ["waiting_periods", "major_exclusions"]
  }'
```

## Python SDK Usage

### Using as a Library

```python
from models.database import init_db, get_db
from services.policy_service import PolicyService
from services.document_service import DocumentService
from agents.insurance_agent import InsuranceAgent
import os

# Initialize database
init_db()
db = get_db()

# Use policy service
policy_service = PolicyService(db)
policies = policy_service.list_all()
for policy in policies:
    print(f"{policy.product_name} by {policy.insurer_name}")

# Get specific policy
policy = policy_service.get_by_id_or_name("Star Comprehensive")
print(policy.to_dict())

# Use document service
doc_service = DocumentService(db)
doc_id = doc_service.add_user_document(
    path="/path/to/policy.pdf",
    insurer="Star Health",
    product="My Policy"
)

# Use AI agent
agent = InsuranceAgent(api_key=os.getenv("ANTHROPIC_API_KEY"))
response = agent.chat("What policies do you have?")
print(response)

# Continue conversation
response = agent.chat("Tell me more about waiting periods")
print(response)

# Reset conversation
agent.reset_conversation()
```

### Using Tools Directly

```python
from agents.tools import (
    list_all_policies,
    get_policy_details,
    search_policy_document,
    compare_policies,
    calculate_premium
)

# List policies
result = list_all_policies()
print(f"Found {result['count']} policies")

# Get policy details
details = get_policy_details("Star Comprehensive")
print(details['waiting_periods'])

# Search documents
results = search_policy_document(
    query="pre-existing disease",
    policy_id="1"
)

# Compare policies
comparison = compare_policies(
    policy_ids=["Star Comprehensive", "HDFC Optima Secure"],
    comparison_aspects=["waiting_periods", "major_exclusions"]
)

# Calculate premium
premium = calculate_premium(
    policy_id="Star Comprehensive",
    age=35,
    sum_insured=1000000,
    family_members=4
)
print(f"Estimated premium: ₹{premium['estimated_annual_premium']}")
```

## Docker Examples

### Using Docker Compose

```bash
# Set your API key
export ANTHROPIC_API_KEY=sk-ant-...

# Start services
docker-compose up

# API available at http://localhost:8000

# Interactive chat
docker-compose run cli python cli.py chat
```

### Using Dockerfile

```bash
# Build image
docker build -t health-insurance-cli .

# Run API server
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  health-insurance-cli

# Run CLI
docker run -it \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  health-insurance-cli \
  python cli.py chat
```

## Advanced Use Cases

### 1. Batch Processing Queries

```python
from agents.insurance_agent import InsuranceAgent
import os

agent = InsuranceAgent(api_key=os.getenv("ANTHROPIC_API_KEY"))

questions = [
    "What are the waiting periods for all policies?",
    "Which policy has the highest sum insured?",
    "Compare network hospitals across policies",
    "What are common exclusions?"
]

for question in questions:
    print(f"\nQ: {question}")
    response = agent.chat(question)
    print(f"A: {response}\n")
    print("-" * 80)
```

### 2. Building a Custom Tool

```python
# In agents/tools.py

def get_policies_by_age(age: int) -> dict:
    """Get policies available for a specific age"""
    from models.database import get_db
    from services.policy_service import PolicyService
    
    db = get_db()
    policies = PolicyService(db).list_all()
    
    eligible_policies = [
        p for p in policies
        if p.min_age <= age <= p.max_age
    ]
    
    return {
        "age": age,
        "eligible_policies": [
            {
                "id": p.id,
                "product": p.product_name,
                "insurer": p.insurer_name
            }
            for p in eligible_policies
        ]
    }

# Then add to InsuranceAgent's tools list
```

### 3. Exporting Data

```python
from models.database import get_db
from services.policy_service import PolicyService
import json

db = get_db()
policies = PolicyService(db).list_all()

# Export to JSON
with open('policies.json', 'w') as f:
    json.dump(
        [p.to_dict() for p in policies],
        f,
        indent=2
    )

# Export to CSV
import csv
with open('policies.csv', 'w') as f:
    writer = csv.DictWriter(
        f,
        fieldnames=['id', 'insurer_name', 'product_name', 'uin_number']
    )
    writer.writeheader()
    for p in policies:
        writer.writerow({
            'id': p.id,
            'insurer_name': p.insurer_name,
            'product_name': p.product_name,
            'uin_number': p.uin_number
        })
```

## Troubleshooting

### API Key Not Set
```bash
# Error: ANTHROPIC_API_KEY not configured
# Solution:
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Database Not Initialized
```bash
# Error: no such table: policies
# Solution:
python cli.py db init
```

### No Policies in Database
```bash
# Solution:
python cli.py db add-sample
```

### PDF Processing Errors
```bash
# Error: Failed to read PDF
# Ensure PyMuPDF is installed:
pip install --upgrade pymupdf
```

## Best Practices

1. **Always initialize the database first**: `python cli.py db init`
2. **Set API key in environment**: Never hardcode API keys
3. **Use specific policy names**: "Star Comprehensive" works better than "Star"
4. **Reset agent conversation**: Use `agent.reset_conversation()` for new topics
5. **Check database status**: Run `python cli.py db status` regularly

## Next Steps

- Explore the API documentation at `/docs` when running the server
- Try different questions in chat mode
- Add your own insurance documents
- Extend with custom tools
- Build a web UI on top of the API
