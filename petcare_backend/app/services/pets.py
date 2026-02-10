from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pets import Pet, PetVaccination


async def list_pets(session: AsyncSession, *, owner_user_id: int) -> list[Pet]:
    return (
        await session.scalars(select(Pet).where(Pet.owner_user_id == owner_user_id))
    ).all()


async def create_pet(session: AsyncSession, *, payload: dict) -> Pet:
    pet = Pet(**payload)
    session.add(pet)
    await session.commit()
    await session.refresh(pet)
    return pet


async def update_pet(session: AsyncSession, *, pet_id: int, payload: dict) -> Pet:
    pet = await session.get(Pet, pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="pet_not_found")
    for field, value in payload.items():
        setattr(pet, field, value)
    await session.commit()
    await session.refresh(pet)
    return pet


async def list_vaccinations(session: AsyncSession, *, pet_id: int) -> list[PetVaccination]:
    return (
        await session.scalars(
            select(PetVaccination).where(PetVaccination.pet_id == pet_id)
        )
    ).all()


async def create_vaccination(session: AsyncSession, *, payload: dict) -> PetVaccination:
    vaccination = PetVaccination(**payload)
    session.add(vaccination)
    await session.commit()
    await session.refresh(vaccination)
    return vaccination
