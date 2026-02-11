import math

from fastapi import HTTPException
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime, time, timezone

from app.models.providers import Provider, ProviderHome, ProviderService, ProviderVerification
from app.models.services import ServiceType
from app.models.users import Address, Favorite, SearchHistory, UserVerification
from app.services.availability import is_provider_available


def _haversine_km(lat1, lng1, lat2, lng2):
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlng / 2) ** 2
    )
    return 2 * r * math.asin(math.sqrt(a))


def _rank_score(
    average_rating: float | None,
    response_rate_percent: int | None,
    total_completed_bookings: int | None,
    featured: bool | None,
    is_star_sitter: bool | None,
) -> float:
    rating_score = (average_rating or 0.0) / 5.0
    response_score = (response_rate_percent or 0) / 100.0
    bookings_score = math.log1p(total_completed_bookings or 0) / math.log1p(500)
    featured_score = 1.0 if featured else 0.0
    star_score = 1.0 if is_star_sitter else 0.0

    return (
        0.4 * rating_score
        + 0.2 * response_score
        + 0.2 * bookings_score
        + 0.1 * featured_score
        + 0.1 * star_score
    )


async def search_providers(session: AsyncSession, *, payload: dict):
    provider_query = select(Provider).where(Provider.status == "approved")

    # Service readiness
    service_exists = (
        select(ProviderService.provider_service_id)
        .join(ServiceType, ServiceType.service_type_id == ProviderService.service_type_id)
        .where(
            ProviderService.provider_id == Provider.provider_id,
            ProviderService.is_active.is_(True),
            ProviderService.status == "approved",
            ServiceType.is_active.is_(True),
        )
        .limit(1)
    )

    if payload.get("service_type_id"):
        service_exists = service_exists.where(
            ProviderService.service_type_id == payload["service_type_id"]
        )

    provider_query = provider_query.where(exists(service_exists))

    # Trust filters (optional)
    if payload.get("require_provider_verification_status"):
        pv_exists = (
            select(ProviderVerification.provider_verification_id)
            .where(
                ProviderVerification.provider_id == Provider.provider_id,
                ProviderVerification.status
                == payload["require_provider_verification_status"],
            )
            .limit(1)
        )
        provider_query = provider_query.where(exists(pv_exists))

    if payload.get("require_user_verification_status"):
        uv_exists = (
            select(UserVerification.verification_id)
            .where(
                UserVerification.user_id == Provider.user_id,
                UserVerification.status == payload["require_user_verification_status"],
            )
            .limit(1)
        )
        provider_query = provider_query.where(exists(uv_exists))

    # Location filters
    address_query = select(Address).where(Address.user_id == Provider.user_id)
    if payload.get("province_id"):
        address_query = address_query.where(Address.province_id == payload["province_id"])
    if payload.get("city_id"):
        address_query = address_query.where(Address.city_id == payload["city_id"])

    if payload.get("lat") is not None and payload.get("lng") is not None:
        address_query = address_query.where(Address.lat.is_not(None), Address.lng.is_not(None))
        address_query = address_query.where(Address.is_default.is_(True))

    provider_query = provider_query.join(Address, Address.user_id == Provider.user_id)
    provider_query = provider_query.where(
        Address.address_id.in_(address_query.with_only_columns(Address.address_id))
    )

    if any(
        key in payload
        for key in [
            "home_type",
            "has_fenced_yard",
            "smoking_household",
            "has_children",
            "has_pets",
            "work_from_home",
        ]
    ):
        provider_query = provider_query.join(
            ProviderHome, ProviderHome.provider_id == Provider.provider_id
        )
        if payload.get("home_type") is not None:
            provider_query = provider_query.where(ProviderHome.home_type == payload["home_type"])
        if payload.get("has_fenced_yard") is not None:
            provider_query = provider_query.where(
                ProviderHome.has_fenced_yard == payload["has_fenced_yard"]
            )
        if payload.get("smoking_household") is not None:
            provider_query = provider_query.where(
                ProviderHome.smoking_household == payload["smoking_household"]
            )
        if payload.get("has_children") is not None:
            provider_query = provider_query.where(
                ProviderHome.has_children == payload["has_children"]
            )
        if payload.get("has_pets") is not None:
            provider_query = provider_query.where(
                ProviderHome.has_pets == payload["has_pets"]
            )
        if payload.get("work_from_home") is not None:
            provider_query = provider_query.where(
                ProviderHome.work_from_home == payload["work_from_home"]
            )

    providers = (await session.scalars(provider_query)).all()

    results = []
    for provider in providers:
        provider_service_id = None
        provider_service = None
        if payload.get("service_type_id"):
            provider_service = await session.scalar(
                select(ProviderService).where(
                    ProviderService.provider_id == provider.provider_id,
                    ProviderService.service_type_id == payload["service_type_id"],
                    ProviderService.is_active.is_(True),
                    ProviderService.status == "approved",
                )
            )
            provider_service_id = (
                provider_service.provider_service_id if provider_service else None
            )

        distance_km = None
        if payload.get("lat") is not None and payload.get("lng") is not None:
            address = await session.scalar(
                select(Address).where(
                    Address.user_id == provider.user_id, Address.is_default.is_(True)
                )
            )
            if address and address.lat is not None and address.lng is not None:
                distance_km = _haversine_km(
                    payload["lat"], payload["lng"], address.lat, address.lng
                )
                radius_km = provider.service_radius_km
                if provider_service and provider_service.service_area_radius_km:
                    radius_km = provider_service.service_area_radius_km
                if radius_km is not None and distance_km > radius_km:
                    continue

        if payload.get("start_date") and payload.get("end_date") and payload.get(
            "service_type_id"
        ):
            start_date = payload["start_date"]
            end_date = payload["end_date"]
            start_dt = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
            end_dt = datetime.combine(end_date, time.max, tzinfo=timezone.utc)
            requested_units = payload.get("requested_units") or 1
            available = await is_provider_available(
                session,
                provider_id=provider.provider_id,
                service_type_id=payload["service_type_id"],
                start_datetime=start_dt,
                end_datetime=end_dt,
                requested_units=requested_units,
            )
            if not available:
                continue

        score = _rank_score(
            provider.average_rating,
            provider.response_rate_percent,
            provider.total_completed_bookings,
            provider.featured,
            provider.is_star_sitter,
        )

        provider_verified = await session.scalar(
            select(ProviderVerification.provider_verification_id)
            .where(
                ProviderVerification.provider_id == provider.provider_id,
                ProviderVerification.status == "passed",
            )
            .limit(1)
        )
        identity_verified = await session.scalar(
            select(UserVerification.verification_id)
            .where(
                UserVerification.user_id == provider.user_id,
                UserVerification.type == "identity",
                UserVerification.status == "passed",
            )
            .limit(1)
        )

        results.append(
            {
                "provider_id": provider.provider_id,
                "user_id": provider.user_id,
                "provider_service_id": provider_service_id,
                "distance_km": distance_km,
                "average_rating": float(provider.average_rating) if provider.average_rating is not None else None,
                "response_rate_percent": provider.response_rate_percent,
                "total_completed_bookings": provider.total_completed_bookings,
                "featured": provider.featured,
                "is_star_sitter": provider.is_star_sitter,
                "provider_verified": provider_verified is not None,
                "identity_verified": identity_verified is not None,
                "score": score,
            }
        )

    results.sort(key=lambda r: r["score"], reverse=True)

    # Write search history
    if payload.get("user_id") is not None:
        session.add(
            SearchHistory(
                user_id=payload.get("user_id"),
                province_id=payload.get("province_id"),
                city_id=payload.get("city_id"),
                lat=payload.get("lat"),
                lng=payload.get("lng"),
                service_type_id=payload.get("service_type_id"),
                start_date=payload.get("start_date"),
                end_date=payload.get("end_date"),
                filters_json=payload.get("filters_json"),
                results_count=len(results),
            )
        )
        await session.commit()

    return results


async def create_favorite(session: AsyncSession, *, user_id: int, provider_id: int) -> Favorite:
    existing = await session.scalar(
        select(Favorite).where(
            Favorite.user_id == user_id, Favorite.provider_id == provider_id
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="favorite_exists")

    favorite = Favorite(user_id=user_id, provider_id=provider_id)
    session.add(favorite)
    await session.commit()
    await session.refresh(favorite)
    return favorite


async def delete_favorite(session: AsyncSession, *, user_id: int, provider_id: int) -> None:
    favorite = await session.scalar(
        select(Favorite).where(
            Favorite.user_id == user_id, Favorite.provider_id == provider_id
        )
    )
    if not favorite:
        raise HTTPException(status_code=404, detail="favorite_not_found")
    await session.delete(favorite)
    await session.commit()


async def list_favorites(session: AsyncSession, *, user_id: int):
    return (
        await session.scalars(select(Favorite).where(Favorite.user_id == user_id))
    ).all()


async def list_search_history(session: AsyncSession, *, user_id: int):
    return (
        await session.scalars(select(SearchHistory).where(SearchHistory.user_id == user_id))
    ).all()
