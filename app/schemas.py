# backend/tyres_service/schemas.py
from pydantic import BaseModel, StringConstraints
from typing import Annotated, Literal, Optional
from decimal import Decimal
from annotated_types import Ge, Gt

# -------------------------------------------------
#                Reusable Shared Types
# -------------------------------------------------

# String types
BrandStr = Annotated[str, StringConstraints(min_length=1, max_length=50)]
ModelStr = Annotated[str, StringConstraints(min_length=1, max_length=50)]
SizeStr = Annotated[str, StringConstraints(min_length=1, max_length=20)]
SupplierStr = Annotated[str, StringConstraints(min_length=2, max_length=100)]

# Numbers
LoadRateInt = Annotated[int, Gt(0)]
NoiseLevelInt = Annotated[int, Gt(0)]
PositiveDecimal = Annotated[Decimal, Gt(0)]
QuantityInt = Annotated[int, Ge(0)]

# Literal types
SpeedRate = Literal[
    "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8",
    "B", "C", "D", "E", "F", "G", "H", "J", "K", "L",
    "M", "N", "P", "Q", "R", "S", "T", "U", "V", "W", "Y", "ZR"
]

Season = Literal["Summer", "Winter", "All Season"]

FuelEfficiency = Literal["A", "B", "C", "D", "E"]

WeatherEfficiency = Literal["A", "B", "C", "D", "E"]


# -------------------------------------------------
#                    SCHEMAS
# -------------------------------------------------

class TyreSchema(BaseModel):
    brand: BrandStr
    model: ModelStr
    size: SizeStr
    load_rate: LoadRateInt
    speed_rate: SpeedRate
    season: Season
    supplier: SupplierStr
    fuel_efficiency: FuelEfficiency
    noise_level: NoiseLevelInt
    weather_efficiency: WeatherEfficiency
    ev_approved: bool
    cost: PositiveDecimal
    quantity: QuantityInt
    retail_cost: Optional[Decimal] = None


class TyreCreate(TyreSchema):
    pass

class TyreUpdate(BaseModel):
    brand: Optional[BrandStr] = None
    model: Optional[ModelStr] = None
    size: Optional[SizeStr] = None
    load_rate: Optional[LoadRateInt] = None
    speed_rate: Optional[SpeedRate] = None
    season: Optional[Season] = None
    supplier: Optional[SupplierStr] = None
    fuel_efficiency: Optional[FuelEfficiency] = None
    noise_level: Optional[NoiseLevelInt] = None
    weather_efficiency: Optional[WeatherEfficiency] = None
    ev_approved: Optional[bool] = None
    cost: Optional[PositiveDecimal] = None
    quantity: Optional[QuantityInt] = None
