from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class ServiceOnboardingFlow(Base):
    __tablename__ = "service_onboarding_flows"

    flow_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    service_type_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("service_types.service_type_id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ServiceOnboardingStep(Base):
    __tablename__ = "service_onboarding_steps"

    step_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    flow_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("service_onboarding_flows.flow_id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    title_fa: Mapped[str | None] = mapped_column(String(128))
    title_en: Mapped[str | None] = mapped_column(String(128))
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_required: Mapped[bool] = mapped_column(nullable=False)
    review_required: Mapped[bool] = mapped_column(nullable=False)
    schema_json: Mapped[dict | None] = mapped_column(JSONB)
    completion_rule_json: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ProviderServiceStepProgress(Base):
    __tablename__ = "provider_service_step_progress"
    __table_args__ = (
        UniqueConstraint("provider_service_id", "step_id", name="uq_provider_service_step"),
    )

    progress_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    provider_service_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("provider_services.provider_service_id", ondelete="CASCADE"), nullable=False
    )
    step_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("service_onboarding_steps.step_id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    data_json: Mapped[dict | None] = mapped_column(JSONB)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    review_note: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())
