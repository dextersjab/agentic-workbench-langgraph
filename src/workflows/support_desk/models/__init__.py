"""
Pydantic models for structured outputs from workflow nodes.
"""
from .clarify_output import ClarifyOutput
from .classify_output import ClassifyOutput
from .triage_output import TriageOutput
from .gather_output import GatherOutput
from .gather_question_output import GatherQuestionOutput
from .send_to_desk_output import SendToDeskOutput

__all__ = [
    "ClarifyOutput",
    "ClassifyOutput", 
    "TriageOutput",
    "GatherOutput",
    "GatherQuestionOutput",
    "SendToDeskOutput"
]