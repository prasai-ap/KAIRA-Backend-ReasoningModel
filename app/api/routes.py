from fastapi import APIRouter, HTTPException

from app.models.birth import BirthInput

from app.utils.helpers import (
    jd_from_birth,
    place_to_obj,
    place_to_tuple,
    set_ayanamsa_mode_safe
)

from app.services.chart_service import compute_chart
from app.services.summary_service import compute_summary_card_en
from app.services.dasha_service import (
    compute_vimshottari,
    compute_tribhagi,
    compute_yogini
)
from app.services.yoga_service import compute_yogas_d1
from app.services.dosha_service import compute_doshas_d1

router = APIRouter()

