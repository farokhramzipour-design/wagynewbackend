from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.users import (
    AddressCreate,
    AddressOut,
    AddressUpdate,
    MeOut,
    MeUpdate,
    UserProfileOut,
    UserProfileUpdate,
)
from app.services.users import (
    create_address,
    delete_address,
    get_me,
    get_profile,
    list_addresses,
    update_address,
    update_me,
    upsert_profile,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=MeOut)
async def get_me_endpoint(user_id: int, db: AsyncSession = Depends(get_db)) -> MeOut:
    user = await get_me(db, user_id=user_id)
    return MeOut.model_validate(user, from_attributes=True)


@router.put("/me", response_model=MeOut)
async def update_me_endpoint(
    user_id: int, payload: MeUpdate, db: AsyncSession = Depends(get_db)
) -> MeOut:
    user = await update_me(db, user_id=user_id, payload=payload.model_dump(exclude_unset=True))
    return MeOut.model_validate(user, from_attributes=True)


@router.get("/me/profile", response_model=UserProfileOut | None)
async def get_profile_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    profile = await get_profile(db, user_id=user_id)
    return UserProfileOut.model_validate(profile, from_attributes=True) if profile else None


@router.put("/me/profile", response_model=UserProfileOut)
async def update_profile_endpoint(
    user_id: int, payload: UserProfileUpdate, db: AsyncSession = Depends(get_db)
) -> UserProfileOut:
    profile = await upsert_profile(
        db, user_id=user_id, payload=payload.model_dump(exclude_unset=True)
    )
    return UserProfileOut.model_validate(profile, from_attributes=True)


@router.get("/me/addresses", response_model=list[AddressOut])
async def list_addresses_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    addresses = await list_addresses(db, user_id=user_id)
    return [AddressOut.model_validate(a, from_attributes=True) for a in addresses]


@router.post("/me/addresses", response_model=AddressOut)
async def create_address_endpoint(
    user_id: int, payload: AddressCreate, db: AsyncSession = Depends(get_db)
) -> AddressOut:
    address = await create_address(db, user_id=user_id, payload=payload.model_dump())
    return AddressOut.model_validate(address, from_attributes=True)


@router.put("/me/addresses/{address_id}", response_model=AddressOut)
async def update_address_endpoint(
    address_id: int, user_id: int, payload: AddressUpdate, db: AsyncSession = Depends(get_db)
) -> AddressOut:
    address = await update_address(
        db, address_id=address_id, user_id=user_id, payload=payload.model_dump(exclude_unset=True)
    )
    return AddressOut.model_validate(address, from_attributes=True)


@router.delete("/me/addresses/{address_id}")
async def delete_address_endpoint(
    address_id: int, user_id: int, db: AsyncSession = Depends(get_db)
):
    await delete_address(db, address_id=address_id, user_id=user_id)
    return {"deleted": True}
