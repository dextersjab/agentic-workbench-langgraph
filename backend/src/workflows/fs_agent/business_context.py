"""Business context and domain knowledge for fs_agent workflow.

This module contains the business rules and domain expertise specific to
the fs_agent workflow. These constants define the behavior and limits
for the file system agent operations.
"""

SCHEMA_VERSION = "1.0"

# Maximum thinking iterations before forcing action (following ReAct pattern)
# This prevents infinite reflection loops while allowing thoughtful planning
MAX_THINKING_ITERATIONS = 2

# Default workspace path for file operations
DEFAULT_WORKSPACE_PATH = "/workspace"

# File operation limits for safety
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB max file size
MAX_FILES_PER_OPERATION = 50  # Max files to list/process at once

# Action repetition limits (prevent infinite loops)
MAX_ACTION_REPETITIONS = 2  # Max times same action can be repeated
