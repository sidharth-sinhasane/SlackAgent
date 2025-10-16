from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(String(255), nullable=False)
    user_id = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    embedding = Column(Vector(1536))  # OpenAI embeddings are 1536 dimensions
    handled = Column(Boolean, default=False)
    message_metadata = Column('metadata', JSONB, default={})
    mention_bot = Column(Boolean, default=False)
    
    __table_args__ = (
        Index('messages_embedding_idx', 'embedding', postgresql_using='ivfflat', 
              postgresql_with={'lists': 100}, postgresql_ops={'embedding': 'vector_cosine_ops'}),
        Index('idx_messages_channel_id', 'channel_id'),
        Index('idx_messages_user_id', 'user_id'),
        Index('idx_messages_created_at', 'created_at'),
    )
