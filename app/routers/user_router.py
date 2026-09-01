from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from pydantic import EmailStr
from app.api.dependencies import get_current_user, get_user_service
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User, Gender, UserRole
from app.schemas.user import UserCreate, UserLogin, UserResponse, RefreshTokenRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
        name: str = Form(..., min_length=1),
        username: str = Form(..., min_length=3, max_length=50),
        email: EmailStr = Form(...),
        password: str = Form(..., min_length=6),
        gender: Gender = Form(Gender.MALE),
        role: UserRole = Form(UserRole.STUDENT),
        avatar: UploadFile = File(None),
        user_service: UserService = Depends(get_user_service)
):
    username = username.strip().lower()
    email = str(email).strip().lower()
    existing_user = (await user_service.get_user_by_username_or_email(username, email))
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username hoặc email đã tồn tại")

    user_data = {
        "name": name,
        "username": username,
        "email": email,
        "password": password,
        "gender": gender,
        "role": role,
    }

    return await user_service.create_user(user_data=user_data, avatar=avatar)


@router.post("/login")
async def login(
        login_data: UserLogin,
        user_service: UserService = Depends(get_user_service)
):
    user = await user_service.login(username=login_data.username, password=login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản hoặc mật khẩu không đúng",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/profile", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/refresh")
async def refresh_token(
        request: RefreshTokenRequest,
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.refresh_access_token(request.refresh_token)