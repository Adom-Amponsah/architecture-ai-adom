from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from pgvector.sqlalchemy import Vector
from app.database import Base

class LayoutStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Layout(Base):
    __tablename__ = "layouts"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
    
    # Graph representation (nodes/edges)
    constraint_graph = Column(JSON)
    
    # Vector embeddings for semantic search/matching (e.g. 1536 dims for OpenAI or 768 for generic BERT)
    # Using 256 as per spec "256-dim graph embedding"
    embedding = Column(Vector(256)) 
    
    # Resulting geometry
    floorplan_vector = Column(JSON) # GeoJSON or similar
    model_3d_path = Column(String) # Path to GLB/IFC in Object Storage
    
    status = Column(String, default=LayoutStatus.PENDING)
    error_message = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    prompt = relationship("Prompt", back_populates="layouts")
