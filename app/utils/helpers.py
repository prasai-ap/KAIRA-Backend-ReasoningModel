import re
from typing import Any, Dict, List, Optional, Tuple

from app.models.birth import PlaceIn, BirthInput
from app.core.config import (
    YOGINI_LORD_ID_TO_YOGINI_NAME,
    DASHA_PLANET_ID_TO_NAME,
    AYANAMSA_MODE,
    WEEKDAY_EN,
    NAKSHATRA_EN,
    TITHI_NAMES_SHUKLA,
    TITHI_NAMES_KRISHNA,
    RASI_INDEX_TO_NAME,
)

from jhora import utils, const
from jhora.panchanga import drik

def _validate_jd(jd: float) -> None:
    if jd < 625000.5 or jd > 2818000.5:
        raise ValueError(f"Invalid JD computed: {jd}. Check input birth date/time.")


def set_ayanamsa_mode_safe(jd: float) -> None:
    _validate_jd(jd)

    mode = str(AYANAMSA_MODE).upper()
    available = {k.upper() for k in const.available_ayanamsa_modes.keys()}
    if mode not in available:
        raise RuntimeError(f"Ayanamsa mode {mode} not available. Available: {sorted(available)}")

    drik.set_ayanamsa_mode(mode, jd=jd)


def _house_from_lagna(lagna_rasi_index: int, planet_rasi_index: int) -> int:
    return ((int(planet_rasi_index) - int(lagna_rasi_index)) % 12) + 1


def place_to_tuple(p: PlaceIn) -> Tuple[str, float, float, float]:
    return (str(p.name), float(p.latitude), float(p.longitude), float(p.timezone))


def place_to_obj(p: PlaceIn) -> drik.Place:
    return drik.Place(str(p.name), float(p.latitude), float(p.longitude), float(p.timezone))


def jd_from_birth(b: BirthInput) -> float:
    dob = drik.Date(b.year, b.month, b.day)
    tob = (b.hour, b.minute, b.second)
    return utils.julian_day_number(dob, tob)


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


def _weekday_from_jd(jd: float) -> Optional[str]:
    try:
        import datetime as dt
        y, m, d, _fh = utils.jd_to_gregorian(jd)
        wd = dt.date(int(y), int(m), int(d)).weekday()
        return WEEKDAY_EN[wd]
    except Exception:
        return None


def _tithi_from_drik(jd: float, place_obj: drik.Place) -> Optional[Dict[str, Any]]:
    if not hasattr(drik, "tithi"):
        return None

    t = None
    for args in ((jd, place_obj), (jd,)):
        try:
            t = drik.tithi(*args)
            break
        except Exception:
            continue

    if t is None:
        return None

    info: Dict[str, Any] = {"tithi_no": None, "paksha": None, "name": None, "raw": t}

    if isinstance(t, (list, tuple)) and len(t) > 0 and isinstance(t[0], (int, float)):
        tno = int(t[0])
        info["tithi_no"] = tno

        if 1 <= tno <= 15:
            info["paksha"] = "Shukla"
            info["name"] = f"Shukla {TITHI_NAMES_SHUKLA[tno - 1]}"
        elif 16 <= tno <= 30:
            info["paksha"] = "Krishna"
            info["name"] = f"Krishna {TITHI_NAMES_KRISHNA[tno - 16]}"
    elif isinstance(t, str):
        info["name"] = t

    return info


def _moon_rasi_from_d1_positions(d1_positions: List[Any]) -> Optional[str]:
    for pid, (rasi, _lon) in d1_positions:
        if int(pid) == 1:
            rasi0 = int(rasi)
            if 0 <= rasi0 <= 11:
                return RASI_INDEX_TO_NAME[rasi0]
    return None


def _nakshatra_from_drik(jd: float, place_obj: drik.Place) -> Tuple[Optional[str], Optional[int], Any]:
    if not hasattr(drik, "nakshatra"):
        return (None, None, None)

    try:
        nk = drik.nakshatra(jd, place_obj)
    except Exception:
        return (None, None, None)

    if (
        isinstance(nk, (list, tuple))
        and len(nk) >= 2
        and isinstance(nk[0], (int, float))
        and isinstance(nk[1], (int, float))
    ):
        nak_no = int(nk[0])
        pada = int(nk[1])
        name = NAKSHATRA_EN[nak_no - 1] if 1 <= nak_no <= 27 else None
        return (name, pada, nk)

    return (str(nk), None, nk)