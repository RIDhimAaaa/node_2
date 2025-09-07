from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from dependencies.get_current_user import get_current_user
from config import get_db
from models import Tracker
from .schemas import TrackerCreate, TrackerResponse
from .helpers import run_scrape_task
from services.notifications import send_whatsapp_notification

router = APIRouter(
    prefix="/trackers",
    tags=["trackers"]
)


@router.post("", response_model=TrackerResponse)
async def add_tracker(
    tracker_data: TrackerCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a new tracker for the current user."""
    
    # Use universal scraper with the new URL-based approach
    initial_status = run_scrape_task(
        target_url=tracker_data.target_url, 
        selector_or_pattern=None,  # Can be expanded later
        search_term=tracker_data.search_term
    )
    
    if "Error" in initial_status:
        raise HTTPException(status_code=400, detail=f"Could not add tracker. Reason: {initial_status}")

    try:
        # Create new tracker
        new_tracker = Tracker(
            user_id=current_user["user_id"],
            name=tracker_data.name,
            application_id=tracker_data.search_term,  # Use search_term as application_id
            target_url=tracker_data.target_url,
            search_term=tracker_data.search_term,
            last_status=initial_status
        )
        
        db.add(new_tracker)
        await db.commit()
        await db.refresh(new_tracker)
        
        return new_tracker

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("", response_model=List[TrackerResponse])
async def get_trackers(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all trackers for the current user."""
    
    try:
        print(f"🔍 GET /trackers - User ID: {current_user['user_id']}")
        print(f"🔍 User data: {current_user}")
        
        result = await db.execute(
            select(Tracker).where(Tracker.user_id == current_user["user_id"])
        )
        trackers = result.scalars().all()
        
        print(f"🔍 Found {len(trackers)} trackers")
        for tracker in trackers:
            print(f"   - Tracker: {tracker.name}, URL: {tracker.target_url}")
        
        return trackers
        
    except Exception as e:
        print(f"❌ Error in get_trackers: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{tracker_id}", response_model=TrackerResponse)
async def get_tracker(
    tracker_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific tracker by ID."""
    
    try:
        result = await db.execute(
            select(Tracker).where(
                Tracker.id == tracker_id,
                Tracker.user_id == current_user["user_id"]
            )
        )
        tracker = result.scalar_one_or_none()
        
        if not tracker:
            raise HTTPException(status_code=404, detail="Tracker not found")
            
        return tracker
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/{tracker_id}/refresh", response_model=TrackerResponse)
async def refresh_tracker(
    tracker_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Refresh a tracker's status by scraping again."""
    
    try:
        result = await db.execute(
            select(Tracker).where(
                Tracker.id == tracker_id,
                Tracker.user_id == current_user["user_id"]
            )
        )
        tracker = result.scalar_one_or_none()
        
        if not tracker:
            raise HTTPException(status_code=404, detail="Tracker not found")
        
        # Store old status to compare
        old_status = tracker.last_status
        
        # Scrape new status using the universal scraper with new fields
        new_status = run_scrape_task(
            target_url=tracker.target_url,
            selector_or_pattern=None,  # Can be expanded later
            search_term=tracker.search_term
        )
        tracker.last_status = new_status
        
        await db.commit()
        await db.refresh(tracker)
        
        # Debug notification logic
        print(f"🔍 Notification Debug:")
        print(f"   Old Status: '{old_status}'")
        print(f"   New Status: '{new_status}'")
        print(f"   Status Changed: {old_status != new_status}")
        print(f"   User Phone: {current_user.get('phone', 'Not set')}")
        
        # Send WhatsApp notification if status changed
        if old_status != new_status:
            # HARDCODED FOR TESTING - Always send to your number
            hardcoded_phone = "+919877235405"
            print(f"📱 Sending WhatsApp notification to {hardcoded_phone}")
            success = send_whatsapp_notification(
                user_phone_number=hardcoded_phone,
                tracker_name=tracker.name,
                new_status=new_status
            )
            print(f"📨 Notification sent: {'✅ Success' if success else '❌ Failed'}")
        else:
            print("📝 Status unchanged - no notification needed")
        
        return tracker
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.delete("/{tracker_id}")
async def delete_tracker(
    tracker_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a tracker."""
    
    try:
        result = await db.execute(
            select(Tracker).where(
                Tracker.id == tracker_id,
                Tracker.user_id == current_user["user_id"]
            )
        )
        tracker = result.scalar_one_or_none()
        
        if not tracker:
            raise HTTPException(status_code=404, detail="Tracker not found")
        
        await db.delete(tracker)
        await db.commit()
        
        return {"message": "Tracker deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")