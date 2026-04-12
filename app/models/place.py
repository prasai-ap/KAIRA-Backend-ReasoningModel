from pydantic import BaseModel, model_validator


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