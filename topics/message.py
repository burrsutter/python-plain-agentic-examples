from pydantic import BaseModel, Field

from typing import Optional
from datetime import datetime


class Message(BaseModel):
    id: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    comment: Optional[str] = None
    error: Optional[str] = None
