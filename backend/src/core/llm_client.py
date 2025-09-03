"""LLM client for OpenRouter integration with streaming support."""
import json
import os
import logging
from typing import Dict, Any, Optional, Callable, List, Type
import aiohttp
from pydantic import BaseModel
from .state_logger import GREY, RESET
from .schema_utils import pydantic_to_openai_tool, extract_tool_call_args

logger = logging.getLogger(__name__)

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
        tool_choice: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
        use_streaming: bool = True
    ) -> Dict[str, Any]:
        """
        Process chat messages with OpenRouter LLM.
        
        Args:
            messages: List of chat messages
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream_callback: Function to call with each streaming chunk
            tools: List of tools available to the model (for non-streaming tool calls)
            tool_choice: How the model should choose tools ("auto", "required", or specific tool)
            response_format: OpenRouter structured output format (for streaming)
            use_streaming: Whether to use streaming (False for tool calls, True for structured outputs)
            
        Returns:
            Complete response from the LLM, including tool calls if any
        """
        logger.info(f"{GREY}Processing chat request - model: {model}, messages: {len(messages)}{RESET}")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/dextersjab/agentic-workbench-langgraph",
            "X-Title": "HelpHub IT Support Agent",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": use_streaming
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
            
        # Handle tool calls (non-streaming) vs structured outputs (streaming)
        if tools:
            payload["tools"] = tools
            if tool_choice:
                payload["tool_choice"] = tool_choice
        elif response_format:
            payload["response_format"] = response_format
        
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
                    
                    # Handle non-streaming responses (tool calls)
                    if not use_streaming:
                        response_data = await response.json()
                        return response_data.get("choices", [{}])[0].get("message", {})
                    
                    # Handle streaming responses (structured outputs)
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