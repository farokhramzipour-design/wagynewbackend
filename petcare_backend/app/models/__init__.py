from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )


# Import models so Alembic can discover them
from app.models import users  # noqa: E402,F401
from app.models import providers  # noqa: E402,F401
from app.models import services  # noqa: E402,F401
from app.models import onboarding  # noqa: E402,F401
from app.models import availability  # noqa: E402,F401
from app.models import pets  # noqa: E402,F401
from app.models import bookings  # noqa: E402,F401
from app.models import payments  # noqa: E402,F401
from app.models import messaging  # noqa: E402,F401
from app.models import reviews  # noqa: E402,F401
from app.models import charity  # noqa: E402,F401
from app.models import geo  # noqa: E402,F401
from app.models import media  # noqa: E402,F401
