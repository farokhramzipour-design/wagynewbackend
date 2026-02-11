from datetime import datetime

from pydantic import BaseModel, Field


class ServiceOnboardingFlowCreate(BaseModel):
    service_type_id: int
    version: int
    name: str
    is_active: bool = True


class ServiceOnboardingStepCreate(BaseModel):
    flow_id: int
    code: str
    title_fa: str | None = None
    title_en: str | None = None
    sort_order: int
    is_required: bool
    review_required: bool
    schema_json: dict | None = None
    completion_rule_json: dict | None = None


class ServiceOnboardingFlowOut(BaseModel):
    flow_id: int
    service_type_id: int
    version: int
    name: str
    is_active: bool
    created_at: datetime


class ServiceOnboardingStepOut(BaseModel):
    step_id: int
    flow_id: int
    code: str
    title_fa: str | None = None
    title_en: str | None = None
    sort_order: int
    is_required: bool
    review_required: bool
    schema_json: dict | None = None
    completion_rule_json: dict | None = None
    created_at: datetime


class ProviderServiceEnable(BaseModel):
    provider_id: int
    service_type_id: int


class ProviderServiceStepSave(BaseModel):
    data_json: dict | None = None


class ProviderServiceStepComplete(BaseModel):
    data_json: dict | None = None


class ProviderServiceSubmit(BaseModel):
    provider_service_id: int


class ProviderServiceStatusUpdate(BaseModel):
    status: str
    review_note: str | None = None


class ProviderServiceStepProgressOut(BaseModel):
    progress_id: int
    provider_service_id: int
    step_id: int
    status: str
    data_json: dict | None = None
    completed_at: datetime | None = None
    review_note: str | None = None
    created_at: datetime
    updated_at: datetime | None = None


class ProviderServiceMissingOut(BaseModel):
    provider_service_id: int
    service_type_id: int
    status: str
    missing_steps: list[str]


class ProviderOnboardingSummaryOut(BaseModel):
    provider_id: int
    provider_status: str
    verifications: list[dict]
    services: list[ProviderServiceMissingOut]


class ProviderServiceReviewStepOut(BaseModel):
    step_id: int
    code: str
    status: str
    data_json: dict | None = None
    review_note: str | None = None
    completed_at: datetime | None = None


class ProviderServiceReviewOut(BaseModel):
    provider_service_id: int
    status: str
    review_note: str | None = None
    steps: list[ProviderServiceReviewStepOut]
