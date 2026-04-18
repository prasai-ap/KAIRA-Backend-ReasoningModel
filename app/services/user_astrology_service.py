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


def generate_or_get_user_astrology(db, user, birth_input):
    existing = get_user_astrology(db, user.id)

    if existing:
        return {
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

    jd = jd_from_birth(birth_input)
    set_ayanamsa_mode_safe(jd)

    place_obj = place_to_obj(birth_input.place)
    place_tuple = place_to_tuple(birth_input.place)

    d1 = compute_chart(jd, place_obj, 1, birth_input.chart_method, birth_input.calculation_type)
    d9 = compute_chart(jd, place_obj, 9, birth_input.chart_method, birth_input.calculation_type)
    summary_card = compute_summary_card_en(jd, place_obj, birth_input.chart_method, birth_input.calculation_type)

    charts_result = {
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
        "charts": {
            "D1": d1,
            "D9": d9,
        },
    }

    vim = compute_vimshottari(jd, place_obj, levels=int(birth_input.levels))
    tri = compute_tribhagi(jd, place_obj, levels=int(birth_input.levels))
    yogini = compute_yogini(jd, place_obj)

    dasha_result = {
        "meta": {
            "ayanamsa": AYANAMSA_MODE,
            "julian_day": jd,
            "levels": int(birth_input.levels),
        },
        "vimshottari": vim,
        "tribhagi": tri,
        "yogini": yogini,
    }

    yoga_result = {
        "meta": {
            "ayanamsa": AYANAMSA_MODE,
            "julian_day": jd,
            "chart": "D1",
            "language": birth_input.language,
        },
        "yogas": compute_yogas_d1(jd, place_obj, language=birth_input.language),
    }

    dosha_result = {
        "meta": {
            "ayanamsa": AYANAMSA_MODE,
            "julian_day": jd,
            "chart": "D1",
            "language": birth_input.language,
        },
        "doshas": compute_doshas_d1(jd, place_obj, language=birth_input.language),
    }

    saved = create_user_astrology(
        db=db,
        user_id=user.id,
        input_data=birth_input.model_dump(),
        charts=charts_result,
        dasha=dasha_result,
        yoga=yoga_result,
        dosha=dosha_result,
    )

    return {
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


def get_saved_user_astrology(db, user):
    existing = get_user_astrology(db, user.id)

    if not existing:
        return None

    return {
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


def regenerate_user_astrology(db, user, birth_input):
    jd = jd_from_birth(birth_input)
    set_ayanamsa_mode_safe(jd)

    place_obj = place_to_obj(birth_input.place)
    place_tuple = place_to_tuple(birth_input.place)

    d1 = compute_chart(jd, place_obj, 1, birth_input.chart_method, birth_input.calculation_type)
    d9 = compute_chart(jd, place_obj, 9, birth_input.chart_method, birth_input.calculation_type)
    summary_card = compute_summary_card_en(jd, place_obj, birth_input.chart_method, birth_input.calculation_type)

    charts_result = {
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
        "charts": {
            "D1": d1,
            "D9": d9,
        },
    }

    vim = compute_vimshottari(jd, place_obj, levels=int(birth_input.levels))
    tri = compute_tribhagi(jd, place_obj, levels=int(birth_input.levels))
    yogini = compute_yogini(jd, place_obj)

    dasha_result = {
        "meta": {
            "ayanamsa": AYANAMSA_MODE,
            "julian_day": jd,
            "levels": int(birth_input.levels),
        },
        "vimshottari": vim,
        "tribhagi": tri,
        "yogini": yogini,
    }

    yoga_result = {
        "meta": {
            "ayanamsa": AYANAMSA_MODE,
            "julian_day": jd,
            "chart": "D1",
            "language": birth_input.language,
        },
        "yogas": compute_yogas_d1(jd, place_obj, language=birth_input.language),
    }

    dosha_result = {
        "meta": {
            "ayanamsa": AYANAMSA_MODE,
            "julian_day": jd,
            "chart": "D1",
            "language": birth_input.language,
        },
        "doshas": compute_doshas_d1(jd, place_obj, language=birth_input.language),
    }

    existing = get_user_astrology(db, user.id)
    if existing:
        updated = update_user_astrology(
            db=db,
            obj=existing,
            input_data=birth_input.model_dump(),
            charts=charts_result,
            dasha=dasha_result,
            yoga=yoga_result,
            dosha=dosha_result,
        )
        return {
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

    return generate_or_get_user_astrology(db, user, birth_input)