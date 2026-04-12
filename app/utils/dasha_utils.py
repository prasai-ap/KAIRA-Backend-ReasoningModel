from typing import Any, Dict, Optional, List, Tuple
from app.core.config import YOGINI_LORD_ID_TO_YOGINI_NAME

def _set_end_times(items: List[Dict[str, Any]]) -> None:
    for i in range(len(items)):
        items[i]["end"] = items[i + 1].get("start") if i < len(items) - 1 else None

def _fill_last_end_from_parent(items: List[Dict[str, Any]], parent_end: Optional[str]) -> None:
    """
    After calling _set_end_times(items), ensure the LAST item end is not null.
    Uses parent_end (e.g., antar.end for pratyantar list, maha.end for antar list).
    """
    if not items:
        return
    if items[-1].get("end") is None and parent_end:
        items[-1]["end"] = parent_end


def _ensure_nested_dasha_end_dates(tree: Dict[str, Any]) -> None:
    """
    Ensures no end:null at the last element of each list by propagating parent end downward.
    Works with your current tree shape:
      tree = {"level": ..., "mahadashas":[{"end":..., "antardashas":[{"end":..., "pratyantardashas":[...]}]}]}
    """
    mahadashas = tree.get("mahadashas") or []
    for maha in mahadashas:
        antar_list = maha.get("antardashas") or []
        _fill_last_end_from_parent(antar_list, maha.get("end"))

        for antar in antar_list:
            praty_list = antar.get("pratyantardashas") or []
            _fill_last_end_from_parent(praty_list, antar.get("end"))

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
            maha_map[maha_pid] = {"planet_id": maha_pid, "planet": _planet_name(maha_pid), "start": None, "end": None, "antardashas": []}

        maha_entry = maha_map[maha_pid]
        if maha_entry["start"] is None:
            maha_entry["start"] = start_str

        antar_list: List[Dict[str, Any]] = maha_entry["antardashas"]
        antar_node = next((x for x in antar_list if int(x["planet_id"]) == antara_pid), None)
        if antar_node is None:
            antar_node = {"planet_id": antara_pid, "planet": _planet_name(antara_pid), "start": start_str, "end": None}
            if lvl >= 3:
                antar_node["pratyantardashas"] = []
            antar_list.append(antar_node)

        if lvl >= 3:
            if len(r) < 4:
                continue
            praty_pid = int(r[2])
            praty_list: List[Dict[str, Any]] = antar_node["pratyantardashas"]  # type: ignore[index]
            praty_list.append({"planet_id": praty_pid, "planet": _planet_name(praty_pid), "start": start_str, "end": None})

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
                maha_map[l1] = {"yogini": _yogini_name_from_lord_id(l1), "lord_planet_id": l1, "lord_planet": _planet_name(l1), "start": None, "end": None, "antardashas": []}

            maha = maha_map[l1]
            if maha["start"] is None:
                maha["start"] = start_str

            maha["antardashas"].append({"yogini": _yogini_name_from_lord_id(l2), "lord_planet_id": l2, "lord_planet": _planet_name(l2), "start": start_str, "end": None, "dur_years": dur_years})

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
