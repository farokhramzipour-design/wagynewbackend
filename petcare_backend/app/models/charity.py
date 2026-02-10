from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class CharityCase(Base):
    __tablename__ = "charity_cases"

    charity_case_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    creator_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(5000))
    province_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("provinces.province_id")
    )
    city_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("cities.city_id"))
    lat: Mapped[float | None] = mapped_column(Float)
    lng: Mapped[float | None] = mapped_column(Float)
    currency_code: Mapped[str] = mapped_column(
        String(3), ForeignKey("currencies.currency_code", ondelete="RESTRICT"), nullable=False
    )
    target_amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    collected_amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    incident_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reviewed_by_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.user_id", ondelete="SET NULL")
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )


class CharityCaseMedia(Base):
    __tablename__ = "charity_case_media"
    __table_args__ = (
        UniqueConstraint("charity_case_id", "media_id", name="uq_charity_case_media"),
    )

    charity_case_media_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    charity_case_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("charity_cases.charity_case_id", ondelete="CASCADE"),
        nullable=False,
    )
    media_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("media.media_id", ondelete="CASCADE"), nullable=False
    )
    sort_order: Mapped[int | None] = mapped_column(Integer)


class CharityDonation(Base):
    __tablename__ = "charity_donations"

    donation_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    charity_case_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("charity_cases.charity_case_id", ondelete="CASCADE"),
        nullable=False,
    )
    donor_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.user_id", ondelete="SET NULL")
    )
    payment_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("payments.payment_id", ondelete="SET NULL")
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    currency_code: Mapped[str] = mapped_column(
        String(3), ForeignKey("currencies.currency_code", ondelete="RESTRICT"), nullable=False
    )
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    donation_reference: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )


class CharityUpdate(Base):
    __tablename__ = "charity_updates"

    charity_update_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    charity_case_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("charity_cases.charity_case_id", ondelete="CASCADE"),
        nullable=False,
    )
    author_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.user_id", ondelete="SET NULL")
    )
    body: Mapped[str] = mapped_column(String(4000), nullable=False)
    spent_amount_minor: Mapped[int | None] = mapped_column(BigInteger)
    currency_code: Mapped[str | None] = mapped_column(
        String(3), ForeignKey("currencies.currency_code", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class CharityUpdateMedia(Base):
    __tablename__ = "charity_update_media"
    __table_args__ = (
        UniqueConstraint("charity_update_id", "media_id", name="uq_charity_update_media"),
    )

    charity_update_media_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    charity_update_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("charity_updates.charity_update_id", ondelete="CASCADE"),
        nullable=False,
    )
    media_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("media.media_id", ondelete="CASCADE"), nullable=False
    )
    sort_order: Mapped[int | None] = mapped_column(Integer)
