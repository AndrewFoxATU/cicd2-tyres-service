# backend/tyres_service/models.py
from sqlalchemy import Column, Integer, String, Boolean, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from decimal import Decimal

class Base(DeclarativeBase):
    pass

class TyreModel(Base):
    __tablename__ = "tyres"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    brand: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[str] = mapped_column(String, nullable=False)
    load_rate: Mapped[int] = mapped_column(Integer, nullable=False)
    speed_rate: Mapped[str] = mapped_column(String, nullable=False)
    season: Mapped[str] = mapped_column(String, nullable=False)
    supplier: Mapped[str] = mapped_column(String, nullable=False)
    fuel_efficiency: Mapped[str] = mapped_column(String, nullable=False)
    noise_level: Mapped[int] = mapped_column(Integer, nullable=False)
    weather_efficiency: Mapped[str] = mapped_column(String, nullable=False)
    ev_approved: Mapped[bool] = mapped_column(Boolean, nullable=False)
    cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    retail_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
