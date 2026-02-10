from datetime import date, datetime, time

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class ProviderAvailabilityRule(Base):
    __tablename__ = "provider_availability_rules"

    rule_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    provider_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("providers.provider_id", ondelete="CASCADE"), nullable=False
    )
    service_type_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("service_types.service_type_id", ondelete="SET NULL")
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False)


class ProviderAvailabilityOverride(Base):
    __tablename__ = "provider_availability_overrides"

    override_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    provider_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("providers.provider_id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    service_type_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("service_types.service_type_id", ondelete="SET NULL")
    )
    is_available: Mapped[bool] = mapped_column(nullable=False)
    capacity: Mapped[int | None] = mapped_column(Integer)
    note: Mapped[str | None] = mapped_column()


class ProviderTimeOff(Base):
    __tablename__ = "provider_time_off"

    time_off_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    provider_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("providers.provider_id", ondelete="CASCADE"), nullable=False
    )
    start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reason: Mapped[str | None] = mapped_column()
