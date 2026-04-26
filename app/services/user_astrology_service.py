from datetime import datetime, timezone

from app.db.user_astrology_repository import (
    get_user_astrology,
    create_user_astrology,
    update_user_astrology,
)

from app.services.chart_service import compute_chart
from app.services.summary_service import compute_summary_card_en
from app.services.dasha_service import compute_vimshottari, compute_tribhagi, compute_yogini
from app.services.yoga_service import compute_yogas_d1
from app.services.dosha_service import compute_doshas_d1
from app.utils.astrology_helpers import jd_from_birth, set_ayanamsa_mode_safe, place_to_obj, place_to_tuple
from app.core.astrology_config import AYANAMSA_MODE


DIVISIONAL_CHARTS = {
    "D1": 1,
    "D2": 2,
    "D3": 3,
    "D4": 4,
    "D7": 7,
    "D9": 9,
    "D10": 10,
    "D12": 12,
    "D16": 16,
    "D20": 20,
    "D24": 24,
    "D27": 27,
    "D30": 30,
    "D40": 40,
    "D45": 45,
    "D60": 60,
}


def calculate_age_from_input(input_data):
    today = datetime.now(timezone.utc)

    birth_year = int(input_data["year"])
    birth_month = int(input_data["month"])
    birth_day = int(input_data["day"])

    age = today.year - birth_year

    if (today.month, today.day) < (birth_month, birth_day):
        age -= 1

    return age


def get_moon_rashi_from_charts(charts):
    d1 = charts.get("D1", {})
    positions = d1.get("positions", [])

    for item in positions:
        if item.get("planet") == "Moon":
            return item.get("rasi")

    return None


def inject_dynamic_age(data):
    age = calculate_age_from_input(data["input_data"])

    if isinstance(data.get("charts"), dict):
        summary_card = data["charts"].get("summary_card")

        if isinstance(summary_card, dict):
            summary_card["current_age"] = age
            summary_card["age_as_of_date"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    return data


def compute_all_charts(jd, place_obj, chart_method, calculation_type):
    charts = {}

    for chart_name, division in DIVISIONAL_CHARTS.items():
        try:
            charts[chart_name] = compute_chart(
                jd,
                place_obj,
                division,
                chart_method,
                calculation_type,
            )
        except Exception as e:
            charts[chart_name] = {
                "error": f"Failed to compute {chart_name}: {str(e)}"
            }

    return charts


def build_charts_result(jd, place_obj, place_tuple, birth_input):
    summary_card = compute_summary_card_en(
        jd,
        place_obj,
        birth_input.chart_method,
        birth_input.calculation_type,
    )

    charts = compute_all_charts(
        jd,
        place_obj,
        birth_input.chart_method,
        birth_input.calculation_type,
    )

    moon_rashi = get_moon_rashi_from_charts(charts)

    if isinstance(summary_card, dict):
        summary_card["moon_rashi"] = moon_rashi
        summary_card["horoscope"] = moon_rashi

    return {
        "meta": {
            "ayanamsa": AYANAMSA_MODE,
            "julian_day": jd,
            "chart_method": birth_input.chart_method,
            "calculation_type": birth_input.calculation_type,
            "place": {
                "name": place_tuple[0],
                "latitude": place_tuple[1],
                "longitude": place_tuple[2],
                "timezone": place_tuple[3],
            },
            "birth": {
                "year": birth_input.year,
                "month": birth_input.month,
                "day": birth_input.day,
                "hour": birth_input.hour,
                "minute": birth_input.minute,
                "second": birth_input.second,
            },
        },
        "summary_card": summary_card,
        "charts": charts,
    }


def build_dasha_result(jd, place_obj, birth_input):
    vim = compute_vimshottari(jd, place_obj, levels=int(birth_input.levels))
    tri = compute_tribhagi(jd, place_obj, levels=int(birth_input.levels))
    yogini = compute_yogini(jd, place_obj)

    return {
        "meta": {
            "ayanamsa": AYANAMSA_MODE,
            "julian_day": jd,
            "levels": int(birth_input.levels),
        },
        "vimshottari": vim,
        "tribhagi": tri,
        "yogini": yogini,
    }


def build_yoga_result(jd, place_obj, birth_input):
    return {
        "meta": {
            "ayanamsa": AYANAMSA_MODE,
            "julian_day": jd,
            "chart": "D1",
            "language": birth_input.language,
        },
        "yogas": compute_yogas_d1(jd, place_obj, language=birth_input.language),
    }


def build_dosha_result(jd, place_obj, birth_input):
    return {
        "meta": {
            "ayanamsa": AYANAMSA_MODE,
            "julian_day": jd,
            "chart": "D1",
            "language": birth_input.language,
        },
        "doshas": compute_doshas_d1(jd, place_obj, language=birth_input.language),
    }


def prepare_astrology_payload(birth_input):
    jd = jd_from_birth(birth_input)
    set_ayanamsa_mode_safe(jd)

    place_obj = place_to_obj(birth_input.place)
    place_tuple = place_to_tuple(birth_input.place)

    charts_result = build_charts_result(jd, place_obj, place_tuple, birth_input)
    dasha_result = build_dasha_result(jd, place_obj, birth_input)
    yoga_result = build_yoga_result(jd, place_obj, birth_input)
    dosha_result = build_dosha_result(jd, place_obj, birth_input)

    return {
        "input_data": birth_input.model_dump(),
        "charts": charts_result,
        "dasha": dasha_result,
        "yoga": yoga_result,
        "dosha": dosha_result,
    }


def generate_or_get_user_astrology(db, user, birth_input):
    existing = get_user_astrology(db, user.id)

    if existing:
        data = {
            "source": "database",
            "meta": {
                "user_id": str(user.id),
            },
            "input_data": existing.input_data,
            "charts": existing.charts,
            "dasha": existing.dasha,
            "yoga": existing.yoga,
            "dosha": existing.dosha,
        }

        return inject_dynamic_age(data)

    payload = prepare_astrology_payload(birth_input)

    saved = create_user_astrology(
        db=db,
        user_id=user.id,
        input_data=payload["input_data"],
        charts=payload["charts"],
        dasha=payload["dasha"],
        yoga=payload["yoga"],
        dosha=payload["dosha"],
    )

    data = {
        "source": "computed_and_saved",
        "meta": {
            "user_id": str(user.id),
        },
        "input_data": saved.input_data,
        "charts": saved.charts,
        "dasha": saved.dasha,
        "yoga": saved.yoga,
        "dosha": saved.dosha,
    }

    return inject_dynamic_age(data)


def get_saved_user_astrology(db, user):
    existing = get_user_astrology(db, user.id)

    if not existing:
        return None

    data = {
        "source": "database",
        "meta": {
            "user_id": str(user.id),
        },
        "input_data": existing.input_data,
        "charts": existing.charts,
        "dasha": existing.dasha,
        "yoga": existing.yoga,
        "dosha": existing.dosha,
    }

    return inject_dynamic_age(data)


def regenerate_user_astrology(db, user, birth_input):
    payload = prepare_astrology_payload(birth_input)

    existing = get_user_astrology(db, user.id)
    if existing:
        updated = update_user_astrology(
            db=db,
            obj=existing,
            input_data=payload["input_data"],
            charts=payload["charts"],
            dasha=payload["dasha"],
            yoga=payload["yoga"],
            dosha=payload["dosha"],
        )

        data = {
            "source": "recomputed_and_updated",
            "meta": {
                "user_id": str(user.id),
            },
            "input_data": updated.input_data,
            "charts": updated.charts,
            "dasha": updated.dasha,
            "yoga": updated.yoga,
            "dosha": updated.dosha,
        }

        return inject_dynamic_age(data)

    return generate_or_get_user_astrology(db, user, birth_input)