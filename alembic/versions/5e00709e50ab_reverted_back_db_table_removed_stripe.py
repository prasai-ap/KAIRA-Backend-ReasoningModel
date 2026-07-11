"""reverted back db table removed stripe

Revision ID: 5e00709e50ab
Revises: bd724af9e8e4
Create Date: 2026-07-11 13:02:22.318743

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e00709e50ab'
down_revision: Union[str, Sequence[str], None] = 'bd724af9e8e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
