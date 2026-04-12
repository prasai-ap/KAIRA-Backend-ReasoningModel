from jhora import const
from jhora.panchanga import drik

from app.core.config import AYANAMSA_MODE


def validate_jd(jd: float):
    if jd < 625000.5 or jd > 2818000.5:
        raise ValueError("Invalid JD")


def set_ayanamsa_mode_safe(jd: float):
    validate_jd(jd)

    mode = AYANAMSA_MODE.upper()
    available = {k.upper() for k in const.available_ayanamsa_modes.keys()}

    if mode not in available:
        raise RuntimeError("Invalid ayanamsa")

    drik.set_ayanamsa_mode(mode, jd=jd)