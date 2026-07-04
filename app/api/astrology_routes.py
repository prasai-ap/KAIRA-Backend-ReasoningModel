from fastapi import APIRouter, Depends, HTTPException ,Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas.astrology_schemas import BirthInput
from app.services.user_astrology_service import (
    generate_or_get_user_astrology,
    get_saved_user_astrology,
    regenerate_user_astrology,
)
from app.core.rate_limit import limiter, ASTROLOGY_RATE_LIMIT

router = APIRouter(prefix="/astrology", tags=["astrology"])


@router.post("/generate")
@limiter.limit(ASTROLOGY_RATE_LIMIT)
def generate_astrology(
    request: Request,
    data: BirthInput,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return generate_or_get_user_astrology(db, user, data)


@router.get("/me")
def get_my_astrology(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    result = get_saved_user_astrology(db, user)
    if not result:
        raise HTTPException(status_code=404, detail="No saved astrology data found for user")
    return result


@router.post("/regenerate")
@limiter.limit(ASTROLOGY_RATE_LIMIT)
def regenerate_astrology(
    request: Request,
    data: BirthInput,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return regenerate_user_astrology(db, user, data)