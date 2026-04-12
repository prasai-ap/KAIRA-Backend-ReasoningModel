from fastapi import APIRouter, HTTPException

from app.models.birth import BirthInput

from app.utils.helpers import (
    jd_from_birth,
    place_to_obj,
    place_to_tuple,
    set_ayanamsa_mode_safe
)

from app.services.chart_service import compute_chart
from app.services.summary_service import compute_summary_card_en
from app.services.dasha_service import (
    compute_vimshottari,
    compute_tribhagi,
    compute_yogini
)
from app.services.yoga_service import compute_yogas_d1
from app.services.dosha_service import compute_doshas_d1

router = APIRouter()

@router.post("/api/charts")
def api_charts(inp: BirthInput) -> Dict[str, Any]:
    jd = jd_from_birth(inp)

    try:
        set_ayanamsa_mode_safe(jd)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ayanamsa setup failed: {e}")

    place_tuple = place_to_tuple(inp.place)
    place_obj = place_to_obj(inp.place)

    try:
        d1 = compute_chart(jd, place_obj, 1, inp.chart_method, inp.calculation_type)
        d9 = compute_chart(jd, place_obj, 9, inp.chart_method, inp.calculation_type)

        # ADDED: summary card (no extra fields, no nulls)
        summary_card = compute_summary_card_en(jd, place_obj, inp.chart_method, inp.calculation_type)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Chart calculation failed: {e}")

    return {
        "meta": {
            "ayanamsa": AYANAMSA_MODE,
            "julian_day": jd,
            "chart_method": inp.chart_method,
            "calculation_type": inp.calculation_type,
            "place": {
                "name": place_tuple[0],
                "latitude": place_tuple[1],
                "longitude": place_tuple[2],
                "timezone": place_tuple[3],
            },
            "birth": {"year": inp.year, "month": inp.month, "day": inp.day, "hour": inp.hour, "minute": inp.minute, "second": inp.second},
        },
        "summary_card": summary_card,
        "charts": {"D1": d1, "D9": d9},
    }

@router.post("/api/dasha")
def api_dasha(inp: BirthInput) -> Dict[str, Any]:
    if not (1 <= int(inp.levels) <= 6):
        raise HTTPException(status_code=422, detail="levels must be between 1 and 6")

    jd = jd_from_birth(inp)

    try:
        set_ayanamsa_mode_safe(jd)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ayanamsa setup failed: {e}")

    place_obj = place_to_obj(inp.place)

    try:
        vim = compute_vimshottari(jd, place_obj, levels=int(inp.levels))
        tri = compute_tribhagi(jd, place_obj, levels=int(inp.levels))
        yog = compute_yogini(jd, place_obj)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Dasha calculation failed: {e}")

    return {
        "meta": {"ayanamsa": AYANAMSA_MODE, "julian_day": jd, "levels": int(inp.levels)},
        "vimshottari": vim,
        "tribhagi": tri,
        "yogini": yog,
    }

@router.post("/api/yoga")
def api_yoga(inp: BirthInput) -> Dict[str, Any]:
    jd = jd_from_birth(inp)

    try:
        set_ayanamsa_mode_safe(jd)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ayanamsa setup failed: {e}")

    place_obj = place_to_obj(inp.place)

    try:
        yogas = compute_yogas_d1(jd, place_obj, language=inp.language)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Yoga calculation failed: {e}")

    return {"meta": {"ayanamsa": AYANAMSA_MODE, "julian_day": jd, "chart": "D1", "language": inp.language}, "yogas": yogas}

@router.post("/api/dosha")
def api_dosha(inp: BirthInput) -> Dict[str, Any]:
    jd = jd_from_birth(inp)

    try:
        set_ayanamsa_mode_safe(jd)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ayanamsa setup failed: {e}")

    place_obj = place_to_obj(inp.place)

    try:
        doshas = compute_doshas_d1(jd, place_obj, language=inp.language)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Dosha calculation failed: {e}")

    return {"meta": {"ayanamsa": AYANAMSA_MODE, "julian_day": jd, "chart": "D1", "language": inp.language}, "doshas": doshas}