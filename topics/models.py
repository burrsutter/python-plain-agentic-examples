from pydantic import BaseModel, Field

from typing import Optional
from datetime import datetime


class AnalyzedEmail(BaseModel):
    reason: str
    sentiment: Optional[str]
    customer_name: Optional[str]
    email_address: Optional[str]
    product_name: Optional[str]
    escalate: bool

class Message(BaseModel):
    id: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    comment: Optional[AnalyzedEmail] = None
    error: Optional[str] = None


