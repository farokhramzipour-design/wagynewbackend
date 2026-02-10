from sqlalchemy import select

from app.models.pets import Pet, PetVaccination
from app.repositories.base import BaseRepository


class PetsRepository(BaseRepository):
    async def list_for_owner(self, owner_user_id: int) -> list[Pet]:
        return (
            await self.session.scalars(select(Pet).where(Pet.owner_user_id == owner_user_id))
        ).all()

    async def create(self, payload: dict) -> Pet:
        pet = Pet(**payload)
        self.session.add(pet)
        await self.session.flush()
        return pet

    async def update(self, pet_id: int, payload: dict) -> Pet:
        pet = await self.session.get(Pet, pet_id)
        if not pet:
            raise ValueError("pet_not_found")
        for field, value in payload.items():
            setattr(pet, field, value)
        await self.session.flush()
        return pet


class PetVaccinationsRepository(BaseRepository):
    async def list_for_pet(self, pet_id: int) -> list[PetVaccination]:
        return (
            await self.session.scalars(
                select(PetVaccination).where(PetVaccination.pet_id == pet_id)
            )
        ).all()

    async def create(self, payload: dict) -> PetVaccination:
        vaccination = PetVaccination(**payload)
        self.session.add(vaccination)
        await self.session.flush()
        return vaccination
