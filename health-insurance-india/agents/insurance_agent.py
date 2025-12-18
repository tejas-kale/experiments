"""Insurance advisor agent using Anthropic Agents SDK"""

import anthropic
import json
from typing import List, Dict, Any
from agents.tools import (
    list_all_policies,
    search_policy_document,
    get_policy_details,
    extract_section,
    compare_policies,
    calculate_premium,
    get_document_text
)


class InsuranceAgent:
    """AI agent for insurance advisory"""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Define tools for Anthropic
        self.tools = [
            {
                "name": "list_all_policies",
                "description": "List all available health insurance policies in the database. Returns policy names, insurers, UIN numbers, and sum insured ranges.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "search_policy_document",
                "description": "Search for specific information across policy documents. Use this to find details about coverage, exclusions, waiting periods, etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (e.g., 'pre-existing disease waiting period')"
                        },
                        "policy_id": {
                            "type": "string",
                            "description": "Optional: Limit search to specific policy ID or name"
                        },
                        "section": {
                            "type": "string",
                            "description": "Optional: Search within specific section"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_policy_details",
                "description": "Get complete details of a specific insurance policy including features, exclusions, waiting periods, and warnings.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "policy_id": {
                            "type": "string",
                            "description": "Policy ID, UIN number, or policy name"
                        }
                    },
                    "required": ["policy_id"]
                }
            },
            {
                "name": "extract_section",
                "description": "Extract a specific section from a policy document (e.g., 'Exclusions', 'Waiting Period', 'Coverage Details').",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "policy_id": {
                            "type": "string",
                            "description": "Policy ID or name"
                        },
                        "section_name": {
                            "type": "string",
                            "description": "Name of the section to extract"
                        }
                    },
                    "required": ["policy_id", "section_name"]
                }
            },
            {
                "name": "compare_policies",
                "description": "Compare multiple insurance policies across various aspects like waiting periods, exclusions, coverage, etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "policy_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of policy IDs or names to compare"
                        },
                        "comparison_aspects": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional: Specific aspects to compare (e.g., ['waiting_periods', 'major_exclusions'])"
                        }
                    },
                    "required": ["policy_ids"]
                }
            },
            {
                "name": "calculate_premium",
                "description": "Calculate estimated premium for a policy based on age, sum insured, and family size.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "policy_id": {
                            "type": "string",
                            "description": "Policy ID or name"
                        },
                        "age": {
                            "type": "integer",
                            "description": "Age of the proposer"
                        },
                        "sum_insured": {
                            "type": "integer",
                            "description": "Optional: Sum insured amount in rupees"
                        },
                        "family_members": {
                            "type": "integer",
                            "description": "Number of family members to be covered (default: 1)"
                        }
                    },
                    "required": ["policy_id", "age"]
                }
            },
            {
                "name": "get_document_text",
                "description": "Get the full text or specific pages from a policy document.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "Document ID"
                        },
                        "page_start": {
                            "type": "integer",
                            "description": "Optional: Starting page number"
                        },
                        "page_end": {
                            "type": "integer",
                            "description": "Optional: Ending page number"
                        }
                    },
                    "required": ["document_id"]
                }
            }
        ]
    
    def process_tool_call(self, tool_name: str, tool_input: dict) -> dict:
        """Execute tool and return result"""
        tool_functions = {
            "list_all_policies": list_all_policies,
            "search_policy_document": search_policy_document,
            "get_policy_details": get_policy_details,
            "extract_section": extract_section,
            "compare_policies": compare_policies,
            "calculate_premium": calculate_premium,
            "get_document_text": get_document_text
        }
        
        if tool_name in tool_functions:
            return tool_functions[tool_name](**tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    def chat(self, user_message: str) -> str:
        """Main chat interface using Agents SDK"""
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # System prompt
        system_prompt = """You are an expert insurance advisor helping users understand health insurance policies in India.

You have access to multiple tools to query policy documents, extract information, compare policies, and calculate premiums.

When answering:
1. Use tools to find accurate information from policy documents
2. Explain complex insurance terms in simple English
3. Always cite your sources (policy name, section, page number)
4. Highlight critical warnings, exclusions, and waiting periods
5. Compare policies when asked
6. Be conversational but precise

If you need to use multiple tools to answer a question, do so. For example:
- First list available policies
- Then get details for specific ones
- Then extract and compare relevant sections

Always prioritize accuracy over speed."""

        # Call Claude with tools
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system_prompt,
            tools=self.tools,
            messages=self.conversation_history
        )
        
        # Process response and tool calls
        while response.stop_reason == "tool_use":
            # Extract tool uses
            tool_results = []
            assistant_content = []
            
            for block in response.content:
                if block.type == "tool_use":
                    # Execute tool
                    tool_result = self.process_tool_call(block.name, block.input)
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(tool_result)
                    })
                    
                    assistant_content.append(block)
                elif block.type == "text":
                    assistant_content.append(block)
            
            # Add assistant message to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_content
            })
            
            # Add tool results to history
            self.conversation_history.append({
                "role": "user",
                "content": tool_results
            })
            
            # Continue conversation
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=system_prompt,
                tools=self.tools,
                messages=self.conversation_history
            )
        
        # Extract final text response
        final_response = ""
        for block in response.content:
            if block.type == "text":
                final_response += block.text
        
        # Add final assistant message to history
        self.conversation_history.append({
            "role": "assistant",
            "content": final_response
        })
        
        return final_response
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
