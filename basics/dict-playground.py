from pydantic import BaseModel, Field

import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

class AnalyzedMessage(BaseModel):
    reason: str
    sentiment: Optional[str]
    company_name: Optional[str]
    customer_name: Optional[str]    
    email_address: Optional[str]
    phone: Optional[str]
    product_name: Optional[str]
    escalate: bool

class Message(BaseModel):
    id: str
    filename: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    structured: Optional[AnalyzedMessage] = None
    comment: Optional[str] = None
    error: list = Field(default_factory=list)

structured_message = AnalyzedMessage(
    reason="lost Invoice for TechGear Pro Laptop",
    sentiment="complaint",
    company_name=None,
    customer_name="Liu",
    email_address="liuwong@example.com",
    phone=None,
    product_name="TechGear Pro Laptop",
    escalate=False
)

complete_message = Message(
    id=str(uuid.uuid4()),
    filename="/Users/burr/ai-projects/ai-message-triage/data/intake/missing-invoice.txt",
    metadata={
        "original_path": "/Users/burr/ai-projects/ai-message-triage/data/intake/missing-invoice.txt",
        "size_bytes": 123,
        "created_timestamp": 1741480122.818238,
        "modified_timestamp": 1741480122.8180687,
    },
    timestamp=datetime(2025, 3, 9, 0, 28, 42, 841754),
    content="Hello, I purchased a TechGear Pro Laptop, but I can't find the invoice in my email. Sincerely, Liu liuwong@example.org",
    structured = structured_message,
    comment = None,
    error=[]
)

def log_dict_elements(d, prefix=""):
    """
    Recursively logs each key-value pair in a dictionary.
    
    :param d: Dictionary to log.
    :param prefix: String prefix for nested keys.
    """
    for key, value in d.items():
        full_key = f"{prefix}.{key}" if prefix else key
        
        if isinstance(value, dict):  # Recursively log nested dictionaries
            logging.info(f"{full_key}: [Nested Dictionary]")
            log_dict_elements(value, full_key)
        else:
            logging.info(f"{full_key}: {value}")


log_dict_elements(complete_message.model_dump())