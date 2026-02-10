from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import Address, User, UserProfile


async def get_me(session: AsyncSession, *, user_id: int) -> User:
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user_not_found")
    return user


async def update_me(session: AsyncSession, *, user_id: int, payload: dict) -> User:
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user_not_found")

    if "email" in payload and payload["email"]:
        existing = await session.scalar(
            select(User).where(User.email == payload["email"], User.user_id != user_id)
        )
        if existing:
            raise HTTPException(status_code=409, detail="email_already_registered")

    for field, value in payload.items():
        setattr(user, field, value)
    await session.commit()
    await session.refresh(user)
    return user


async def get_profile(session: AsyncSession, *, user_id: int) -> UserProfile | None:
    return await session.get(UserProfile, user_id)


async def upsert_profile(
    session: AsyncSession, *, user_id: int, payload: dict
) -> UserProfile:
    profile = await session.get(UserProfile, user_id)
    if not profile:
        profile = UserProfile(user_id=user_id, **payload)
        session.add(profile)
    else:
        for field, value in payload.items():
            setattr(profile, field, value)
    await session.commit()
    await session.refresh(profile)
    return profile


async def list_addresses(session: AsyncSession, *, user_id: int) -> list[Address]:
    return (
        await session.scalars(select(Address).where(Address.user_id == user_id))
    ).all()


async def create_address(session: AsyncSession, *, user_id: int, payload: dict) -> Address:
    if payload.get("is_default"):
        await session.execute(
            Address.__table__.update()
            .where(Address.user_id == user_id)
            .values(is_default=False)
        )
    address = Address(user_id=user_id, **payload)
    session.add(address)
    await session.commit()
    await session.refresh(address)
    return address


async def update_address(
    session: AsyncSession, *, address_id: int, user_id: int, payload: dict
) -> Address:
    address = await session.get(Address, address_id)
    if not address or address.user_id != user_id:
        raise HTTPException(status_code=404, detail="address_not_found")

    for field, value in payload.items():
        setattr(address, field, value)
    if payload.get("is_default") is True:
        await session.execute(
            Address.__table__.update()
            .where(Address.user_id == user_id, Address.address_id != address_id)
            .values(is_default=False)
        )
    await session.commit()
    await session.refresh(address)
    return address


async def delete_address(session: AsyncSession, *, address_id: int, user_id: int) -> None:
    address = await session.get(Address, address_id)
    if not address or address.user_id != user_id:
        raise HTTPException(status_code=404, detail="address_not_found")
    await session.delete(address)
    await session.commit()
