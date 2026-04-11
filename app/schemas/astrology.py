from pydantic import BaseModel, Field, model_validator
from typing import Literal

class PlaceIn(BaseModel):
    """
    Accepts place either as:
      - object: {"name":..., "latitude":..., "longitude":..., "timezone":...}
      - list/tuple(4): [name, lat, lon, tz]
      - list/tuple(3): [lat, lon, tz] (name becomes "Unknown")
    """
    name: str = "Unknown"
    latitude: float
    longitude: float
    timezone: float

    @model_validator(mode="before")
    @classmethod
    def accept_tuple_or_dict(cls, v):
        if isinstance(v, (list, tuple)):
            if len(v) == 4:
                name, lat, lon, tz = v
                return {"name": name, "latitude": lat, "longitude": lon, "timezone": tz}
            if len(v) == 3:
                lat, lon, tz = v
                return {"name": "Unknown", "latitude": lat, "longitude": lon, "timezone": tz}
            raise ValueError("place must be (name,lat,lon,tz) or (lat,lon,tz)")
        return v


class BirthInput(BaseModel):
    year: int
    month: int
    day: int
    hour: int = 0
    minute: int = 0
    second: int = 0

    place: PlaceIn

    chart_method: int = Field(1, description="PyJHora chart method")
    calculation_type: Literal["drik", "ss"] = "drik"

    # PyJHora dhasa_level_index: 1..6
    levels: int = Field(
        3,
        description="Dasha depth 1..6 (1=Maha, 2=+Antar, 3=+Pratyantar, 4=+Sookshma, 5=+Prana, 6=+Deha)",
    )

    # allow frontend to choose language for yoga/dosha resources
    language: str = Field("en", description="Language code for resource messages (en, hi, ta, te, ka, ml, ...)")
