from typing import Dict, Any, Optional, Tuple

from jhora import utils
from jhora.panchanga import drik
from jhora.horoscope.chart import charts

from app.services.astrology.constants import RASI_INDEX_TO_NAME
from app.services.astrology.core_utils import strip_nulls

WEEKDAY_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

NAKSHATRA_EN = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra", "Punarvasu",
    "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra",
    "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

TITHI_NAMES_SHUKLA = [
    "Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
]
TITHI_NAMES_KRISHNA = [
    "Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya",
]

def _weekday_from_jd(jd: float) -> Optional[str]:
    try:
        import datetime as dt
        y, m, d, _fh = utils.jd_to_gregorian(jd)
        wd = dt.date(int(y), int(m), int(d)).weekday()  # Monday=0
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
        if int(pid) == 1:  # Moon
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

    if isinstance(nk, (list, tuple)) and len(nk) >= 2 and isinstance(nk[0], (int, float)) and isinstance(nk[1], (int, float)):
        nak_no = int(nk[0])
        pada = int(nk[1])
        name = NAKSHATRA_EN[nak_no - 1] if 1 <= nak_no <= 27 else None
        return (name, pada, nk)

    return (str(nk), None, nk)


def compute_summary_card_en(jd: float, place_obj: drik.Place, chart_method: int, calculation_type: str) -> Dict[str, Any]:
    lagna_sign = None
    try:
        asc = drik.ascendant(jd, place_obj)
        lagna_rasi0 = int(asc[0])
        if 0 <= lagna_rasi0 <= 11:
            lagna_sign = RASI_INDEX_TO_NAME[lagna_rasi0]
    except Exception:
        pass

    rasi_sign = None
    try:
        pp_d1 = charts.divisional_chart(
            jd_at_dob=jd,
            place_as_tuple=place_obj,
            divisional_chart_factor=1,
            chart_method=chart_method,
            calculation_type=calculation_type,
        )
        rasi_sign = _moon_rasi_from_d1_positions(pp_d1)
    except Exception:
        pass

    nak_name, pada, _nak_raw = _nakshatra_from_drik(jd, place_obj)

    out: Dict[str, Any] = {
        "weekday": _weekday_from_jd(jd),
        "tithi": _tithi_from_drik(jd, place_obj),
        "lagna": lagna_sign,
        "rasi": rasi_sign,
        "nakshatra": nak_name,
        "pada": pada,
    }

    return strip_nulls(out)