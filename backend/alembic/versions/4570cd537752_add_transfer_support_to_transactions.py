"""add transfer support to transactions

Revision ID: 4570cd537752
Revises: 9aec0a4c7332
Create Date: 2026-08-10 14:51:05.622270

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4570cd537752"
down_revision: Union[str, Sequence[str], None] = "9aec0a4c7332"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "transactions",
        "entry_kind",
        existing_type=sa.Enum("income", "expense", name="entry_kind"),
        type_=sa.Enum("income", "expense", "transfer", name="entry_kind"),
        existing_nullable=False,
    )
    op.add_column(
        "transactions", sa.Column("transfer_to_asset_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        "fk_transactions_transfer_to_asset_id",
        "transactions",
        "assets",
        ["transfer_to_asset_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_transactions_transfer_to_asset_id", "transactions", type_="foreignkey"
    )
    op.drop_column("transactions", "transfer_to_asset_id")
    op.alter_column(
        "transactions",
        "entry_kind",
        existing_type=sa.Enum("income", "expense", "transfer", name="entry_kind"),
        type_=sa.Enum("income", "expense", name="entry_kind"),
        existing_nullable=False,
    )
