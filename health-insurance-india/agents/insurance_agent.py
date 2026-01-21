"""Insurance agent using Anthropic's Agents SDK"""

from anthropic import Anthropic
from typing import List, Dict, Any, Optional
import json
from utils.config import Config
from utils.logger import get_logger
from agents.tools import TOOL_DEFINITIONS, TOOL_FUNCTIONS

logger = get_logger(__name__)


class InsuranceAgent:
    """Main agent for insurance policy queries using Agents SDK"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize insurance agent

        Args:
            api_key: Anthropic API key (uses Config if not provided)
        """
        self.client = Anthropic(api_key=api_key or Config.ANTHROPIC_API_KEY)
        self.model = Config.ANTHROPIC_MODEL
        self.tools = TOOL_DEFINITIONS
        self.conversation_history: List[Dict[str, Any]] = []
        self.system_prompt = self._create_system_prompt()

    def _create_system_prompt(self) -> str:
        """Create system prompt for the agent"""
        return """You are an expert Indian health insurance advisor helping users understand and compare health insurance policies.

Your capabilities:
- You have access to multiple Indian health insurance policies and their complete documents
- You can search across policy documents to find specific information
- You can extract and explain sections like exclusions, coverage, waiting periods
- You can compare multiple policies side-by-side
- You can calculate estimated premiums based on user details
- You understand Indian insurance terminology and regulations

When answering:
1. Always use tools to find accurate information from policy documents
2. Explain complex insurance terms in simple English
3. Always cite your sources (policy name, section, page number when available)
4. Highlight critical information like exclusions, waiting periods, and limitations
5. Be thorough but concise
6. When comparing policies, present information in a structured way
7. Always include disclaimers for premium calculations
8. If information is not available in documents, clearly state that

Important guidelines:
- Exclusions and waiting periods are CRITICAL - always highlight them clearly
- Sub-limits and co-payments significantly affect coverage - mention them
- Room rent limits can make a big difference - explain their impact
- Pre-existing disease coverage varies greatly - clarify waiting periods
- Network hospital availability is important for cashless treatment

Be conversational but precise. Your goal is to help users make informed decisions about health insurance."""

    def chat(self, user_message: str, reset_history: bool = False) -> str:
        """
        Chat with the insurance agent

        Args:
            user_message: User's message/question
            reset_history: Whether to reset conversation history

        Returns:
            Agent's response
        """
        if reset_history:
            self.reset_conversation()

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        try:
            # Call Claude with tools
            response = self.client.messages.create(
                model=self.model,
                max_tokens=Config.MAX_TOKENS,
                system=self.system_prompt,
                tools=self.tools,
                messages=self.conversation_history
            )

            # Process response and handle tool calls
            final_response = self._process_response(response)

            # Add final response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": final_response
            })

            return final_response

        except Exception as e:
            logger.error(f"Error in agent chat: {e}")
            return f"I encountered an error: {str(e)}. Please try again."

    def _process_response(self, response) -> str:
        """
        Process Claude's response and handle tool calls

        Args:
            response: Claude API response

        Returns:
            Final text response
        """
        # Keep calling tools until we get a final text response
        while response.stop_reason == "tool_use":
            # Extract tool uses and text
            tool_results = []
            assistant_content = []

            for block in response.content:
                if block.type == "tool_use":
                    # Execute tool
                    logger.info(f"Calling tool: {block.name}")
                    tool_result = self._execute_tool(block.name, block.input)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(tool_result)
                    })

                    assistant_content.append(block)

                elif block.type == "text":
                    assistant_content.append(block)

            # Add assistant message with tool uses to history
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
                model=self.model,
                max_tokens=Config.MAX_TOKENS,
                system=self.system_prompt,
                tools=self.tools,
                messages=self.conversation_history
            )

        # Extract final text response
        final_text = ""
        for block in response.content:
            if block.type == "text":
                final_text += block.text

        return final_text

    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call

        Args:
            tool_name: Name of the tool
            tool_input: Input parameters for the tool

        Returns:
            Tool execution result
        """
        if tool_name not in TOOL_FUNCTIONS:
            logger.error(f"Unknown tool: {tool_name}")
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            tool_function = TOOL_FUNCTIONS[tool_name]
            result = tool_function(**tool_input)
            return result

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": f"Tool execution failed: {str(e)}"}

    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history reset")

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation_history

    def load_conversation_history(self, history: List[Dict[str, Any]]):
        """Load conversation history"""
        self.conversation_history = history
        logger.info(f"Loaded conversation history with {len(history)} messages")


class StreamingInsuranceAgent(InsuranceAgent):
    """Insurance agent with streaming support"""

    def chat_stream(self, user_message: str, reset_history: bool = False):
        """
        Chat with streaming response

        Args:
            user_message: User's message
            reset_history: Whether to reset history

        Yields:
            Response chunks
        """
        if reset_history:
            self.reset_conversation()

        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        try:
            # Create streaming response
            with self.client.messages.stream(
                model=self.model,
                max_tokens=Config.MAX_TOKENS,
                system=self.system_prompt,
                tools=self.tools,
                messages=self.conversation_history
            ) as stream:
                full_response = ""

                for text in stream.text_stream:
                    full_response += text
                    yield text

                # Handle tool calls if needed
                # (Simplified - full implementation would handle tools in streaming)

                # Add to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": full_response
                })

        except Exception as e:
            logger.error(f"Error in streaming chat: {e}")
            yield f"Error: {str(e)}"
