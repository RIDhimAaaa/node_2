from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config import Base
import uuid


class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to trackers
    trackers = relationship("Tracker", back_populates="user")
    
    def __repr__(self):
        return f"<Profile(id={self.id}, email={self.email})>"


class Tracker(Base):
    __tablename__ = "trackers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'), nullable=False)
    name = Column(String, nullable=False)
    application_id = Column(String, nullable=False)  # Original field
    target_url = Column(String, nullable=False)  # Added by migration
    search_term = Column(String, nullable=False)  # Added by migration
    last_status = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to user
    user = relationship("Profile", back_populates="trackers")
    
    def __repr__(self):
        return f"<Tracker(id={self.id}, name={self.name}, url={self.target_url}, search={self.search_term})>"






