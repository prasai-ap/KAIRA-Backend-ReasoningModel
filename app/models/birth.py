from pydantic import BaseModel, Field
from typing import Literal

from app.models.place import PlaceIn


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