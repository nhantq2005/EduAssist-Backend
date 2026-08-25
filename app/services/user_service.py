import uuid
from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import GoogleLoginRequest


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: int):
        stm = select(User).where(User.id == user_id)
        result = await self.session.execute(stm)
        return result.scalar_one_or_none()

    async def create_user(self, user_data: dict):
        try:
            hashed_password = get_password_hash(
                user_data["password"]
            )

            new_user = User(
                name=user_data["name"],
                gender=user_data["gender"],
                username=user_data["username"].strip().lower(),
                email=str(user_data["email"]).strip().lower(),
                password=hashed_password,
                role=user_data.get("role", "STUDENT"),
            )

            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)
            return new_user

        except SQLAlchemyError:
            await self.session.rollback()
            raise

    async def get_user_by_username(self, username: str):
        stm = select(User).where(User.username == username)
        result = await self.session.execute(stm)
        return result.scalar_one_or_none()

    async def delete_user(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.commit()

    async def login(self, username: str, password: str):
        stm = select(User).where(User.username == username)
        result = await self.session.execute(stm)
        user = result.scalar_one_or_none()

        if user and verify_password(password, user.password):
            return user
        return None

    async def get_user_by_username_or_email(self, username: str, email: str):
        stmt = select(User).where(
            or_(
                User.username == username,
                User.email == email,
            )
        )

        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_user(self, user_id: int, update_data: dict):
        try:
            stm = select(User).where(User.id == user_id)
            result = await self.session.execute(stm)
            user = result.scalar_one_or_none()
            if not user:
                return None
            for key, value in update_data.items():
                setattr(user, key, value)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except Exception as e:
            await self.session.rollback()
            print(f"Lỗi: {e}")


    async def login_with_google(self, google_login_request: GoogleLoginRequest):
        try:
            id_info = id_token.verify_oauth2_token(
                id_token=google_login_request.token,
                request=google_requests.Request(),
                audience=settings.GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=10
            )

            email = id_info.get("email")
            name = id_info.get("name","")

            if not email:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không thể lấy email")

            existing_user = await self.get_user_by_username(email)

            if existing_user:
                user = existing_user
            else:
                random_password = str(uuid.uuid4())
                hashed_password = get_password_hash(random_password)
                username = email.split("@")[0]
                
                user_data = User(
                    name=name,
                    gender="MALE",
                    username=username,
                    email=email,
                    password=hashed_password,
                    role="STUDENT"
                )
                
                user = await self.create_user(user_data=user_data)

            access_token = create_access_token(data={"sub": user.username})
            return {"access_token": access_token, "token_type": "bearer"}
            
        except ValueError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token không hợp lệ")