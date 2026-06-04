from jhora import const

AYANAMSA_MODE = "LAHIRI"


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

YOGINI_LORD_ID_TO_YOGINI_NAME = {
    x["lord_planet_id"]: x["yogini"] for x in YOGINI_ORDERED
}

WEEKDAY_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

NAKSHATRA_EN = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra", "Punarvasu",
    "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra",
    "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

TITHI_NAMES_SHUKLA = [
    "Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
]
TITHI_NAMES_KRISHNA = [
    "Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya",
]
NAKSHATRA_GANA_MAP = {
    1: "Deva",        # Ashwini
    2: "Manushya",    # Bharani
    3: "Rakshasa",    # Krittika
    4: "Manushya",    # Rohini
    5: "Deva",        # Mrigashira
    6: "Manushya",    # Ardra
    7: "Deva",        # Punarvasu
    8: "Deva",        # Pushya
    9: "Rakshasa",    # Ashlesha
    10: "Rakshasa",   # Magha
    11: "Manushya",   # Purva Phalguni
    12: "Manushya",   # Uttara Phalguni
    13: "Deva",       # Hasta
    14: "Rakshasa",   # Chitra
    15: "Deva",       # Swati
    16: "Rakshasa",   # Vishakha
    17: "Deva",       # Anuradha
    18: "Rakshasa",   # Jyeshtha
    19: "Rakshasa",   # Mula
    20: "Manushya",   # Purva Ashadha
    21: "Manushya",   # Uttara Ashadha
    22: "Deva",       # Shravana
    23: "Rakshasa",   # Dhanishta
    24: "Rakshasa",   # Shatabhisha
    25: "Manushya",   # Purva Bhadrapada
    26: "Manushya",   # Uttara Bhadrapada
    27: "Deva",       # Revati
}
NAKSHATRA_NADI_MAP = {
    1: "Adi",       # Ashwini
    2: "Madhya",    # Bharani
    3: "Antya",     # Krittika
    4: "Antya",     # Rohini
    5: "Madhya",    # Mrigashira
    6: "Adi",       # Ardra
    7: "Adi",       # Punarvasu
    8: "Madhya",    # Pushya
    9: "Antya",     # Ashlesha
    10: "Antya",    # Magha
    11: "Madhya",   # Purva Phalguni
    12: "Adi",      # Uttara Phalguni
    13: "Adi",      # Hasta
    14: "Madhya",   # Chitra
    15: "Antya",    # Swati
    16: "Antya",    # Vishakha
    17: "Madhya",   # Anuradha
    18: "Adi",      # Jyeshtha
    19: "Adi",      # Mula
    20: "Madhya",   # Purva Ashadha
    21: "Antya",    # Uttara Ashadha
    22: "Antya",    # Shravana
    23: "Madhya",   # Dhanishta
    24: "Adi",      # Shatabhisha
    25: "Adi",      # Purva Bhadrapada
    26: "Madhya",   # Uttara Bhadrapada
    27: "Antya",    # Revati
}