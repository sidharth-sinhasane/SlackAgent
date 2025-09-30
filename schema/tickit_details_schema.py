from pydantic import BaseModel
from typing import Dict, Any, Optional

class TicketDetailsSchema(BaseModel):
    ticket_id: str
    ticket_title: str
    ticket_description: str
    ticket_status: str
    ticket_priority: str
    ticket_assignee: str
    should_create_ticket: bool