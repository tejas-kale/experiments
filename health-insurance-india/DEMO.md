# Demo: Health Insurance India CLI

This document provides a quick demo of the Health Insurance India CLI capabilities.

## Setup

```bash
cd health-insurance-india
pip install -r requirements.txt
python cli.py db init
python cli.py db add-sample
```

## Demo Scenarios

### 1. List Available Policies

```bash
$ python cli.py list-policies
```

Output:
```
Insurance Policies                                      
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃ ID ┃ Insurer               ┃ Product            ┃ UIN                 ┃ Sum Insured Range ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ 1  │ Star Health Insurance │ Star Comprehensive │ SHAHLIP21374V022021 │    ₹5.0L - ₹25.0L │
│ 2  │ HDFC ERGO             │ Optima Secure      │ HDFHLIP21374V012021 │    ₹3.0L - ₹50.0L │
└────┴───────────────────────┴────────────────────┴─────────────────────┴───────────────────┘
```

### 2. Ask Questions (with Anthropic API Key)

Set your API key:
```bash
export ANTHROPIC_API_KEY=your_key_here
```

Ask a question:
```bash
$ python cli.py ask "What are the waiting periods for Star Comprehensive?"
```

The AI agent will:
1. Use the `get_policy_details` tool to fetch policy information
2. Extract waiting period details
3. Provide a clear, formatted answer with citations

### 3. Interactive Chat

```bash
$ python cli.py chat
```

Example conversation:
```
You: What policies are available?
Agent: [Agent lists policies using list_all_policies tool]

You: Compare Star Comprehensive and HDFC Optima Secure
Agent: [Agent uses compare_policies tool and provides detailed comparison]

You: What are the exclusions for Star Comprehensive?
Agent: [Agent extracts exclusions and explains them in simple terms]
```

### 4. Policy Comparison

```bash
$ python cli.py compare "Star Comprehensive,HDFC Optima Secure"
```

### 5. Policy Summary

```bash
$ python cli.py summarize --policy "Star Comprehensive"
```

### 6. Database Operations

```bash
# Check database status
$ python cli.py db status

# Add more sample data
$ python cli.py db add-sample
```

### 7. Add Your Own Document

```bash
$ python cli.py add-document /path/to/policy.pdf --insurer "Star Health" --product "My Policy"
```

### 8. REST API Server

Start the API server:
```bash
$ python cli.py serve
# Or: uvicorn api:app --reload
```

The API will be available at `http://localhost:8000`

Interactive API documentation: `http://localhost:8000/docs`

Example API calls:

```bash
# List policies
curl http://localhost:8000/policies

# Chat with agent
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the best policies for a family?"}'

# Compare policies
curl -X POST http://localhost:8000/compare \
  -H "Content-Type: application/json" \
  -d '{"policy_ids": ["1", "2"], "aspects": ["waiting_periods", "exclusions"]}'
```

## Agent Tools

The AI agent has access to these tools:

1. **list_all_policies**: Lists all available insurance policies
2. **search_policy_document**: Searches across policy documents
3. **get_policy_details**: Gets complete policy details
4. **extract_section**: Extracts specific sections (e.g., "Exclusions")
5. **compare_policies**: Compares multiple policies
6. **calculate_premium**: Calculates estimated premiums
7. **get_document_text**: Gets document text

## Example Agent Workflows

### Workflow 1: Finding the Best Policy
User: "What's the best policy for a 35-year-old family of 4?"

Agent workflow:
1. Calls `list_all_policies()` to see available options
2. Calls `get_policy_details()` for each policy
3. Compares age limits, family coverage, and features
4. Calls `calculate_premium()` for relevant policies
5. Provides a comprehensive recommendation

### Workflow 2: Understanding Waiting Periods
User: "What are the waiting periods for pre-existing diseases?"

Agent workflow:
1. Calls `list_all_policies()` to get all policies
2. Calls `get_policy_details()` for each policy
3. Extracts `waiting_periods` from each
4. Compares and explains in simple terms
5. Highlights important warnings

### Workflow 3: Deep Dive into Exclusions
User: "Tell me about exclusions in Star Comprehensive"

Agent workflow:
1. Calls `get_policy_details("Star Comprehensive")`
2. Extracts `major_exclusions`
3. Optionally calls `extract_section()` for full exclusions text
4. Explains each exclusion in simple language
5. Highlights critical points

## Sample Output

When you run the chat command without an API key, you'll see:
```
Error: ANTHROPIC_API_KEY not configured
Set ANTHROPIC_API_KEY environment variable
```

With a valid API key, you get:
```
╭─────────────────────────────────────────╮
│  Health Insurance Agent                 │
│  Powered by Anthropic Agents SDK        │
╰─────────────────────────────────────────╯

Ask me anything about health insurance policies!

You: What policies are available?

Agent:
I found 2 health insurance policies in the database:

1. **Star Comprehensive** by Star Health Insurance
   - UIN: SHAHLIP21374V022021
   - Sum Insured Range: ₹5L - ₹25L
   
2. **Optima Secure** by HDFC ERGO
   - UIN: HDFHLIP21374V012021
   - Sum Insured Range: ₹3L - ₹50L

Would you like me to provide more details about any of these policies?
```

## Features Demonstrated

✅ Beautiful CLI interface with Rich formatting
✅ Database initialization and management
✅ Sample data for testing
✅ Policy listing with formatted tables
✅ AI agent integration (requires API key)
✅ REST API server
✅ Interactive chat mode
✅ Single question mode
✅ Policy comparison
✅ Document management

## Next Steps

1. Set up your `ANTHROPIC_API_KEY` to enable AI agent features
2. Add your own insurance documents
3. Ask questions about your policies
4. Use the API to integrate with web applications
5. Extend the system with more insurers and documents
