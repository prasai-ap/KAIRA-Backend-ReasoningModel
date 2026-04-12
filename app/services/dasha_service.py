from typing import Dict, Any
from jhora.horoscope.dhasa.graha import vimsottari
from jhora.horoscope.dhasa.graha import yogini as yogini_mod
from jhora import utils, const
from jhora.panchanga import drik

from app.utils.dasha_utils import (
    dasha_rows_to_tree,
    yogini_rows_to_tree_level2,
    _ensure_nested_dasha_end_dates
)

def compute_vimshottari(jd: float, place_obj: drik.Place, levels: int) -> Dict[str, Any]:
    from jhora.horoscope.dhasa.graha import vimsottari
    vim_bal, rows = vimsottari.get_vimsottari_dhasa_bhukthi(
        jd=jd,
        place=place_obj,
        use_tribhagi_variation=False,
        dhasa_level_index=int(levels),
    )
    tree = dasha_rows_to_tree(rows, level=levels)
    _ensure_nested_dasha_end_dates(tree)
    return {"type": "vimshottari", "balance": vim_bal, "tree": tree}


def compute_tribhagi(jd: float, place_obj: drik.Place, levels: int) -> Dict[str, Any]:
    from jhora.horoscope.dhasa.graha import vimsottari
    vim_bal, rows = vimsottari.get_vimsottari_dhasa_bhukthi(
        jd=jd,
        place=place_obj,
        use_tribhagi_variation=True,
        dhasa_level_index=int(levels),
    )
    tree = dasha_rows_to_tree(rows, level=levels)
    _ensure_nested_dasha_end_dates(tree)
    return {"type": "tribhagi", "balance": vim_bal, "tree": tree}

def compute_yogini(jd: float, place_obj: drik.Place) -> Dict[str, Any]:
    y, m, d, fh = utils.jd_to_gregorian(jd)
    dob = drik.Date(int(y), int(m), int(d))
    hour = int(fh)
    minute = int((fh - hour) * 60)
    second = int(round((((fh - hour) * 60) - minute) * 60))
    tob = (hour, minute, second)

    rows = yogini_mod.get_dhasa_bhukthi(dob=dob, tob=tob, place=place_obj, use_tribhagi_variation=False, dhasa_level_index=2)
    return {"type": "yogini", "tree": yogini_rows_to_tree_level2(rows)}