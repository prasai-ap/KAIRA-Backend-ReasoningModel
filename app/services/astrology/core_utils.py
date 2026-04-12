import re
from typing import Any, Dict, List, Tuple, Optional

from jhora import const, utils
from jhora.panchanga import drik

from app.core.config import AYANAMSA_MODE

def _validate_jd(jd: float) -> None:
    # Swiss Ephemeris supported JD range shown in your error message
    if jd < 625000.5 or jd > 2818000.5:
        raise ValueError(f"Invalid JD computed: {jd}. Check input birth date/time.")


def set_ayanamsa_mode_safe(jd: float) -> None:
    _validate_jd(jd)

    mode = str(AYANAMSA_MODE).upper()
    available = {k.upper() for k in const.available_ayanamsa_modes.keys()}
    if mode not in available:
        raise RuntimeError(f"Ayanamsa mode {mode} not available. Available: {sorted(available)}")

    drik.set_ayanamsa_mode(mode, jd=jd)


def place_to_tuple(p: PlaceIn) -> Tuple[str, float, float, float]:
    return (str(p.name), float(p.latitude), float(p.longitude), float(p.timezone))


def place_to_obj(p: PlaceIn) -> drik.Place:
    return drik.Place(str(p.name), float(p.latitude), float(p.longitude), float(p.timezone))


def jd_from_birth(b: BirthInput) -> float:
    dob = drik.Date(b.year, b.month, b.day)
    tob = (b.hour, b.minute, b.second)
    return utils.julian_day_number(dob, tob)


def _set_end_times(items: List[Dict[str, Any]]) -> None:
    for i in range(len(items)):
        items[i]["end"] = items[i + 1].get("start") if i < len(items) - 1 else None


def _html_to_text(s: Any) -> str:
    if s is None:
        return ""
    s = str(s)
    s = s.replace("<br><br>", "\n\n").replace("<br>", "\n")
    s = re.sub(r"</?html>", "", s, flags=re.IGNORECASE)
    s = re.sub(r"<[^>]+>", "", s)
    return s.strip()

def strip_nulls(obj: Any) -> Any:
    if isinstance(obj, dict):
        cleaned: Dict[str, Any] = {}
        for k, v in obj.items():
            v2 = strip_nulls(v)
            if v2 is None:
                continue
            if isinstance(v2, dict) and not v2:
                continue
            if isinstance(v2, list) and not v2:
                continue
            cleaned[k] = v2
        return cleaned
    if isinstance(obj, list):
        cleaned_list: List[Any] = []
        for v in obj:
            v2 = strip_nulls(v)
            if v2 is None:
                continue
            if isinstance(v2, dict) and not v2:
                continue
            if isinstance(v2, list) and not v2:
                continue
            cleaned_list.append(v2)
        return cleaned_list
    return obj