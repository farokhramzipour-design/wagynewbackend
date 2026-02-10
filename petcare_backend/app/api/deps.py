from fastapi import Depends, Header, HTTPException

from app.core.database import AsyncSessionLocal


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


def require_admin(x_role: str | None = Header(default=None), x_user_id: str | None = Header(default=None)):
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="admin_required")
    return x_user_id
