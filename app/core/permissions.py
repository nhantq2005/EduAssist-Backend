from functools import wraps
from fastapi import HTTPException
from starlette import status


def require_role(roles: list):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("current_user")
            if not user or user.role not in roles:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
            return await func(*args, **kwargs)
        return wrapper
    return decorator