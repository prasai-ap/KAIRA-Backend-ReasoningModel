from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.user_astrology_models import UserAstrologyData


def get_user_astrology(db: Session, user_id):
    return (
        db.query(UserAstrologyData)
        .filter(UserAstrologyData.user_id == user_id)
        .first()
    )


def create_user_astrology(
    db: Session,
    user_id,
    input_data,
    charts,
    dasha,
    yoga,
    dosha,
):
    obj = UserAstrologyData(
        user_id=user_id,
        input_data=input_data,
        charts=charts,
        dasha=dasha,
        yoga=yoga,
        dosha=dosha,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_user_astrology(
    db: Session,
    obj: UserAstrologyData,
    input_data,
    charts,
    dasha,
    yoga,
    dosha,
):
    obj.input_data = input_data
    obj.charts = charts
    obj.dasha = dasha
    obj.yoga = yoga
    obj.dosha = dosha
    obj.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(obj)
    return obj