from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class Booking(Base):
    __tablename__ = "bookings"

    booking_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    booking_reference: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    owner_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    provider_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("providers.provider_id", ondelete="CASCADE"), nullable=False
    )
    service_type_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("service_types.service_type_id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    pets: Mapped[list["BookingPet"]] = relationship(back_populates="booking")
    pricing: Mapped["BookingPricing"] = relationship(
        back_populates="booking", uselist=False
    )
    events: Mapped[list["BookingEvent"]] = relationship(back_populates="booking")


class BookingPet(Base):
    __tablename__ = "booking_pets"
    __table_args__ = (
        UniqueConstraint("booking_id", "pet_id", name="uq_booking_pets"),
    )

    booking_pet_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    booking_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bookings.booking_id", ondelete="CASCADE"), nullable=False
    )
    pet_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("pets.pet_id", ondelete="RESTRICT"), nullable=False
    )
    per_pet_notes: Mapped[str | None] = mapped_column(String(1000))

    booking: Mapped["Booking"] = relationship(back_populates="pets")


class BookingPricing(Base):
    __tablename__ = "booking_pricing"

    booking_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bookings.booking_id", ondelete="CASCADE"), primary_key=True
    )
    currency_code: Mapped[str] = mapped_column(
        String(3), ForeignKey("currencies.currency_code", ondelete="RESTRICT"), nullable=False
    )
    subtotal_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    owner_fee_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    provider_fee_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    total_charge_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    provider_payout_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    breakdown_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    booking: Mapped["Booking"] = relationship(back_populates="pricing")


class BookingEvent(Base):
    __tablename__ = "booking_events"

    event_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    booking_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bookings.booking_id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    actor_type: Mapped[str] = mapped_column(String(32), nullable=False)
    actor_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.user_id", ondelete="SET NULL")
    )
    payload_json: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    booking: Mapped["Booking"] = relationship(back_populates="events")


class BookingCancellation(Base):
    __tablename__ = "booking_cancellations"

    cancellation_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    booking_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bookings.booking_id", ondelete="CASCADE"), nullable=False
    )
    cancelled_by: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(500))
    policy_snapshot_json: Mapped[dict | None] = mapped_column(JSONB)
    refund_minor: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class MeetGreet(Base):
    __tablename__ = "meet_greets"

    meet_greet_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    owner_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    provider_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("providers.provider_id", ondelete="CASCADE"), nullable=False
    )
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    location_text: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
