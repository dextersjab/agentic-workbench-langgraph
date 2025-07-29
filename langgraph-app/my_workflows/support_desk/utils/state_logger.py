"""
State logging utility for Support Desk workflow.

Provides consistent, colored logging of state reads and writes across all nodes.
"""
import logging
from typing import Dict, Any, List, Set
from copy import deepcopy

from ..state import SupportDeskState

logger = logging.getLogger(__name__)

START_GREEN = "\033[38;5;84m"    # Vibrant mint green for starting
END_RED = "\033[38;5;203m"       # Warm coral red for ending
GREY = "\033[38;5;240m"          # Subtle grey for infrastructure logs
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


def log_state_access(node_name: str, state_before: SupportDeskState, state_after: SupportDeskState, 
                    expected_reads: List[str] = None, expected_writes: List[str] = None) -> None:
    """
    Log what state fields a node reads from and writes to with blue formatting.
    
    Args:
        node_name: Name of the node (e.g., "classify_issue", "triage_issue")
        state_before: State before node execution
        state_after: State after node execution
        expected_reads: Optional list of expected read fields for validation
        expected_writes: Optional list of expected write fields for validation
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
    
    logger.info(f"{START_GREEN}{node_name.upper()}: reads=[{reads_str}] writes=[{writes_str}]{RESET}")


def log_node_start(node_name: str, reads: list[str], state: SupportDeskState | None = None) -> None:
    """
    Log node start with expected reads and their values.
    
    Args:
        node_name: Name of the node
        reads: List of state fields this node will read
        state: Optional current state to show values of read fields
    """
    if state is not None:
        reads_with_values = []
        for field in reads:
            if field in state:
                value = state[field]
                concise_value = format_value_concisely(value)
                reads_with_values.append(f"{field}: {concise_value}")
            else:
                reads_with_values.append(f"{field}: <missing>")
        reads_str = ", ".join(reads_with_values) if reads_with_values else "none"
    else:
        reads_str = ", ".join(reads) if reads else "none"
    
    logger.info(f"{START_GREEN}{node_name.upper()} ← {{{reads_str}}}{RESET}")


def log_node_complete(node_name: str, state_before: SupportDeskState, state_after: SupportDeskState) -> None:
    """
    Log node completion with actual writes and their values.
    
    Args:
        node_name: Name of the node
        state_before: State before node execution
        state_after: State after node execution
    """
    writes = []
    for key in state_after.keys():
        if key not in state_before or state_before[key] != state_after[key]:
            value = state_after[key]
            concise_value = format_value_concisely(value)
            writes.append(f"{key}: {concise_value}")
    
    writes_str = ", ".join(writes) if writes else "none"
    logger.info(f"{END_RED}{node_name.upper()} → {{{writes_str}}}{RESET}")