"""Schema conversion utilities for OpenRouter structured outputs."""

import json
from typing import Dict, Any, Type
from pydantic import BaseModel


def pydantic_to_json_schema(
    model_class: Type[BaseModel], schema_name: str
) -> Dict[str, Any]:
    """
    Convert a Pydantic model to OpenRouter's JSON Schema format for structured outputs.

    Args:
        model_class: Pydantic model class
        schema_name: Name for the schema

    Returns:
        OpenRouter response_format specification
    """
    # Get the JSON schema from Pydantic
    json_schema = model_class.model_json_schema()

    # Remove the title if it exists (OpenRouter prefers name)
    if "title" in json_schema:
        del json_schema["title"]

    # Ensure strict mode and no additional properties
    json_schema["additionalProperties"] = False

    # OpenRouter requires ALL properties to be in required array for structured outputs
    if "properties" in json_schema:
        json_schema["required"] = list(json_schema["properties"].keys())

    return {
        "type": "json_schema",
        "json_schema": {"name": schema_name, "strict": True, "schema": json_schema},
    }


def pydantic_to_openai_tool(
    model_class: Type[BaseModel], tool_name: str
) -> Dict[str, Any]:
    """
    Convert a Pydantic model to OpenAI tool format (for non-streaming tool calls).

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
            "description": model_class.__doc__
            or f"Use this tool to provide {tool_name} output",
            "parameters": model_class.model_json_schema(),
        },
    }


def extract_tool_call_args(
    response: Dict[str, Any], expected_tool_name: str = None
) -> Dict[str, Any]:
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
        raise ValueError("No tool calls found in response")

    if not isinstance(tool_calls, list) or len(tool_calls) == 0:
        raise ValueError("Tool calls is not a valid list or is empty")

    # Get the first tool call
    tool_call = tool_calls[0]

    # Validate tool call structure
    if not isinstance(tool_call, dict):
        raise ValueError("Tool call is not a dictionary")

    function = tool_call.get("function")
    if not function:
        raise ValueError("No function found in tool call")

    # Validate expected tool name if provided
    if expected_tool_name:
        actual_name = function.get("name")
        if actual_name != expected_tool_name:
            raise ValueError(
                f"Expected tool '{expected_tool_name}', got '{actual_name}'"
            )

    # Extract and parse arguments
    arguments_str = function.get("arguments")
    if not arguments_str:
        raise ValueError("No arguments found in function call")

    try:
        arguments = json.loads(arguments_str)
        if not isinstance(arguments, dict):
            raise ValueError("Arguments are not a valid dictionary")
        return arguments
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse arguments JSON: {e}")
