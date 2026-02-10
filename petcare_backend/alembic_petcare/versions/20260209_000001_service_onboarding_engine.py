"""service onboarding engine

Revision ID: 20260209_000001
Revises: None
Create Date: 2026-02-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260209_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "service_onboarding_flows",
        sa.Column("flow_id", sa.BigInteger(), primary_key=True),
        sa.Column("service_type_id", sa.BigInteger(), sa.ForeignKey("service_types.service_type_id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "service_onboarding_steps",
        sa.Column("step_id", sa.BigInteger(), primary_key=True),
        sa.Column("flow_id", sa.BigInteger(), sa.ForeignKey("service_onboarding_flows.flow_id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("title_fa", sa.String(length=128)),
        sa.Column("title_en", sa.String(length=128)),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False),
        sa.Column("review_required", sa.Boolean(), nullable=False),
        sa.Column("schema_json", postgresql.JSONB()),
        sa.Column("completion_rule_json", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "provider_service_step_progress",
        sa.Column("progress_id", sa.BigInteger(), primary_key=True),
        sa.Column("provider_service_id", sa.BigInteger(), sa.ForeignKey("provider_services.provider_service_id", ondelete="CASCADE"), nullable=False),
        sa.Column("step_id", sa.BigInteger(), sa.ForeignKey("service_onboarding_steps.step_id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("data_json", postgresql.JSONB()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("review_note", sa.String(length=500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_unique_constraint(
        "uq_provider_service_step",
        "provider_service_step_progress",
        ["provider_service_id", "step_id"],
    )

    op.add_column("provider_services", sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"))
    op.add_column("provider_services", sa.Column("flow_version", sa.Integer()))
    op.add_column("provider_services", sa.Column("submitted_at", sa.DateTime(timezone=True)))
    op.add_column("provider_services", sa.Column("reviewed_at", sa.DateTime(timezone=True)))
    op.add_column("provider_services", sa.Column("review_note", sa.String(length=500)))
    op.add_column("provider_services", sa.Column("approved_at", sa.DateTime(timezone=True)))
    op.add_column("provider_services", sa.Column("service_area_radius_km", sa.Integer()))


def downgrade() -> None:
    op.drop_column("provider_services", "service_area_radius_km")
    op.drop_column("provider_services", "approved_at")
    op.drop_column("provider_services", "review_note")
    op.drop_column("provider_services", "reviewed_at")
    op.drop_column("provider_services", "submitted_at")
    op.drop_column("provider_services", "flow_version")
    op.drop_column("provider_services", "status")

    op.drop_constraint("uq_provider_service_step", "provider_service_step_progress", type_="unique")
    op.drop_table("provider_service_step_progress")
    op.drop_table("service_onboarding_steps")
    op.drop_table("service_onboarding_flows")
