import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class UserAstrologyData(Base):
    __tablename__ = "user_astrology_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)

    input_data = Column(JSON, nullable=False)

    charts = Column(JSON, nullable=False)
    dasha = Column(JSON, nullable=False)
    yoga = Column(JSON, nullable=False)
    dosha = Column(JSON, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)