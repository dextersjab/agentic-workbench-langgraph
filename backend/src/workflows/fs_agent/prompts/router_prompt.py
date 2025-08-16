"""
Prompts for router node in fs_agent workflow.
"""

ROUTER_PROMPT = """
# Objective

You are part of a file system agent workflow. Your task is to determine if the user's request will involve read-only operations or write operations.

# Task

Analyze the user's request and determine if it will involve:
1. Read-only operations (list files, read file contents, explore directory)
2. Write operations (write to files, delete files, create files)

# Decision Logic

Set is_read_only to True if the user:
- Wants to explore or browse files
- Wants to read file contents
- Wants to list directory contents
- Uses words like "show", "list", "read", "what's in", "explore"

Set is_read_only to False if the user:
- Wants to create new files
- Wants to write or modify files  
- Wants to delete files
- Uses words like "create", "write", "delete", "modify", "save"

Call the router_output tool with your decision.
"""