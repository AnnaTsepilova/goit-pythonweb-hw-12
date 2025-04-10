from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas import (
    UserRegister,
    UserCreate,
    UserRole,
    Token,
    TokenRefreshRequest,
    User,
    RequestEmail,
    ChangePassword,
)
from src.services.auth import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    get_email_from_token,
    create_email_token,
    change_user_password,
    Hash,
)
from src.services.users import UserService
from src.database.db import get_db
from src.redis.redis import get_redis
from src.services.email import send_email, send_reset_password_email

router = APIRouter(prefix="/auth", tags=["auth"])

# Реєстрація користувача
@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """Register users

    Args:
        user_data (UserRegister): User information for creating
        background_tasks (BackgroundTasks): Background tasks after registering user
        request (Request): HTTP Request
        db (Session, optional): db connection. Defaults to Depends(get_db).

    Raises:
        HTTPException: HTTP_409_CONFLICT

    Returns:
        Object of registered user
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким email вже існує",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким іменем вже існує",
        )
    user_data.password = Hash().get_password_hash(user_data.password)

    new_user = await user_service.create_user(
        UserCreate(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            role=UserRole.USER,
        )
    )
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return new_user

# Логін користувача
@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db), redis = Depends(get_redis),
):
    """User login endpoint

    Args:
        form_data (OAuth2PasswordRequestForm, optional): Form data with user credentials. Defaults to Depends().
        db (Session, optional): db connection. Defaults to Depends(get_db).

    Raises:
        HTTPException: HTTP_401_UNAUTHORIZED

    Returns:
        JSON with access token
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний логін або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Електронна адреса не підтверджена",
        )

    access_token = await create_access_token(data={"sub": user.username})
    refresh_token = await create_refresh_token(data={"sub": user.username})
    user.refresh_token = refresh_token
    redis.delete(str(user.username))
    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh-token", response_model=Token)
async def new_token(request: TokenRefreshRequest, db: Session = Depends(get_db)):
    user = await verify_refresh_token(request.refresh_token, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    new_access_token = await create_access_token(data={"sub": user.username})
    return {
        "access_token": new_access_token,
        "refresh_token": request.refresh_token,
        "token_type": "bearer",
    }

@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """Endpoint for registration confirmation with token from email

    Args:
        token (str): Confiramtion token from email
        db (Session, optional): db connection. Defaults to Depends(get_db).

    Raises:
        HTTPException: HTTP_400_BAD_REQUEST

    Returns:
        Confirmation result message
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    await user_service.confirmed_email(email)
    return {"message": "Електронну пошту підтверджено"}

@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """Endpoint for email confirmation

    Args:
        body (RequestEmail): Form data with user email
        background_tasks (BackgroundTasks): BackgroundTasks handler
        request (Request): _description_
        db (Session, optional): db connection. Defaults to Depends(get_db).

    Returns:
        JSON result for email confirmaton
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Електронна адреса не існує",
        )

    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Перевірте свою електронну пошту для підтвердження"}

@router.post("/reset-password")
async def reset_password_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """Endpoint for reset password

    Args:
        body (RequestEmail): Form data with user email
        background_tasks (BackgroundTasks): BackgroundTasks handler
        request (Request): _description_
        db (Session, optional): db connection. Defaults to Depends(get_db).

    Returns:
        JSON result for password email
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    reset_token = create_email_token({"sub": user.email, "token_type": "reset"})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Електронна адреса не існує",
        )

    if user:
        background_tasks.add_task(
            send_reset_password_email, user.email, user.username, request.base_url, reset_token
        )
        user.password_reset_token = reset_token
        await db.commit()
    return {"message": "Перевірте свою електронну пошту для підтвердження"}

@router.post("/change-password")
async def change_password(
    body: ChangePassword,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """Change password with token from email

    Args:
        body (ChangePassword): Data for password change
        background_tasks (BackgroundTasks): BackgroundTasks handler
        request (Request): _description_
        db (Session, optional): db connection. Defaults to Depends(get_db).

    Returns:
        JSON result for password email
    """

    await change_user_password(change_password=body, db=db)

    return {"message": "Пароль змінено"}
