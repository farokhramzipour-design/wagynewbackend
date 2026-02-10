from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class Provider(Base):
    __tablename__ = "providers"

    provider_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    headline: Mapped[str | None] = mapped_column(String(200))
    bio: Mapped[str | None] = mapped_column(String(2000))
    years_of_experience: Mapped[int | None] = mapped_column(Integer)
    service_radius_km: Mapped[int | None] = mapped_column(Integer)
    is_star_sitter: Mapped[bool | None] = mapped_column()
    response_rate_percent: Mapped[int | None] = mapped_column(Integer)
    avg_response_time_minutes: Mapped[int | None] = mapped_column(Integer)
    total_completed_bookings: Mapped[int | None] = mapped_column(Integer)
    repeat_clients_count: Mapped[int | None] = mapped_column(Integer)
    average_rating: Mapped[Numeric | None] = mapped_column(Numeric(3, 2))
    featured: Mapped[bool | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    home: Mapped["ProviderHome"] = relationship(back_populates="provider", uselist=False)
    verifications: Mapped[list["ProviderVerification"]] = relationship(
        back_populates="provider"
    )
    services: Mapped[list["ProviderService"]] = relationship(
        back_populates="provider"
    )


class ProviderHome(Base):
    __tablename__ = "provider_home"

    provider_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("providers.provider_id", ondelete="CASCADE"), primary_key=True
    )
    home_type: Mapped[str | None] = mapped_column(String(64))
    has_fenced_yard: Mapped[bool | None] = mapped_column()
    smoking_household: Mapped[bool | None] = mapped_column()
    has_children: Mapped[bool | None] = mapped_column()
    has_pets: Mapped[bool | None] = mapped_column()
    work_from_home: Mapped[bool | None] = mapped_column()

    provider: Mapped["Provider"] = relationship(back_populates="home")


class ProviderVerification(Base):
    __tablename__ = "provider_verifications"

    provider_verification_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    provider_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("providers.provider_id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    report_media_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("media.media_id")
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    provider: Mapped["Provider"] = relationship(back_populates="verifications")


class ProviderService(Base):
    __tablename__ = "provider_services"
    __table_args__ = (
        UniqueConstraint("provider_id", "service_type_id", name="uq_provider_service"),
    )

    provider_service_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    provider_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("providers.provider_id", ondelete="CASCADE"), nullable=False
    )
    service_type_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("service_types.service_type_id", ondelete="RESTRICT"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="draft")
    flow_version: Mapped[int | None] = mapped_column(Integer)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    review_note: Mapped[str | None] = mapped_column(String(500))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    service_area_radius_km: Mapped[int | None] = mapped_column(Integer)
    max_pets: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    provider: Mapped["Provider"] = relationship(back_populates="services")
    service_type: Mapped["ServiceType"] = relationship()
    rates: Mapped[list["ProviderServiceRate"]] = relationship(
        back_populates="provider_service"
    )


class ProviderServiceRate(Base):
    __tablename__ = "provider_service_rates"

    rate_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    provider_service_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("provider_services.provider_service_id", ondelete="CASCADE"),
        nullable=False,
    )
    currency_code: Mapped[str] = mapped_column(
        String(3), ForeignKey("currencies.currency_code", ondelete="RESTRICT"), nullable=False
    )
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    base_amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    effective_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    provider_service: Mapped["ProviderService"] = relationship(back_populates="rates")
