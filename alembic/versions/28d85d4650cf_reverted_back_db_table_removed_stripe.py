"""reverted back db table removed stripe

Revision ID: 28d85d4650cf
Revises: 8707ee9bd2a5
Create Date: 2026-07-11 12:47:33.047389

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28d85d4650cf'
down_revision: Union[str, Sequence[str], None] = '8707ee9bd2a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
