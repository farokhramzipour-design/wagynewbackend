from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.search import FavoriteCreate, SearchHistoryOut, SearchProvidersRequest
from app.services.search import (
    create_favorite,
    delete_favorite,
    list_favorites,
    list_search_history,
    search_providers,
)

router = APIRouter(tags=["search"])


@router.post("/search/providers")
async def search_providers_endpoint(
    payload: SearchProvidersRequest, db: AsyncSession = Depends(get_db)
):
    return await search_providers(db, payload=payload.model_dump())


@router.get("/search/history", response_model=list[SearchHistoryOut])
async def search_history(user_id: int, db: AsyncSession = Depends(get_db)):
    history = await list_search_history(db, user_id=user_id)
    return [SearchHistoryOut.model_validate(h, from_attributes=True) for h in history]


@router.post("/favorites")
async def add_favorite(payload: FavoriteCreate, db: AsyncSession = Depends(get_db)):
    favorite = await create_favorite(
        db, user_id=payload.user_id, provider_id=payload.provider_id
    )
    return {"favorite_id": favorite.favorite_id}


@router.delete("/favorites")
async def remove_favorite(user_id: int, provider_id: int, db: AsyncSession = Depends(get_db)):
    await delete_favorite(db, user_id=user_id, provider_id=provider_id)
    return {"deleted": True}


@router.get("/favorites")
async def list_favorites_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    favorites = await list_favorites(db, user_id=user_id)
    return favorites
