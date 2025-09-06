"""
Shared state logging utility for all workflows.

Provides consistent, colored logging of state reads and writes across all nodes.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

START_GREEN = "\033[38;5;84m"  # Vibrant mint green for starting
END_RED = "\033[38;5;203m"  # Warm coral red for ending
GREY = "\033[38;5;240m"  # Subtle grey for infrastructure logs
RESET = "\033[0m"


def format_value_concisely(value: Any, max_str_len: int = 40) -> str:
    """
    Format a value concisely for logging display.

    Args:
        value: The value to format
        max_str_len: Maximum length for string values before truncation

    Returns:
        A concise string representation of the value
    """
    if value is None:
        return "None"
    elif isinstance(value, str):
        if len(value) > max_str_len:
            return f'"{value[:max_str_len]}..."'
        return f'"{value}"'
    elif isinstance(value, (list, tuple)):
        return f"[{len(value)} items]"
    elif isinstance(value, dict):
        return f"{{{len(value)} keys}}"
    elif isinstance(value, bool):
        return str(value)
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        return f"{type(value).__name__}(...)"


def get_nested_value(state: Dict[str, Any], path: str) -> Any:
    """
    Get a value from nested dictionary using dot notation.

    Args:
        state: The state dictionary
        path: Dot-separated path to the value (e.g., "action.planned_action")

    Returns:
        The value at the path or None if not found
    """
    parts = path.split(".")
    value = state
    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return None
    return value


def log_node_start(
    node_name: str, reads: List[str], state: Dict[str, Any] = None
) -> None:
    """
    Log node start with expected reads and their values.

    Args:
        node_name: Name of the node
        reads: List of state fields this node will read (supports dot notation)
        state: Optional current state to show values of read fields
    """
    if state is not None:
        reads_with_values = []
        for field in reads:
            # Support both dot notation and direct field access
            if "." in field:
                value = get_nested_value(state, field)
            else:
                value = state.get(field)

            if value is not None:
                concise_value = format_value_concisely(value)
                reads_with_values.append(f"{field}: {concise_value}")
            else:
                reads_with_values.append(f"{field}: <missing>")
        reads_str = ", ".join(reads_with_values) if reads_with_values else "none"
    else:
        reads_str = ", ".join(reads) if reads else "none"

    logger.info(f"{START_GREEN}{node_name.upper()} ← {{{reads_str}}}{RESET}")


def log_node_complete(
    node_name: str, state_before: Dict[str, Any], state_after: Dict[str, Any]
) -> None:
    """
    Log node completion with actual writes and their values.

    Args:
        node_name: Name of the node
        state_before: State before node execution
        state_after: State after node execution
    """
    writes = []

    # Check top-level changes
    for key in state_after.keys():
        if key not in state_before:
            # New key added
            value = state_after[key]
            concise_value = format_value_concisely(value)
            writes.append(f"{key}: {concise_value}")
        elif state_before[key] != state_after[key]:
            # Existing key modified
            value = state_after[key]

            # For nested dictionaries, try to show what specifically changed
            if isinstance(value, dict) and isinstance(state_before[key], dict):
                # Check nested changes
                for nested_key in value.keys():
                    if (
                        nested_key not in state_before[key]
                        or state_before[key][nested_key] != value[nested_key]
                    ):
                        nested_value = value[nested_key]
                        concise_value = format_value_concisely(nested_value)
                        writes.append(f"{key}.{nested_key}: {concise_value}")
            else:
                concise_value = format_value_concisely(value)
                writes.append(f"{key}: {concise_value}")

    writes_str = ", ".join(writes) if writes else "none"
    logger.info(f"{END_RED}{node_name.upper()} → {{{writes_str}}}{RESET}")


# Deprecated function for backward compatibility
def log_state_access(
    node_name: str,
    state_before: Dict[str, Any],
    state_after: Dict[str, Any],
    expected_reads: List[str] = None,
    expected_writes: List[str] = None,
) -> None:
    """
    DEPRECATED: Use log_node_start and log_node_complete instead.

    Log what state fields a node reads from and writes to.

    Args:
        node_name: Name of the node
        state_before: State before node execution
        state_after: State after node execution
        expected_reads: Optional list of expected read fields
        expected_writes: Optional list of expected write fields
    """
    # Determine what fields were read (accessed for logic)
    reads = expected_reads or []

    # Determine what fields were written (changed between before/after)
    writes = []
    for key in state_after.keys():
        if key not in state_before or state_before[key] != state_after[key]:
            writes.append(key)

    # Format the log message
    reads_str = ", ".join(reads) if reads else "none"
    writes_str = ", ".join(writes) if writes else "none"

    logger.info(
        f"{START_GREEN}{node_name.upper()}: reads=[{reads_str}] writes=[{writes_str}]{RESET}"
    )
