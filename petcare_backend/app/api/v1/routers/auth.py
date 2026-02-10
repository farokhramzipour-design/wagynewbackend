from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.auth import (
    LoginRequest,
    OtpRequest,
    OtpStatusOut,
    OtpVerifyRequest,
    RegisterRequest,
    UserOut,
)
from app.services.auth import login_user, register_user, request_otp, verify_otp

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> UserOut:
    user = await register_user(
        db,
        phone_e164=payload.phone_e164,
        email=str(payload.email) if payload.email else None,
        password=payload.password,
        profile=payload.profile.model_dump() if payload.profile else None,
    )
    return UserOut.model_validate(user, from_attributes=True)


@router.post("/login", response_model=UserOut)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> UserOut:
    user = await login_user(db, phone_e164=payload.phone_e164, password=payload.password)
    return UserOut.model_validate(user, from_attributes=True)


@router.post("/otp/request", response_model=OtpStatusOut)
async def otp_request(payload: OtpRequest, db: AsyncSession = Depends(get_db)) -> OtpStatusOut:
    verification = await request_otp(
        db,
        phone_e164=payload.phone_e164,
        provider=payload.provider,
        reference_id=payload.reference_id,
    )
    return OtpStatusOut(status=verification.status, verified_at=verification.verified_at)


@router.post("/otp/verify", response_model=OtpStatusOut)
async def otp_verify(payload: OtpVerifyRequest, db: AsyncSession = Depends(get_db)) -> OtpStatusOut:
    verification = await verify_otp(
        db,
        phone_e164=payload.phone_e164,
        provider=payload.provider,
        reference_id=payload.reference_id,
    )
    return OtpStatusOut(status=verification.status, verified_at=verification.verified_at)
