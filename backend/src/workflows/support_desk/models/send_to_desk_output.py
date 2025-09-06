"""
Pydantic model for send_to_desk node output.
"""

from pydantic import BaseModel, Field
from typing import Dict


class SendToDeskOutput(BaseModel):
    """
    Structured output from the send_to_desk node.

    This model defines the final ticket creation and response.
    """

    ticket_id: str = Field(description="Generated unique ticket identifier")

    ticket_status: str = Field(
        default="created", description="Initial status of the created ticket"
    )

    assigned_team: str = Field(description="Team that will handle the ticket")

    sla_commitment: str = Field(
        description="Service level agreement for resolution time"
    )

    next_steps: str = Field(description="What happens next in the process")

    contact_information: Dict[str, str] = Field(
        default_factory=dict, description="How the user can follow up or get updates"
    )

    response: str = Field(
        description="Complete final response to the user with all ticket details"
    )
