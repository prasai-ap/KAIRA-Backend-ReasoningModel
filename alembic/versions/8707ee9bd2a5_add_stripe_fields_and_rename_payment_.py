"""add stripe fields and rename payment status

Revision ID: 8707ee9bd2a5
Revises: fbbde8450b86
Create Date: 2026-07-11 12:12:30.141418

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8707ee9bd2a5'
down_revision: Union[str, Sequence[str], None] = 'fbbde8450b86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
