import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    package_name = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)

    transaction_uuid = Column(String, unique=True, index=True, nullable=False)
    transaction_code = Column(String, nullable=True)

    payment_method = Column(String, default="ESEWA")
    status = Column(String, default="PENDING")

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    paid_at = Column(DateTime(timezone=True), nullable=True)
    invoice_number = Column(String, nullable=True)
    invoice_sent_at = Column(DateTime(timezone=True), nullable=True)

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    plan_name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)

    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)

    is_active = Column(Boolean, default=True)

    payment_id = Column(UUID(as_uuid=True), ForeignKey("payment_transactions.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expiry_reminder_sent_at = Column(DateTime(timezone=True), nullable=True)
    expired_email_sent_at = Column(DateTime(timezone=True), nullable=True)