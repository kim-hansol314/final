from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChatRequest(BaseModel):
    user_id: int
    conversation_id: int
    user_input: str

class ChatResponse(BaseModel):
    answer: str

class ConversationCreate(BaseModel):
    user_id: int
    conversation_type: Optional[str] = "default"
