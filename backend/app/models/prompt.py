from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    raw_text = Column(Text, nullable=False)
    parsed_structure = Column(JSON) # Stores extracted rooms, constraints, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="prompts")
    layouts = relationship("Layout", back_populates="prompt", cascade="all, delete-orphan")
