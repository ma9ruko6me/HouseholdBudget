"""set null on delete for category fk

Revision ID: a6fa4e94ddb0
Revises: bfca510ab01f
Create Date: 2026-08-10 09:10:54.666360

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a6fa4e94ddb0"
down_revision: Union[str, Sequence[str], None] = "bfca510ab01f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        op.f("recurring_transactions_ibfk_2"), "recurring_transactions", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("recurring_transactions_ibfk_3"), "recurring_transactions", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_recurring_transactions_expense_category_id",
        "recurring_transactions",
        "expense_categories",
        ["expense_category_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_recurring_transactions_income_category_id",
        "recurring_transactions",
        "income_categories",
        ["income_category_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.drop_constraint(op.f("transactions_ibfk_2"), "transactions", type_="foreignkey")
    op.drop_constraint(op.f("transactions_ibfk_3"), "transactions", type_="foreignkey")
    op.create_foreign_key(
        "fk_transactions_expense_category_id",
        "transactions",
        "expense_categories",
        ["expense_category_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_transactions_income_category_id",
        "transactions",
        "income_categories",
        ["income_category_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_transactions_income_category_id", "transactions", type_="foreignkey")
    op.drop_constraint("fk_transactions_expense_category_id", "transactions", type_="foreignkey")
    op.create_foreign_key(
        op.f("transactions_ibfk_3"),
        "transactions",
        "income_categories",
        ["income_category_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("transactions_ibfk_2"),
        "transactions",
        "expense_categories",
        ["expense_category_id"],
        ["id"],
    )
    op.drop_constraint(
        "fk_recurring_transactions_income_category_id",
        "recurring_transactions",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_recurring_transactions_expense_category_id",
        "recurring_transactions",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("recurring_transactions_ibfk_3"),
        "recurring_transactions",
        "income_categories",
        ["income_category_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("recurring_transactions_ibfk_2"),
        "recurring_transactions",
        "expense_categories",
        ["expense_category_id"],
        ["id"],
    )
