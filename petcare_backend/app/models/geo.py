from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class Country(Base):
    __tablename__ = "countries"

    country_code: Mapped[str] = mapped_column(String(2), primary_key=True)


class Province(Base):
    __tablename__ = "provinces"
    __table_args__ = (UniqueConstraint("code", name="uq_province_code"),)

    province_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    country_code: Mapped[str] = mapped_column(
        String(2), ForeignKey("countries.country_code", ondelete="RESTRICT"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False)


class City(Base):
    __tablename__ = "cities"
    __table_args__ = (UniqueConstraint("name_fa", name="uq_city_name_fa"),)

    city_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    province_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("provinces.province_id", ondelete="CASCADE"), nullable=False
    )
    name_fa: Mapped[str] = mapped_column(String(128), nullable=False)


class Currency(Base):
    __tablename__ = "currencies"

    currency_code: Mapped[str] = mapped_column(String(3), primary_key=True)
    minor_unit: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
