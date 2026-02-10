from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis import redis_client
from app.core.security import get_password_hash, verify_password
from app.models.users import User, UserProfile, UserVerification


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def _login_attempts_key(phone_e164: str) -> str:
    return f"auth:login_attempts:{phone_e164}"


def _login_lockout_key(phone_e164: str) -> str:
    return f"auth:login_lockout:{phone_e164}"


def _otp_cooldown_key(phone_e164: str) -> str:
    return f"auth:otp_cooldown:{phone_e164}"


async def register_user(session: AsyncSession, *, phone_e164: str, email: str | None,
                        password: str, profile: dict | None) -> User:
    if email:
        existing_email = await session.scalar(select(User).where(User.email == email))
        if existing_email:
            raise HTTPException(status_code=409, detail="email_already_registered")

    existing_phone = await session.scalar(select(User).where(User.phone_e164 == phone_e164))
    if existing_phone:
        raise HTTPException(status_code=409, detail="phone_already_registered")

    user = User(
        phone_e164=phone_e164,
        email=email,
        password_hash=get_password_hash(password),
        status="active",
    )
    session.add(user)
    await session.flush()

    if profile:
        session.add(
            UserProfile(
                user_id=user.user_id,
                first_name=profile.get("first_name"),
                last_name=profile.get("last_name"),
                date_of_birth=profile.get("date_of_birth"),
                avatar_media_id=profile.get("avatar_media_id"),
                bio=profile.get("bio"),
            )
        )

    await session.commit()
    await session.refresh(user)
    return user


async def login_user(session: AsyncSession, *, phone_e164: str, password: str) -> User:
    lockout = await redis_client.get(_login_lockout_key(phone_e164))
    if lockout:
        raise HTTPException(status_code=429, detail="login_locked")

    user = await session.scalar(select(User).where(User.phone_e164 == phone_e164))
    if not user:
        raise HTTPException(status_code=401, detail="invalid_credentials")

    if user.status != "active":
        raise HTTPException(status_code=403, detail="user_inactive")

    if not verify_password(password, user.password_hash):
        attempts = await redis_client.incr(_login_attempts_key(phone_e164))
        await redis_client.expire(
            _login_attempts_key(phone_e164), settings.login_attempt_window_seconds
        )
        if attempts >= settings.login_attempt_max:
            await redis_client.setex(
                _login_lockout_key(phone_e164), settings.login_lockout_seconds, "1"
            )
        raise HTTPException(status_code=401, detail="invalid_credentials")

    await redis_client.delete(_login_attempts_key(phone_e164))

    user.last_login_at = _utcnow()
    await session.commit()
    await session.refresh(user)
    return user


async def request_otp(
    session: AsyncSession, *, phone_e164: str, provider: str, reference_id: str | None
) -> UserVerification:
    cooldown_key = _otp_cooldown_key(phone_e164)
    if not await redis_client.set(cooldown_key, "1", ex=settings.otp_request_cooldown_seconds, nx=True):
        raise HTTPException(status_code=429, detail="otp_rate_limited")

    user = await session.scalar(select(User).where(User.phone_e164 == phone_e164))
    if not user:
        raise HTTPException(status_code=404, detail="user_not_found")

    verification = await session.scalar(
        select(UserVerification).where(
            UserVerification.user_id == user.user_id,
            UserVerification.type == "phone",
        )
    )

    if verification:
        verification.status = "pending"
        verification.provider = provider
        verification.reference_id = reference_id
        verification.verified_at = None
    else:
        verification = UserVerification(
            user_id=user.user_id,
            type="phone",
            status="pending",
            provider=provider,
            reference_id=reference_id,
        )
        session.add(verification)

    await session.commit()
    await session.refresh(verification)
    return verification


async def verify_otp(
    session: AsyncSession, *, phone_e164: str, provider: str, reference_id: str | None
) -> UserVerification:
    user = await session.scalar(select(User).where(User.phone_e164 == phone_e164))
    if not user:
        raise HTTPException(status_code=404, detail="user_not_found")

    verification = await session.scalar(
        select(UserVerification).where(
            UserVerification.user_id == user.user_id,
            UserVerification.type == "phone",
            UserVerification.provider == provider,
            UserVerification.reference_id == reference_id,
        )
    )
    if not verification:
        raise HTTPException(status_code=404, detail="verification_not_found")

    verification.status = "passed"
    verification.verified_at = _utcnow()
    await session.commit()
    await session.refresh(verification)
    return verification
