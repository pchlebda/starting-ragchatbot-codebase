import anthropic
from typing import List, Optional, Dict, Any

class AIGenerator:
    """Handles interactions with Anthropic's Claude API for generating responses"""
    
    # Static system prompt to avoid rebuilding on each call
    SYSTEM_PROMPT = """ You are an AI assistant specialized in course materials and educational content with access to a comprehensive search tool for course information.

Search Tool Usage:
- Use the search tool **only** for questions about specific course content or detailed educational materials
- You may perform up to 2 sequential searches per query when results from the first search are needed to formulate the second.
- Synthesize search results into accurate, fact-based responses
- If search yields no results, state this clearly without offering alternatives

Response Protocol:
- **General knowledge questions**: Answer using existing knowledge without searching
- **Course-specific questions**: Search first, then answer
- **No meta-commentary**:
 - Provide direct answers only — no reasoning process, search explanations, or question-type analysis
 - Do not mention "based on the search results"


All responses must be:
1. **Brief, Concise and focused** - Get to the point quickly
2. **Educational** - Maintain instructional value
3. **Clear** - Use accessible language
4. **Example-supported** - Include relevant examples when they aid understanding
Provide only the direct answer to what was asked.
"""
    
    def __init__(self, api_key: str, model: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        
        # Pre-build base API parameters
        self.base_params = {
            "model": self.model,
            "temperature": 0,
            "max_tokens": 800
        }
    
    def generate_response(self, query: str,
                         conversation_history: Optional[str] = None,
                         tools: Optional[List] = None,
                         tool_manager=None) -> str:
        """
        Generate AI response with optional tool usage and conversation context.
        
        Args:
            query: The user's question or request
            conversation_history: Previous messages for context
            tools: Available tools the AI can use
            tool_manager: Manager to execute tools
            
        Returns:
            Generated response as string
        """
        
        # Build system content efficiently - avoid string ops when possible
        system_content = (
            f"{self.SYSTEM_PROMPT}\n\nPrevious conversation:\n{conversation_history}"
            if conversation_history 
            else self.SYSTEM_PROMPT
        )
        
        # Prepare API call parameters efficiently
        api_params = {
            **self.base_params,
            "messages": [{"role": "user", "content": query}],
            "system": system_content
        }
        
        # Add tools if available
        if tools:
            api_params["tools"] = tools
            api_params["tool_choice"] = {"type": "auto"}
        
        # Get response from Claude
        response = self.client.messages.create(**api_params)
        
        # Handle tool execution if needed
        if response.stop_reason == "tool_use" and tool_manager:
            return self._run_agentic_loop(
                response, api_params["messages"], system_content, tools, tool_manager
            )

        # Return direct response
        return response.content[0].text

    def _run_agentic_loop(
        self,
        response,
        messages: List[Dict[str, Any]],
        system: str,
        tools: List,
        tool_manager,
        max_rounds: int = 2
    ):
        """
        Run an agentic loop allowing up to max_rounds of sequential tool use.

        Args:
            response: The first tool_use response from generate_response
            messages: Current message list (will be mutated)
            system: System prompt string
            tools: Tool definitions for intermediate calls
            tool_manager: Manager to execute tools
            max_rounds: Maximum number of tool-use rounds allowed

        Returns:
            Final response text after tool execution and synthesis
        """
        messages = messages.copy()

        for round_num in range(max_rounds):
            # Append the assistant's tool-use response
            messages.append({"role": "assistant", "content": response.content})

            # Execute all tool calls and collect results
            tool_results = []
            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_result = tool_manager.execute_tool(
                        content_block.name,
                        **content_block.input
                    )
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": content_block.id,
                        "content": tool_result
                    })

            messages.append({"role": "user", "content": tool_results})

            # If there are more rounds available, make an intermediate call with tools
            if round_num < max_rounds - 1:
                intermediate_response = self.client.messages.create(
                    **self.base_params,
                    messages=messages,
                    system=system,
                    tools=tools,
                    tool_choice={"type": "auto"}
                )
                if intermediate_response.stop_reason != "tool_use":
                    return intermediate_response.content[0].text
                response = intermediate_response

        # Final synthesis call — no tools
        final_response = self.client.messages.create(
            **self.base_params,
            messages=messages,
            system=system
        )
        return final_response.content[0].text