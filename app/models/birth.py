from pydantic import BaseModel, Field
from typing import Literal

from app.models.place import PlaceIn

class PlaceIn(BaseModel):
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
        return v

class BirthInput(BaseModel):
    year: int
    month: int
    day: int
    hour: int = 0
    minute: int = 0
    second: int = 0

    place: PlaceIn

    chart_method: int = 1
    calculation_type: Literal["drik", "ss"] = "drik"

    levels: int = Field(2)

    language: str = "en"