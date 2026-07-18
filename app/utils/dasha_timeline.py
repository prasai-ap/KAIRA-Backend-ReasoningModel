from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta


VIMSOTTARI_ORDER = [
    "ketu",
    "venus",
    "sun",
    "moon",
    "mars",
    "rahu",
    "jupiter",
    "saturn",
    "mercury",
]

VIMSOTTARI_YEARS = {
    "ketu": 7,
    "venus": 20,
    "sun": 6,
    "moon": 10,
    "mars": 7,
    "rahu": 18,
    "jupiter": 16,
    "saturn": 19,
    "mercury": 17,
}

PLANET_DISPLAY = {
    "ketu": "Ketu",
    "venus": "Venus",
    "sun": "Sun",
    "moon": "Moon",
    "mars": "Mars",
    "rahu": "Rahu",
    "jupiter": "Jupiter",
    "saturn": "Saturn",
    "mercury": "Mercury",
}

YOGINI_ORDER = [
    "mangala",
    "pingala",
    "dhanya",
    "bhramari",
    "bhadrika",
    "ulka",
    "siddha",
    "sankata",
]

YOGINI_YEARS = {
    "mangala": 1,
    "pingala": 2,
    "dhanya": 3,
    "bhramari": 4,
    "bhadrika": 5,
    "ulka": 6,
    "siddha": 7,
    "sankata": 8,
}

YOGINI_DISPLAY = {
    "mangala": "Mangala",
    "pingala": "Pingala",
    "dhanya": "Dhanya",
    "bhramari": "Bhramari",
    "bhadrika": "Bhadrika",
    "ulka": "Ulka",
    "siddha": "Siddha",
    "sankata": "Sankata",
}


def _normalize_name(value: Any) -> str:
    if value is None:
        return ""

    name = str(value).strip().lower()

    aliases = {
        "raahu": "rahu",
        "ket": "ketu",
        "ven": "venus",
        "sukra": "venus",
        "shukra": "venus",
        "surya": "sun",
        "chandra": "moon",
        "mangal": "mars",
        "kuja": "mars",
        "guru": "jupiter",
        "jup": "jupiter",
        "sani": "saturn",
        "shani": "saturn",
        "sat": "saturn",
        "budha": "mercury",
        "merc": "mercury",
    }

    return aliases.get(name, name)


def _parse_date(value: Any) -> Optional[datetime]:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.replace(tzinfo=None)

    raw = str(value).strip()

    if not raw:
        return None

    cleaned = raw.replace("Z", "+00:00")

    try:
        parsed = datetime.fromisoformat(cleaned)
        return parsed.replace(tzinfo=None)
    except Exception:
        pass

    # Handles wrong-looking format like: 2004-08-20 14:07:18 PM
    upper_raw = raw.upper()
    if upper_raw.endswith(" AM") or upper_raw.endswith(" PM"):
        without_ampm = raw.rsplit(" ", 1)[0]

        try:
            return datetime.strptime(without_ampm, "%Y-%m-%d %H:%M:%S")
        except Exception:
            pass

        try:
            return datetime.strptime(raw, "%Y-%m-%d %I:%M:%S %p")
        except Exception:
            pass

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt)
        except Exception:
            continue

    return None


def _format_date(value: datetime) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S")


def _add_fractional_years(start_date: datetime, years: float) -> datetime:
    whole_years = int(years)
    months = round((years - whole_years) * 12)
    return start_date + relativedelta(years=whole_years, months=months)


def _get_dasha_order(dasha_type: str) -> List[str]:
    dasha_type = str(dasha_type).lower().strip()

    if dasha_type in ["vimshottari", "vimsottari", "tribhagi"]:
        return VIMSOTTARI_ORDER

    if dasha_type == "yogini":
        return YOGINI_ORDER

    return []


def _get_duration_years(dasha_type: str, name: str) -> Optional[float]:
    dasha_type = str(dasha_type).lower().strip()
    name = _normalize_name(name)

    if dasha_type in ["vimshottari", "vimsottari"]:
        return VIMSOTTARI_YEARS.get(name)

    if dasha_type == "tribhagi":
        years = VIMSOTTARI_YEARS.get(name)
        if years is None:
            return None
        return years / 3

    if dasha_type == "yogini":
        return YOGINI_YEARS.get(name)

    return None


def _get_maha_name(dasha_type: str, maha: Dict[str, Any]) -> str:
    dasha_type = str(dasha_type).lower().strip()

    if dasha_type == "yogini":
        return _normalize_name(
            maha.get("yogini")
            or maha.get("name")
            or maha.get("lord_planet")
            or maha.get("planet")
        )

    return _normalize_name(
        maha.get("planet")
        or maha.get("name")
        or maha.get("lord")
        or maha.get("dasha_lord")
    )


def _get_template_map(
    dasha_type: str,
    mahadashas: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    template_map: Dict[str, Dict[str, Any]] = {}

    for maha in mahadashas:
        name = _get_maha_name(dasha_type, maha)
        if name:
            template_map[name] = maha

    return template_map


def _build_major_node(
    dasha_type: str,
    name: str,
    start_dt: datetime,
    end_dt: datetime,
    template_map: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    template = template_map.get(name, {})

    if dasha_type == "yogini":
        return {
            "yogini": template.get("yogini") or YOGINI_DISPLAY.get(name, name.title()),
            "lord_planet_id": template.get("lord_planet_id"),
            "lord_planet": template.get("lord_planet"),
            "start": _format_date(start_dt),
            "end": _format_date(end_dt),
            "antardashas": [],
        }

    return {
        "planet_id": template.get("planet_id"),
        "planet": template.get("planet") or PLANET_DISPLAY.get(name, name.title()),
        "start": _format_date(start_dt),
        "end": _format_date(end_dt),
        "antardashas": [],
    }


def _split_period_by_ratio(
    start_dt: datetime,
    end_dt: datetime,
    ratio_values: List[float],
) -> List[tuple[datetime, datetime]]:
    total_seconds = (end_dt - start_dt).total_seconds()

    if total_seconds <= 0 or not ratio_values:
        return []

    total_ratio = sum(ratio_values)

    if total_ratio <= 0:
        return []

    periods = []
    current_start = start_dt

    for index, ratio in enumerate(ratio_values):
        if index == len(ratio_values) - 1:
            current_end = end_dt
        else:
            seconds = total_seconds * (ratio / total_ratio)
            current_end = current_start + timedelta(seconds=seconds)

        periods.append((current_start, current_end))
        current_start = current_end

    return periods


def _ordered_sequence_from(order: List[str], start_name: str) -> List[str]:
    if start_name not in order:
        return order

    start_index = order.index(start_name)
    return order[start_index:] + order[:start_index]


def _build_antardashas_for_new_major(
    dasha_type: str,
    major_name: str,
    major_start: datetime,
    major_end: datetime,
    template_map: Dict[str, Dict[str, Any]],
    level: int,
) -> List[Dict[str, Any]]:
    order = _get_dasha_order(dasha_type)

    if not order:
        return []

    sequence = _ordered_sequence_from(order, major_name)

    if dasha_type == "yogini":
        ratio_values = [YOGINI_YEARS[x] for x in sequence]
    else:
        ratio_values = [VIMSOTTARI_YEARS[x] for x in sequence]

    antardasha_ranges = _split_period_by_ratio(
        start_dt=major_start,
        end_dt=major_end,
        ratio_values=ratio_values,
    )

    antardashas = []

    for antara_name, (antara_start, antara_end) in zip(sequence, antardasha_ranges):
        template = template_map.get(antara_name, {})

        if dasha_type == "yogini":
            antara_node = {
                "yogini": template.get("yogini")
                or YOGINI_DISPLAY.get(antara_name, antara_name.title()),
                "lord_planet_id": template.get("lord_planet_id"),
                "lord_planet": template.get("lord_planet"),
                "start": _format_date(antara_start),
                "end": _format_date(antara_end),
            }
        else:
            antara_node = {
                "planet_id": template.get("planet_id"),
                "planet": template.get("planet")
                or PLANET_DISPLAY.get(antara_name, antara_name.title()),
                "start": _format_date(antara_start),
                "end": _format_date(antara_end),
            }

        # Only add pratyantardashas if frontend requested/uses level 3.
        if level >= 3 and dasha_type != "yogini":
            praty_sequence = _ordered_sequence_from(order, antara_name)
            praty_ratios = [VIMSOTTARI_YEARS[x] for x in praty_sequence]

            praty_ranges = _split_period_by_ratio(
                start_dt=antara_start,
                end_dt=antara_end,
                ratio_values=praty_ratios,
            )

            pratyantardashas = []

            for praty_name, (praty_start, praty_end) in zip(praty_sequence, praty_ranges):
                praty_template = template_map.get(praty_name, {})

                pratyantardashas.append(
                    {
                        "planet_id": praty_template.get("planet_id"),
                        "planet": praty_template.get("planet")
                        or PLANET_DISPLAY.get(praty_name, praty_name.title()),
                        "start": _format_date(praty_start),
                        "end": _format_date(praty_end),
                    }
                )

            antara_node["pratyantardashas"] = pratyantardashas

        antardashas.append(antara_node)

    return antardashas


def _repair_existing_period_end_dates(tree: Dict[str, Any]) -> Dict[str, Any]:
    """
    Repairs missing end dates for already returned periods.
    It does not change start dates or order.
    """

    mahadashas = tree.get("mahadashas", [])

    if not mahadashas:
        return tree

    mahadashas.sort(key=lambda x: _parse_date(x.get("start")) or datetime.max)

    for maha_index, maha in enumerate(mahadashas):
        maha_start = _parse_date(maha.get("start"))
        maha_end = _parse_date(maha.get("end"))

        if maha_start and maha_end is None:
            if maha_index + 1 < len(mahadashas):
                next_start = _parse_date(mahadashas[maha_index + 1].get("start"))
                if next_start:
                    maha["end"] = _format_date(next_start)

        antardashas = maha.get("antardashas", [])

        if antardashas:
            antardashas.sort(key=lambda x: _parse_date(x.get("start")) or datetime.max)

            for antara_index, antara in enumerate(antardashas):
                antara_start = _parse_date(antara.get("start"))
                antara_end = _parse_date(antara.get("end"))

                if antara_start and antara_end is None:
                    if antara_index + 1 < len(antardashas):
                        next_start = _parse_date(
                            antardashas[antara_index + 1].get("start")
                        )
                        if next_start:
                            antara["end"] = _format_date(next_start)
                    else:
                        parent_end = _parse_date(maha.get("end"))
                        if parent_end:
                            antara["end"] = _format_date(parent_end)

                pratyantardashas = antara.get("pratyantardashas", [])

                if pratyantardashas:
                    pratyantardashas.sort(
                        key=lambda x: _parse_date(x.get("start")) or datetime.max
                    )

                    for praty_index, praty in enumerate(pratyantardashas):
                        praty_start = _parse_date(praty.get("start"))
                        praty_end = _parse_date(praty.get("end"))

                        if praty_start and praty_end is None:
                            if praty_index + 1 < len(pratyantardashas):
                                next_start = _parse_date(
                                    pratyantardashas[praty_index + 1].get("start")
                                )
                                if next_start:
                                    praty["end"] = _format_date(next_start)
                            else:
                                parent_end = _parse_date(antara.get("end"))
                                if parent_end:
                                    praty["end"] = _format_date(parent_end)

    tree["mahadashas"] = mahadashas
    return tree


def extend_dasha_tree_for_old_births(
    tree: Dict[str, Any],
    dasha_type: str,
    years_ahead: int = 100,
) -> Dict[str, Any]:
    """
    Extends dasha tree for older birth dates.

    This function:
    - keeps your existing PyJHora output unchanged
    - fills missing end date of last returned mahadasha
    - appends future mahadashas using the same cycle order
    - preserves the same response shape
    - does not calculate current dasha
    """

    if not tree:
        return tree

    mahadashas = tree.get("mahadashas", [])

    if not mahadashas:
        return tree

    dasha_type = str(dasha_type).lower().strip()
    order = _get_dasha_order(dasha_type)

    if not order:
        return tree

    tree = _repair_existing_period_end_dates(tree)
    mahadashas = tree.get("mahadashas", [])

    mahadashas.sort(key=lambda x: _parse_date(x.get("start")) or datetime.max)

    level = int(tree.get("level", 1))
    template_map = _get_template_map(dasha_type, mahadashas)

    last_maha = mahadashas[-1]
    last_name = _get_maha_name(dasha_type, last_maha)
    last_start = _parse_date(last_maha.get("start"))
    last_end = _parse_date(last_maha.get("end"))

    if not last_name or last_name not in order or last_start is None:
        tree["mahadashas"] = mahadashas
        return tree

    # If last mahadasha still has no end, calculate it from duration.
    if last_end is None:
        last_duration = _get_duration_years(dasha_type, last_name)

        if last_duration is None:
            tree["mahadashas"] = mahadashas
            return tree

        last_end = _add_fractional_years(last_start, last_duration)
        last_maha["end"] = _format_date(last_end)

    target_date = datetime.now() + relativedelta(years=years_ahead)

    current_start = last_end
    next_index = (order.index(last_name) + 1) % len(order)

    while current_start <= target_date:
        next_name = order[next_index]
        duration_years = _get_duration_years(dasha_type, next_name)

        if duration_years is None:
            break

        current_end = _add_fractional_years(current_start, duration_years)

        new_maha = _build_major_node(
            dasha_type=dasha_type,
            name=next_name,
            start_dt=current_start,
            end_dt=current_end,
            template_map=template_map,
        )

        if level >= 2:
            new_maha["antardashas"] = _build_antardashas_for_new_major(
                dasha_type=dasha_type,
                major_name=next_name,
                major_start=current_start,
                major_end=current_end,
                template_map=template_map,
                level=level,
            )

        mahadashas.append(new_maha)

        current_start = current_end
        next_index = (next_index + 1) % len(order)

    tree["mahadashas"] = mahadashas
    return tree