from jhora import const

RASI_INDEX_TO_NAME = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

PLANET_ID_TO_NAME = {
    const._ascendant_symbol: "Lagna",
    0: "Sun",
    1: "Moon",
    2: "Mars",
    3: "Mercury",
    4: "Jupiter",
    5: "Venus",
    6: "Saturn",
    7: "Rahu",
    8: "Ketu",
}

DASHA_PLANET_ID_TO_NAME = {
    0: "Sun",
    1: "Moon",
    2: "Mars",
    3: "Mercury",
    4: "Jupiter",
    5: "Venus",
    6: "Saturn",
    7: "Rahu",
    8: "Ketu",
}


YOGINI_ORDERED = [
    {"yogini": "Mangala", "lord_planet_id": 1},   
    {"yogini": "Pingala", "lord_planet_id": 0},   
    {"yogini": "Dhanya", "lord_planet_id": 4},    
    {"yogini": "Bhramari", "lord_planet_id": 2},  
    {"yogini": "Bhadrika", "lord_planet_id": 3},  
    {"yogini": "Ulka", "lord_planet_id": 6},      
    {"yogini": "Siddha", "lord_planet_id": 5},    
    {"yogini": "Sankata", "lord_planet_id": 7},   
]
YOGINI_LORD_ID_TO_YOGINI_NAME = {x["lord_planet_id"]: x["yogini"] for x in YOGINI_ORDERED}


def _planet_name(pid: int) -> str:
    return DASHA_PLANET_ID_TO_NAME.get(int(pid), str(pid))


def _yogini_name_from_lord_id(pid: int) -> str:
    return YOGINI_LORD_ID_TO_YOGINI_NAME.get(int(pid), _planet_name(int(pid)))
