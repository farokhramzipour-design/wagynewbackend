from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.pets import (
    PetCreate,
    PetOut,
    PetUpdate,
    PetVaccinationCreate,
    PetVaccinationOut,
)
from app.services.pets import create_pet, create_vaccination, list_pets, list_vaccinations, update_pet

router = APIRouter(prefix="/pets", tags=["pets"])


@router.get("/", response_model=list[PetOut])
async def list_pets_endpoint(owner_user_id: int, db: AsyncSession = Depends(get_db)):
    pets = await list_pets(db, owner_user_id=owner_user_id)
    return [PetOut.model_validate(p, from_attributes=True) for p in pets]


@router.post("/", response_model=PetOut)
async def create_pet_endpoint(payload: PetCreate, db: AsyncSession = Depends(get_db)) -> PetOut:
    pet = await create_pet(db, payload=payload.model_dump())
    return PetOut.model_validate(pet, from_attributes=True)


@router.put("/{pet_id}", response_model=PetOut)
async def update_pet_endpoint(
    pet_id: int, payload: PetUpdate, db: AsyncSession = Depends(get_db)
) -> PetOut:
    pet = await update_pet(db, pet_id=pet_id, payload=payload.model_dump(exclude_unset=True))
    return PetOut.model_validate(pet, from_attributes=True)


@router.get("/{pet_id}/vaccinations", response_model=list[PetVaccinationOut])
async def list_vaccinations_endpoint(pet_id: int, db: AsyncSession = Depends(get_db)):
    records = await list_vaccinations(db, pet_id=pet_id)
    return [PetVaccinationOut.model_validate(r, from_attributes=True) for r in records]


@router.post("/{pet_id}/vaccinations", response_model=PetVaccinationOut)
async def create_vaccination_endpoint(
    pet_id: int, payload: PetVaccinationCreate, db: AsyncSession = Depends(get_db)
) -> PetVaccinationOut:
    data = payload.model_dump()
    data["pet_id"] = pet_id
    record = await create_vaccination(db, payload=data)
    return PetVaccinationOut.model_validate(record, from_attributes=True)
