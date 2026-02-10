from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import Address, User
from app.repositories.base import BaseRepository


class UsersRepository(BaseRepository):
    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_phone(self, phone_e164: str) -> User | None:
        return await self.session.scalar(select(User).where(User.phone_e164 == phone_e164))

    async def update_status(self, user_id: int, status: str) -> User:
        user = await self.session.get(User, user_id)
        if not user:
            raise ValueError("user_not_found")
        user.status = status
        await self.session.flush()
        return user


class AddressesRepository(BaseRepository):
    async def list_for_user(self, user_id: int) -> list[Address]:
        return (
            await self.session.scalars(select(Address).where(Address.user_id == user_id))
        ).all()

    async def create_for_user(self, user_id: int, payload: dict) -> Address:
        address = Address(user_id=user_id, **payload)
        self.session.add(address)
        await self.session.flush()
        return address

    async def update(self, address_id: int, payload: dict) -> Address:
        address = await self.session.get(Address, address_id)
        if not address:
            raise ValueError("address_not_found")
        for field, value in payload.items():
            setattr(address, field, value)
        await self.session.flush()
        return address

    async def delete(self, address_id: int) -> None:
        address = await self.session.get(Address, address_id)
        if not address:
            raise ValueError("address_not_found")
        await self.session.delete(address)
