from datetime import date as date_type
from decimal import Decimal

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.crud.asset import apply_balance_delta
from app.models import Asset, Transaction


def _signed_amount(entry_kind: str, amount: Decimal) -> Decimal:
    return amount if entry_kind == "income" else -amount


def get_transactions_by_month(db: Session, year: int, month: int) -> list[Transaction]:
    stmt = (
        select(Transaction)
        .where(
            extract("year", Transaction.date) == year,
            extract("month", Transaction.date) == month,
        )
        .order_by(Transaction.date.desc(), Transaction.id.desc())
    )
    return list(db.scalars(stmt).all())


def get_transaction(db: Session, transaction_id: int) -> Transaction | None:
    return db.get(Transaction, transaction_id)


def create_transaction(
    db: Session,
    asset: Asset,
    date: date_type,
    amount: Decimal,
    entry_kind: str,
    major_category_id: int | None,
    expense_category_id: int | None,
    income_category_id: int | None,
    memo: str | None,
) -> Transaction:
    transaction = Transaction(
        date=date,
        amount=amount,
        entry_kind=entry_kind,
        entry_type="normal",
        major_category_id=major_category_id,
        expense_category_id=expense_category_id,
        income_category_id=income_category_id,
        asset_id=asset.id,
        memo=memo,
    )
    db.add(transaction)
    apply_balance_delta(db, asset, _signed_amount(entry_kind, amount))
    db.commit()
    db.refresh(transaction)
    return transaction


def update_transaction(
    db: Session,
    transaction: Transaction,
    asset: Asset,
    date: date_type,
    amount: Decimal,
    entry_kind: str,
    major_category_id: int | None,
    expense_category_id: int | None,
    income_category_id: int | None,
    memo: str | None,
) -> Transaction:
    old_asset = db.get(Asset, transaction.asset_id)
    if old_asset is not None:
        apply_balance_delta(
            db, old_asset, -_signed_amount(transaction.entry_kind, transaction.amount)
        )

    transaction.date = date
    transaction.amount = amount
    transaction.entry_kind = entry_kind
    transaction.major_category_id = major_category_id
    transaction.expense_category_id = expense_category_id
    transaction.income_category_id = income_category_id
    transaction.asset_id = asset.id
    transaction.memo = memo

    apply_balance_delta(db, asset, _signed_amount(entry_kind, amount))
    db.commit()
    db.refresh(transaction)
    return transaction


def delete_transaction(db: Session, transaction: Transaction) -> None:
    asset = db.get(Asset, transaction.asset_id)
    if asset is not None:
        apply_balance_delta(db, asset, -_signed_amount(transaction.entry_kind, transaction.amount))
    db.delete(transaction)
    db.commit()


def get_monthly_summary(db: Session, year: int, month: int) -> dict[str, Decimal]:
    stmt = (
        select(Transaction.entry_kind, func.coalesce(func.sum(Transaction.amount), 0))
        .where(
            extract("year", Transaction.date) == year,
            extract("month", Transaction.date) == month,
        )
        .group_by(Transaction.entry_kind)
    )
    totals = dict(db.execute(stmt).all())
    income_total = Decimal(totals.get("income", 0))
    expense_total = Decimal(totals.get("expense", 0))
    return {
        "income_total": income_total,
        "expense_total": expense_total,
        "balance": income_total - expense_total,
    }
