from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from dependencies.get_current_user import get_current_user
from services.notifications import send_whatsapp_notification
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from config import get_db
from models import Tracker
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test",
    tags=["testing"]
)

class TestNotificationRequest(BaseModel):
    phone_number: str
    message: str = "Test notification from Sarkari Scraper! 🚀"

class ChangeStatusRequest(BaseModel):
    tracker_id: int
    new_status: str

class UpdatePhoneRequest(BaseModel):
    phone_number: str

@router.post("/update-phone")
async def update_user_phone(
    request: UpdatePhoneRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update the user's phone number for WhatsApp notifications.
    Phone should be in E.164 format (e.g., +919876543210)
    """
    try:
        from models import Profile
        
        # Get user profile
        result = await db.execute(
            select(Profile).where(Profile.id == current_user["user_id"])
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Update phone number
        old_phone = profile.phone
        profile.phone = request.phone_number
        await db.commit()
        await db.refresh(profile)
        
        logger.info(f"📱 Phone updated for user {current_user['email']}: {old_phone} → {request.phone_number}")
        
        return {
            "success": True,
            "message": "Phone number updated successfully",
            "old_phone": old_phone,
            "new_phone": request.phone_number,
            "user_email": current_user["email"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to update phone: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update phone: {str(e)}")

@router.get("/user-info")
async def get_user_info(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user information including phone number.
    """
    try:
        from models import Profile
        
        # Get user profile
        result = await db.execute(
            select(Profile).where(Profile.id == current_user["user_id"])
        )
        profile = result.scalar_one_or_none()
        
        return {
            "user_id": current_user["user_id"],
            "email": current_user["email"],
            "phone": profile.phone if profile else None,
            "profile_exists": profile is not None
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get user info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get user info: {str(e)}")

@router.post("/change-status")
async def manually_change_status(
    request: ChangeStatusRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually change a tracker's status for testing purposes.
    This will trigger WhatsApp notifications if the status actually changes.
    """
    try:
        # Get the tracker
        result = await db.execute(
            select(Tracker).where(
                Tracker.id == request.tracker_id,
                Tracker.user_id == current_user["user_id"]
            )
        )
        tracker = result.scalar_one_or_none()
        
        if not tracker:
            raise HTTPException(status_code=404, detail="Tracker not found")
        
        # Store old status
        old_status = tracker.last_status
        
        # Update to new status
        tracker.last_status = request.new_status
        await db.commit()
        await db.refresh(tracker)
        
        logger.info(f"🔄 Status changed for tracker {tracker.name}: '{old_status}' → '{request.new_status}'")
        
        # Send WhatsApp notification if status changed and user has phone number
        notification_sent = False
        if old_status != request.new_status and current_user.get("phone"):
            success = send_whatsapp_notification(
                user_phone_number=current_user["phone"],
                tracker_name=tracker.name,
                new_status=request.new_status
            )
            notification_sent = success
        
        return {
            "success": True,
            "tracker_id": tracker.id,
            "tracker_name": tracker.name,
            "old_status": old_status,
            "new_status": request.new_status,
            "status_changed": old_status != request.new_status,
            "notification_sent": notification_sent,
            "message": f"Status updated from '{old_status}' to '{request.new_status}'"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to change status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to change status: {str(e)}")

@router.post("/whatsapp")
async def test_whatsapp_notification(
    request: TestNotificationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Test endpoint to send a WhatsApp notification.
    Use this to test your Twilio integration.
    """
    try:
        logger.info(f"🧪 Testing WhatsApp notification for user {current_user['email']}")
        
        success = send_whatsapp_notification(
            user_phone_number=request.phone_number,
            tracker_name="Test Tracker",
            new_status=request.message
        )
        
        if success:
            return {
                "success": True,
                "message": f"Test WhatsApp sent to {request.phone_number}",
                "phone": request.phone_number
            }
        else:
            return {
                "success": False,
                "message": "WhatsApp notification failed - check Twilio configuration",
                "phone": request.phone_number
            }
            
    except Exception as e:
        logger.error(f"❌ Test notification failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

@router.get("/scraper-demo")
async def test_scraper_demo():
    """
    Test endpoint to verify the scraper is working.
    This will run the demo scraper.
    """
    try:
        from routers.trackers.helpers import run_scrape_task
        
        logger.info("🧪 Testing scraper with demo roll number")
        result = run_scrape_task("gndu_result", "12345DEMO")
        
        return {
            "success": True,
            "tracker_type": "gndu_result",
            "roll_number": "12345DEMO",
            "result": result,
            "message": "Demo scraper test completed"
        }
        
    except Exception as e:
        logger.error(f"❌ Scraper test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scraper test failed: {str(e)}")
