from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TrackerCreate(BaseModel):
    name: str 
    tracker_type: str = 'gndu_result'  # Platform field: defaults to gndu_result (legacy)
    application_id: str  # Legacy field
    target_url: str  # New field for URL-based tracking
    search_term: str  # New field for what to search for


class TrackerResponse(BaseModel):
    id: int
    name: str
    tracker_type: str  # Platform field (legacy)
    application_id: str  # Legacy field
    target_url: str  # New URL field
    search_term: str  # New search term field
    last_status: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TrackerUpdate(BaseModel):
    name: Optional[str] = None
    tracker_type: Optional[str] = None  # Platform field (legacy)
    application_id: Optional[str] = None  # Legacy field
    target_url: Optional[str] = None  # New URL field
    search_term: Optional[str] = None  # New search term field
    last_status: Optional[str] = None
