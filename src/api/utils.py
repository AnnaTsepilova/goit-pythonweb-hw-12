from fastapi import APIRouter, Depends, Header, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db
from src.redis.redis import get_redis

router = APIRouter(tags=["utils"])

@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db), redis = Depends (get_redis)):
    """Endpoint for health checks of application

    Args:
        db (AsyncSession, optional): _description_. Defaults to Depends(get_db).

    Raises:
        HTTPException: HTTP_500_INTERNAL_SERVER_ERROR

    Returns:
        Status of application
    """
    try:
        # Виконуємо асинхронний запит
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )

        # Виконуємо тест підключення до Redis
        redis.set(str("healthcheck"), "SomeData")
        redis.delete(str("healthcheck"))

        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )
    
@router.get("/headers")
async def read_headers(user_agent: str = Header(default=None)):
    """Test HTTP headers

    Args:
        user_agent (str, optional): Current user agent. Defaults to Header(default=None).

    Returns:
        List of HTTP headers
    """
    return {"User-Agent": user_agent}

@router.get("/all-headers")
async def read_all_headers(request: Request):
    """Get all HTTP headers

    Args:
        request (Request): _description_

    Returns:
        List of HTTP headers
    """
    return {"headers": dict(request.headers)}
