
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import Gender, UserRole


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    gender: Gender = Gender.MALE
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.STUDENT


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id : int
    name: str
    gender: Gender | None = None
    email: EmailStr
    username : str
    email : str
    role : UserRole | None
    is_active : bool
    avatar_url: str | None = None

    model_config = ConfigDict(from_attributes=True)

class GoogleLoginRequest(BaseModel):
    token: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str
