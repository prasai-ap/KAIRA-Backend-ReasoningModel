"""reverted back db table for proper functioning

Revision ID: 4cba9eb2e313
Revises: 5e00709e50ab
Create Date: 2026-07-11 21:45:24.511649

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4cba9eb2e313'
down_revision: Union[str, Sequence[str], None] = '5e00709e50ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
