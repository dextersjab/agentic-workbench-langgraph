"""LLM client for OpenRouter integration with streaming support."""
import json
import os
import logging
from typing import Dict, Any, Optional, Callable, List
import aiohttp

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
        model: str = "openai/gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Process chat messages with OpenRouter LLM.
        
        Args:
            messages: List of chat messages
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream_callback: Function to call with each streaming chunk
            
        Returns:
            Complete response from the LLM
        """
        logger.info(f"Processing chat request - model: {model}, messages: {len(messages)}")
        
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
        
        accumulated_content = ""
        
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
                                    
                                    if content := delta.get("content"):
                                        accumulated_content += content
                                        if stream_callback:
                                            stream_callback(content)
                                            
                                except json.JSONDecodeError:
                                    logger.warning(f"Failed to decode JSON: {data}")
                                    continue
                                except Exception as e:
                                    logger.error(f"Error processing chunk: {e}")
                                    continue
                    
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise
        
        return {
            "role": "assistant",
            "content": accumulated_content
        }


# Create a singleton instance
client = OpenRouterClient()