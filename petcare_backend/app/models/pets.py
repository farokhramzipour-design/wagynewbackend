from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class Pet(Base):
    __tablename__ = "pets"

    pet_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    owner_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    pet_type: Mapped[str] = mapped_column(String(32), nullable=False)
    size: Mapped[str] = mapped_column(String(32), nullable=False)
    gender: Mapped[str] = mapped_column(String(16), nullable=False)
    weight_kg: Mapped[float | None] = mapped_column(Float)
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    primary_photo_media_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("media.media_id")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )


class PetVaccination(Base):
    __tablename__ = "pet_vaccinations"

    vaccination_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    pet_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("pets.pet_id", ondelete="CASCADE"), nullable=False
    )
    vaccine_type: Mapped[str] = mapped_column(String(64), nullable=False)
    vaccination_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[date | None] = mapped_column(Date)
    document_media_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("media.media_id")
    )
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
