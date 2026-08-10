from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, Date, DateTime, Enum, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

EntryKind = Enum("income", "expense", "transfer", name="entry_kind")
EntryType = Enum("normal", "adjustment", name="entry_type")


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (Index("ix_transactions_date", "date"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 0), nullable=False)
    entry_kind: Mapped[str] = mapped_column(EntryKind, nullable=False)
    entry_type: Mapped[str] = mapped_column(EntryType, nullable=False, default="normal")
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
    transfer_to_asset_id: Mapped[int | None] = mapped_column(ForeignKey("assets.id"), nullable=True)
    memo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
