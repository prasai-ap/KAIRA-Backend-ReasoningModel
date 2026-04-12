import json
from typing import List, Dict, Any

from jhora import const, utils
from jhora.panchanga import drik
from jhora.tests import test_yogas

from app.utils.helpers import _html_to_text

def compute_yogas_d1(jd: float, place_obj: drik.Place, language: str = "en") -> List[Dict[str, Any]]:
    """
    Returns only yogas present in D1 with:
      - name
      - description
      - prediction
    """
    import json
    from jhora.tests import test_yogas

    json_file = const._LANGUAGE_PATH + const._DEFAULT_YOGA_JSON_FILE_PREFIX + language + ".json"
    with open(json_file, "r", encoding="utf-8") as f:
        msgs = json.load(f)

    planet_positions = drik.dhasavarga(jd, place_obj, divisional_chart_factor=1)
    ascendant_longitude = drik.ascendant(jd, place_obj)[1]
    asc_house, asc_long = drik.dasavarga_from_long(ascendant_longitude, divisional_chart_factor=1)
    planet_positions += [[const._ascendant_symbol, (asc_house, asc_long)]]

    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)

    items: List[Dict[str, Any]] = []
    for yoga_key, details in msgs.items():
        fn = getattr(test_yogas, yoga_key, None)
        if fn is None:
            continue
        try:
            exists = bool(fn(h_to_p))
        except Exception:
            continue

        if exists:
            name = details[0] if len(details) > 0 else yoga_key
            desc = details[1] if len(details) > 1 else ""
            pred = details[2] if len(details) > 2 else ""
            items.append(
                {
                    "key": yoga_key,
                    "chart": "D1",
                    "name": _html_to_text(name),
                    "description": _html_to_text(desc),
                    "prediction": _html_to_text(pred),
                }
            )

    items.sort(key=lambda x: (x.get("name") or "", x.get("key") or ""))
    return items
