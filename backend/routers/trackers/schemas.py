from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TrackerCreate(BaseModel):
    name: str 
    target_url: str  # URL to track
    search_term: str  # What to search for on the URL


class TrackerResponse(BaseModel):
    id: int
    name: str
    application_id: str  # Original field
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
