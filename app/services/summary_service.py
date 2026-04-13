from typing import Any, Dict
from jhora.panchanga import drik
from jhora.horoscope.chart import charts

from app.core.astrology_config import RASI_INDEX_TO_NAME
from app.utils.astrology_helpers import (
    _weekday_from_jd,
    _tithi_from_drik,
    _moon_rasi_from_d1_positions,
    _nakshatra_from_drik,
    strip_nulls,
)


def compute_summary_card_en(
    jd: float,
    place_obj: drik.Place,
    chart_method: int,
    calculation_type: str,
) -> Dict[str, Any]:
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

    nak_name, pada, _ = _nakshatra_from_drik(jd, place_obj)

    out: Dict[str, Any] = {
        "weekday": _weekday_from_jd(jd),
        "tithi": _tithi_from_drik(jd, place_obj),
        "lagna": lagna_sign,
        "rasi": rasi_sign,
        "nakshatra": nak_name,
        "pada": pada,
    }

    return strip_nulls(out)