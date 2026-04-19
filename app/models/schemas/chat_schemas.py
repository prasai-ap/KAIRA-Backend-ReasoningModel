from typing import Optional
from pydantic import BaseModel


class SendMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None