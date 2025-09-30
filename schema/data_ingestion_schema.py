from pydantic import BaseModel
from typing import Dict, Any, Optional

class DataIngestionSchema(BaseModel):
    channel_id: str
    user_id: str
    message: str
    handled: Optional[bool] = False
    metadata: Optional[Dict[str, Any]] = {}
    mention_bot: Optional[bool] = False

class IngestedDataSchema(BaseModel):
    channel_id: str
    user_id: str
    message: str
    embedding: list[float]
    handled: Optional[bool] = False
    metadata: Optional[Dict[str, Any]] = {}
    mention_bot: Optional[bool] = False