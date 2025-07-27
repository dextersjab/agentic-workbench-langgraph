"""LLM client for OpenRouter integration with streaming support."""
import json
import os
import logging
from typing import Dict, Any, Optional, Callable, List, Type
import aiohttp
from pydantic import BaseModel
from src.workflows.support_desk.utils.state_logger import GREY, RESET

logger = logging.getLogger(__name__)

def pydantic_to_openai_tool(model_class: Type[BaseModel], tool_name: str) -> Dict[str, Any]:
    """
    Convert a Pydantic model to OpenAI tool format.
    
    Args:
        model_class: Pydantic model class
        tool_name: Name for the tool
        
    Returns:
        OpenAI tool specification
    """
    return {
        "type": "function",
        "function": {
            "name": tool_name,
            "description": model_class.__doc__ or f"Use this tool to provide {tool_name} output",
            "parameters": model_class.model_json_schema()
        }
    }


def extract_tool_call_args(response: Dict[str, Any], expected_tool_name: str = None) -> Dict[str, Any]:
    """
    Safely extract and parse tool call arguments from LLM response.
    
    Args:
        response: LLM response containing tool calls
        expected_tool_name: Optional tool name to validate against
        
    Returns:
        Parsed tool call arguments as dict
        
    Raises:
        ValueError: If tool calls are missing, malformed, or arguments are invalid JSON
    """
    # Check if response exists
    if not response:
        raise ValueError("Response is None or empty")
    
    # Check if tool_calls exist
    tool_calls = response.get("tool_calls")
    if not tool_calls:
        raise ValueError("No tool_calls found in response")
    
    if not isinstance(tool_calls, list) or len(tool_calls) == 0:
        raise ValueError("tool_calls is not a non-empty list")
    
    # Get first tool call
    tool_call = tool_calls[0]
    if not isinstance(tool_call, dict):
        raise ValueError("tool_call is not a dictionary")
    
    # Check function exists
    function = tool_call.get("function")
    if not function:
        raise ValueError("tool_call missing 'function' key")
    
    if not isinstance(function, dict):
        raise ValueError("tool_call 'function' is not a dictionary")
    
    # Validate tool name if expected
    if expected_tool_name:
        actual_name = function.get("name", "")
        if actual_name != expected_tool_name:
            raise ValueError(f"Expected tool '{expected_tool_name}' but got '{actual_name}'")
    
    # Get arguments
    args_json = function.get("arguments")
    if args_json is None:
        raise ValueError("tool_call function missing 'arguments' key")
    
    if not isinstance(args_json, str):
        raise ValueError("tool_call arguments is not a string")
    
    # Parse JSON arguments
    try:
        args_dict = json.loads(args_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"tool_call arguments contain invalid JSON: {e}")
    
    if not isinstance(args_dict, dict):
        raise ValueError("tool_call arguments JSON is not an object/dictionary")
    
    return args_dict


class OpenRouterClient:
    """Client for interacting with OpenRouter API with streaming support."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the client with API key."""
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")
        
        self.base_url = "https://openrouter.ai/api/v1"
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "openai/gpt-4.1",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream_callback: Optional[Callable[[str], None]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process chat messages with OpenRouter LLM.
        
        Args:
            messages: List of chat messages
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream_callback: Function to call with each streaming chunk
            tools: List of tools available to the model
            tool_choice: How the model should choose tools ("auto", "required", or specific tool)
            
        Returns:
            Complete response from the LLM, including tool calls if any
        """
        logger.info(f"{GREY}Processing chat request - model: {model}, messages: {len(messages)}{RESET}")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/dextersjab/agentic-course-case-study-0",
            "X-Title": "HelpHub IT Support Agent",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
            
        if tools:
            payload["tools"] = tools
            if tool_choice:
                payload["tool_choice"] = tool_choice
        
        accumulated_content = ""
        tool_calls = []
        current_tool_call = None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error: {response.status} - {error_text}")
                        raise Exception(f"OpenRouter API error: {response.status}")
                    
                    buffer = ""
                    async for chunk in response.content:
                        if not chunk:
                            continue
                        
                        chunk_str = chunk.decode('utf-8')
                        buffer += chunk_str
                        
                        # Process complete lines
                        while '\n' in buffer:
                            line_end = buffer.find('\n')
                            line = buffer[:line_end].strip()
                            buffer = buffer[line_end + 1:]
                            
                            if not line or line.startswith(':'):
                                continue
                            
                            if line.startswith('data: '):
                                data = line[6:]
                                if data == '[DONE]':
                                    break
                                
                                try:
                                    data_obj = json.loads(data)
                                    delta = data_obj.get("choices", [{}])[0].get("delta", {})
                                    
                                    # Handle regular content
                                    if content := delta.get("content"):
                                        accumulated_content += content
                                        if stream_callback:
                                            stream_callback(content)
                                    
                                    # Handle tool calls
                                    if tool_calls_delta := delta.get("tool_calls"):
                                        for tool_call_delta in tool_calls_delta:
                                            index = tool_call_delta.get("index", 0)
                                            
                                            # Ensure we have enough tool calls in our list
                                            while len(tool_calls) <= index:
                                                tool_calls.append({
                                                    "id": "",
                                                    "type": "function",
                                                    "function": {"name": "", "arguments": ""}
                                                })
                                            
                                            # Update the tool call at this index
                                            if "id" in tool_call_delta:
                                                tool_calls[index]["id"] = tool_call_delta["id"]
                                            
                                            if "function" in tool_call_delta:
                                                func_delta = tool_call_delta["function"]
                                                if "name" in func_delta:
                                                    tool_calls[index]["function"]["name"] += func_delta["name"]
                                                if "arguments" in func_delta:
                                                    tool_calls[index]["function"]["arguments"] += func_delta["arguments"]
                                            
                                except json.JSONDecodeError:
                                    logger.warning(f"Failed to decode JSON: {data}")
                                    continue
                                except Exception as e:
                                    logger.error(f"Error processing chunk: {e}")
                                    continue
                    
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise
        
        response = {
            "role": "assistant",
            "content": accumulated_content
        }
        
        # Add tool calls if any were made
        if tool_calls:
            response["tool_calls"] = tool_calls
            
        return response


# Create a singleton instance
client = OpenRouterClient()