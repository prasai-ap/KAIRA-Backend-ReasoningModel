from jhora.horoscope.chart import dosha
from app.services.astrology.core_utils import _html_to_text

def compute_doshas_d1(jd: float, place_obj: drik.Place, language: str = "en") -> List[Dict[str, Any]]:
    """
    Returns doshas present with details text.
    """
    from jhora.horoscope.chart import dosha as dosha_mod

    dosha_dict = dosha_mod.get_dosha_details(jd, place_obj, language=language)
    items: List[Dict[str, Any]] = [{"name": str(name), "details": _html_to_text(html)} for name, html in dosha_dict.items()]
    items.sort(key=lambda x: x["name"])
    return items
