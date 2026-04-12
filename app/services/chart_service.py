from typing import Any, Dict, List
from jhora.horoscope.chart import charts
from jhora.panchanga import drik
from jhora import const
from app.utils.helpers import _house_from_lagna

def _house_from_lagna(lagna_rasi_index: int, planet_rasi_index: int) -> int:
    return ((int(planet_rasi_index) - int(lagna_rasi_index)) % 12) + 1


def positions_to_json_with_houses(planet_positions: List[Any]) -> Dict[str, Any]:
    lagna_rasi0 = None
    for planet_id, (rasi, _lon) in planet_positions:
        if planet_id == const._ascendant_symbol:
            lagna_rasi0 = int(rasi)
            break
    if lagna_rasi0 is None:
        lagna_rasi0 = 0

    out: List[Dict[str, Any]] = []
    for planet_id, (rasi, lon) in planet_positions:
        rasi0 = int(rasi)
        out.append(
            {
                "planet_id": planet_id,
                "planet": PLANET_ID_TO_NAME.get(planet_id, str(planet_id)),
                "rasi_no": rasi0 + 1,
                "rasi_index": rasi0,
                "rasi": RASI_INDEX_TO_NAME[rasi0],
                "house": _house_from_lagna(lagna_rasi0, rasi0),
                "longitude_in_rasi": float(lon),
                "absolute_longitude": float(rasi0 * 30.0 + float(lon)),
            }
        )

    return {
        "lagna": {"rasi_no": lagna_rasi0 + 1, "rasi_index": lagna_rasi0, "rasi": RASI_INDEX_TO_NAME[lagna_rasi0]},
        "positions": out,
    }


def compute_chart(jd: float, place_obj: drik.Place, divisional_chart_factor: int, chart_method: int, calculation_type: str) -> Dict[str, Any]:
    pp = charts.divisional_chart(
        jd_at_dob=jd,
        place_as_tuple=place_obj,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        calculation_type=calculation_type,
    )
    return positions_to_json_with_houses(pp)
