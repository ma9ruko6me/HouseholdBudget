"""drop name from recurring_transactions

Revision ID: aeddaf0c1ecc
Revises: 4570cd537752
Create Date: 2026-08-12 14:23:22.191005

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'aeddaf0c1ecc'
down_revision: Union[str, Sequence[str], None] = '4570cd537752'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('recurring_transactions', 'name')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('recurring_transactions', sa.Column('name', mysql.VARCHAR(length=50), nullable=False))
