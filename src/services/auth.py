from datetime import datetime, timedelta, timezone, UTC
from typing import Optional, Literal

import pickle

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.database.db import get_db
from src.conf.config import settings
from src.services.users import UserService
from src.redis.redis import get_redis
from src.schemas import UserRole, User, ChangePassword

class Hash:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def create_token(
    data: dict, expires_delta: timedelta, token_type: Literal["access", "refresh"]
):
    to_encode = data.copy()
    now = datetime.now(UTC)
    expire = now + expires_delta
    to_encode.update({"exp": expire, "iat": now, "token_type": token_type})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = timedelta(seconds=expires_delta)
    else:
        expire = timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})

    encoded_jwt = create_token(
        to_encode, timedelta(seconds=settings.JWT_EXPIRATION_SECONDS), "access"
    )
    return encoded_jwt

async def create_refresh_token(data: dict, expires_delta: Optional[float] = None):
    if expires_delta:
        refresh_token = create_token(data, expires_delta, "refresh")
    else:
        refresh_token = create_token(
            data, timedelta(minutes=settings.REFRESH_TOKEN_EXPIRATION_MINUTES), "refresh"
        )
    return refresh_token

async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), redis = Depends (get_redis)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    user = redis.get(str(username))
    if user is None:
        user_service = UserService(db)
        user = await user_service.get_user_by_username(username)
        if user is None:
            raise credentials_exception

        redis.set(str(username), pickle.dumps(user))
        redis.expire(str(username), 3600)
    else:
        user = pickle.loads(user)

    # user_service = UserService(db)
    # user = await user_service.get_user_by_username(username)
    # if user is None:
    #     raise credentials_exception
    return user

def get_current_moderator_user(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостатньо прав доступу")
    return current_user

def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостатньо прав доступу")
    return current_user

async def verify_refresh_token(refresh_token: str, db: Session):
    try:
        payload = jwt.decode(
            refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        token_type: str = payload["token_type"]
        if username is None or token_type != "refresh":
            return None
        user_service = UserService(db)
        user = await user_service.get_user_by_refresh_token(username, refresh_token)
        return user
    except JWTError:
        return None

async def change_user_password(change_password: ChangePassword, db: Session):
    try:
        payload = jwt.decode(
            change_password.reset_password_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        print(f"change_password - {payload}")
        username = payload["sub"]
        token_type: str = payload["token_type"]
        if username is None or token_type != "reset":
            return None

        user_service = UserService(db)
        user = await user_service.get_user_by_password_token(change_password.reset_password_token)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Неправильний токен",
            )
        
        if change_password.new_password != change_password.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Паролі не співпадають",
            )

        if len(change_password.new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пароль повинен бути не менше 8 символів",
            )

        user.hashed_password = Hash().get_password_hash(change_password.new_password)
        user.password_reset_token = None
        await db.commit()

        return user

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Неправильний токен",
        )

def create_email_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=2)
    to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

async def get_email_from_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Неправильний токен для перевірки електронної пошти",
        )
