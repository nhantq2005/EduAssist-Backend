from functools import wraps

from fastapi import HTTPException


def require_role(roles: list):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("current_user")
            if not user or user.role not in roles:
                raise HTTPException(status_code=403, detail="Forbidden")
            return await func(*args, **kwargs)

        return wrapper

    return decorator