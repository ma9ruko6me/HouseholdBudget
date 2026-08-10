from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.transaction import EntryKind


class RecurringTransaction(Base):
    __tablename__ = "recurring_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 0), nullable=False)
    entry_kind: Mapped[str] = mapped_column(EntryKind, nullable=False)
    major_category_id: Mapped[int | None] = mapped_column(
        ForeignKey("major_categories.id"), nullable=True
    )
    expense_category_id: Mapped[int | None] = mapped_column(
        ForeignKey("expense_categories.id", ondelete="SET NULL"), nullable=True
    )
    income_category_id: Mapped[int | None] = mapped_column(
        ForeignKey("income_categories.id", ondelete="SET NULL"), nullable=True
    )
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False)
    day_of_month: Mapped[int] = mapped_column(nullable=False)
    memo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
