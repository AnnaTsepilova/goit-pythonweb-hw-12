from fastapi import APIRouter, Depends, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.database.db import get_db
from src.schemas import User
from src.services.auth import get_current_user
from src.conf.config import settings
from src.services.users import UserService
from src.services.upload_file import UploadFileService

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)

@router.get(
    "/me", response_model=User, description="No more than 10 requests per minute"
)
@limiter.limit("10/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """Get current logged user

    Args:
        request (Request): Unused
        user (User, optional): Current logged user. Defaults to Depends(get_current_user).

    Returns:
        Object of current logged in user
    """
    return user

@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add user's avatar

    Args:
        file (UploadFile, optional): Path to uploaded file. Defaults to File().
        user (User, optional): Current logged user. Defaults to Depends(get_current_user).
        db (AsyncSession, optional): db connection. Defaults to Depends(get_db).

    Returns:
        User object
    """
    avatar_url = UploadFileService(
        settings.CLOUDINARY_NAME, settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
