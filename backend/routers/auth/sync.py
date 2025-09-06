from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from dependencies.get_current_user import get_current_user
from config import get_db, supabase
from models import Profile
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/sync-profile")
async def sync_profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync/create user profile in database.
    This endpoint can be called to ensure a profile exists for the current user.
    """
    try:
        user_id = current_user["user_id"]
        email = current_user["email"]
        
        # Check if profile already exists
        result = await db.execute(select(Profile).where(Profile.id == user_id))
        existing_profile = result.scalar_one_or_none()
        
        if existing_profile:
            return {"message": "Profile already exists", "profile_id": str(user_id)}
        
        # Get additional user info from Supabase
        user_data = current_user.get("user")
        user_metadata = user_data.user_metadata if user_data else {}
        
        # Create new profile
        new_profile = Profile(
            id=user_id,
            email=email,
            first_name=user_metadata.get("first_name"),
            last_name=user_metadata.get("last_name"),
            avatar_url=user_metadata.get("avatar_url"),
            phone=user_metadata.get("phone"),
            is_active=True
        )
        
        db.add(new_profile)
        await db.commit()
        await db.refresh(new_profile)
        
        logger.info(f"Profile synced successfully for user {user_id}")
        return {"message": "Profile created successfully", "profile_id": str(user_id)}
        
    except Exception as e:
        logger.error(f"Error syncing profile: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to sync profile: {str(e)}")
