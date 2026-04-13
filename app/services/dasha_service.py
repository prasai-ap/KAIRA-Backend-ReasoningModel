from typing import Any, Dict, List, Tuple
from jhora import utils
from jhora.panchanga import drik
from jhora.horoscope.dhasa.graha import vimsottari
from jhora.horoscope.dhasa.graha import yogini as yogini_mod

from app.utils.astrology_helpers import (
    _planet_name,
    _yogini_name_from_lord_id,
    _set_end_times,
    _fill_last_end_from_parent,
    _ensure_nested_dasha_end_dates,
)


def dasha_rows_to_tree(rows: List[List[Any]], level: int) -> Dict[str, Any]:
    lvl = int(level)

    if lvl <= 1:
        mahadashas: List[Dict[str, Any]] = []
        for r in rows:
            if len(r) < 2:
                continue
            maha_pid = int(r[0])
            start_str = r[-1]
            mahadashas.append({"planet_id": maha_pid, "planet": _planet_name(maha_pid), "start": start_str})
        _set_end_times(mahadashas)
        return {"level": 1, "mahadashas": mahadashas}

    maha_map: Dict[int, Dict[str, Any]] = {}
    for r in rows:
        if len(r) < 3:
            continue
        maha_pid = int(r[0])
        antara_pid = int(r[1])
        start_str = r[-1]

        if maha_pid not in maha_map:
            maha_map[maha_pid] = {
                "planet_id": maha_pid,
                "planet": _planet_name(maha_pid),
                "start": None,
                "end": None,
                "antardashas": [],
            }

        maha_entry = maha_map[maha_pid]
        if maha_entry["start"] is None:
            maha_entry["start"] = start_str

        antar_list: List[Dict[str, Any]] = maha_entry["antardashas"]
        antar_node = next((x for x in antar_list if int(x["planet_id"]) == antara_pid), None)
        if antar_node is None:
            antar_node = {
                "planet_id": antara_pid,
                "planet": _planet_name(antara_pid),
                "start": start_str,
                "end": None,
            }
            if lvl >= 3:
                antar_node["pratyantardashas"] = []
            antar_list.append(antar_node)

        if lvl >= 3:
            if len(r) < 4:
                continue
            praty_pid = int(r[2])
            praty_list: List[Dict[str, Any]] = antar_node["pratyantardashas"]
            praty_list.append(
                {
                    "planet_id": praty_pid,
                    "planet": _planet_name(praty_pid),
                    "start": start_str,
                    "end": None,
                }
            )

    mahadashas = list(maha_map.values())
    mahadashas.sort(key=lambda x: (x["start"] or ""))
    _set_end_times(mahadashas)

    for maha in mahadashas:
        antar_list = maha.get("antardashas", [])
        antar_list.sort(key=lambda x: x.get("start") or "")
        _set_end_times(antar_list)

        for antar in antar_list:
            if "pratyantardashas" in antar:
                praty_list = antar["pratyantardashas"]
                praty_list.sort(key=lambda x: x.get("start") or "")
                _set_end_times(praty_list)

    return {"level": max(2, lvl), "mahadashas": mahadashas}


def yogini_rows_to_tree_level2(rows: List[Tuple[Any, ...]]) -> Dict[str, Any]:
    maha_map: Dict[int, Dict[str, Any]] = {}
    for r in rows:
        if len(r) < 4:
            continue
        l1 = int(r[0])
        l2 = int(r[1])
        start_str = r[-2]
        dur_years = float(r[-1])

        if l1 not in maha_map:
            maha_map[l1] = {
                "yogini": _yogini_name_from_lord_id(l1),
                "lord_planet_id": l1,
                "lord_planet": _planet_name(l1),
                "start": None,
                "end": None,
                "antardashas": [],
            }

        maha = maha_map[l1]
        if maha["start"] is None:
            maha["start"] = start_str

        maha["antardashas"].append(
            {
                "yogini": _yogini_name_from_lord_id(l2),
                "lord_planet_id": l2,
                "lord_planet": _planet_name(l2),
                "start": start_str,
                "end": None,
                "dur_years": dur_years,
            }
        )

    mahadashas = list(maha_map.values())
    mahadashas.sort(key=lambda x: (x["start"] or ""))
    _set_end_times(mahadashas)

    for maha in mahadashas:
        antar_list = maha["antardashas"]
        antar_list.sort(key=lambda x: x.get("start") or "")
        _set_end_times(antar_list)
        _fill_last_end_from_parent(antar_list, maha.get("end"))

    if mahadashas:
        last_maha = mahadashas[-1]
        if last_maha.get("end") is None and last_maha.get("antardashas"):
            last_maha["end"] = last_maha["antardashas"][-1].get("end")

    return {"level": 2, "mahadashas": mahadashas}


def compute_vimshottari(jd: float, place_obj: drik.Place, levels: int) -> Dict[str, Any]:
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

    rows = yogini_mod.get_dhasa_bhukthi(
        dob=dob,
        tob=tob,
        place=place_obj,
        use_tribhagi_variation=False,
        dhasa_level_index=2,
    )
    return {"type": "yogini", "tree": yogini_rows_to_tree_level2(rows)}