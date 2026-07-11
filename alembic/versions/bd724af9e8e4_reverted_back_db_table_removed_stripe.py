"""reverted back db table removed stripe

Revision ID: bd724af9e8e4
Revises: 28d85d4650cf
Create Date: 2026-07-11 12:57:52.440289

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd724af9e8e4'
down_revision: Union[str, Sequence[str], None] = '28d85d4650cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        "payment_transactions",
        "payment_status",
        new_column_name="status",
    )

    op.drop_index(
        "ix_payment_transactions_stripe_checkout_session_id",
        table_name="payment_transactions",
    )

    op.drop_column("payment_transactions", "stripe_payment_intent_id")
    op.drop_column("payment_transactions", "stripe_checkout_session_id")
    op.drop_column("payment_transactions", "currency")


def downgrade():
    op.alter_column(
        "payment_transactions",
        "status",
        new_column_name="payment_status",
    )

    op.add_column(
        "payment_transactions",
        sa.Column("currency", sa.String(), nullable=False, server_default="NPR"),
    )

    op.add_column(
        "payment_transactions",
        sa.Column("stripe_checkout_session_id", sa.String(), nullable=True),
    )

    op.add_column(
        "payment_transactions",
        sa.Column("stripe_payment_intent_id", sa.String(), nullable=True),
    )

    op.create_index(
        "ix_payment_transactions_stripe_checkout_session_id",
        "payment_transactions",
        ["stripe_checkout_session_id"],
        unique=True,
    )