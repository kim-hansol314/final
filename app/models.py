from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey, DateTime, Text, DECIMAL, JSON
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    nickname = Column(String(100))
    business_type = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    admin = Column(Boolean, default=False)
    conversations = relationship("Conversation", back_populates="user")
    phq9_result = relationship("PHQ9Result", back_populates="user", uselist=False)

class Conversation(Base):
    __tablename__ = "conversation"
    conversation_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    conversation_type = Column(String(50))
    started_at = Column(DateTime, default=datetime.now)
    ended_at = Column(DateTime)
    is_visible = Column(Boolean, default=False)
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "message"
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversation.conversation_id"), nullable=False)
    sender_type = Column(String(50))
    agent_type = Column(String(50))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    conversation = relationship("Conversation", back_populates="messages")
    
class Report(Base):
    __tablename__ = "report"
    report_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversation.conversation_id"))
    report_type = Column(String(50))
    title = Column(String(100))
    content_data = Column(JSON)
    file_url = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

class PHQ9Result(Base):
    __tablename__ = "phq9_result"
    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True)
    score = Column(Integer, nullable=False)
    level = Column(String(50))
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    user = relationship("User", back_populates="phq9_result", uselist=False)
