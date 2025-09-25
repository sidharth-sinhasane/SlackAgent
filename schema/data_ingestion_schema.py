from pydantic import BaseModel

class DataIngestionSchema(BaseModel):
    channel_id: str
    user_id: str
    message: str

class IngestedDataSchema(BaseModel):
    channel_id: str
    user_id: str
    message: str
    embedding: list[float]