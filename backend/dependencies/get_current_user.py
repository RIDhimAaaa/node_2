from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import supabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from config import get_db
import jwt
import os
import logging
from typing import Dict, Any, List, Callable

logger = logging.getLogger(__name__)
security = HTTPBearer()

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get current user from JWT token using Supabase verification"""
    try:
        token = credentials.credentials
        logger.info(f"Received token: {token[:20]}...")  # Log first 20 chars for debugging
        
        # Use Supabase to verify the token
        try:
            # Set the auth token and get user
            supabase.auth.set_session(access_token=token, refresh_token="")
            user_response = supabase.auth.get_user(token)
            
            if user_response.user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: user not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            user = user_response.user
            user_id = user.id
            email = user.email
            user_metadata = user.user_metadata or {}
            role = user_metadata.get("role", "user")  # default to user

            logger.info(f"Supabase verified user: {user_id}, email: {email}, role: {role}")
            
        except Exception as supabase_error:
            logger.error(f"Supabase token verification failed: {supabase_error}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: Supabase verification failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Ensure profile exists in database (auto-create if missing)
        from models import Profile
        try:
            # Check if profile exists
            result = await db.execute(select(Profile).where(Profile.id == user_id))
            profile = result.scalar_one_or_none()
            
            if not profile:
                # Create profile automatically
                logger.info(f"Creating new profile for user {user_id}")
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
                logger.info(f"Profile created successfully for user {user_id}")
                
        except Exception as db_error:
            logger.error(f"Database error during profile check/creation: {db_error}")
            await db.rollback()
            # Don't fail auth if profile creation fails, just log it
            logger.warning(f"Continuing without profile creation for user {user_id}")

        # Create a user-like object with the verified information
        current_user = {
            "user_id": user_id,
            "email": email, 
            "role": role,
            "user": user  # Include the full Supabase user object
        }

        logger.info(f"User {user_id} authenticated via Supabase, role: {role}")
        
        # Set current user in request state for RBAC
        request.state.current_user = current_user
        
        return current_user
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )



