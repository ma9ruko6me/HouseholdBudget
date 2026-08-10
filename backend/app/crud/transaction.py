from datetime import date as date_type
from decimal import Decimal

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.crud.asset import apply_balance_delta
from app.models import Asset, Transaction


def _signed_amount(entry_kind: str, amount: Decimal) -> Decimal:
    return amount if entry_kind == "income" else -amount


def _apply_effect(
    db: Session,
    asset: Asset,
    entry_kind: str,
    amount: Decimal,
    transfer_to_asset: Asset | None,
) -> None:
    apply_balance_delta(db, asset, _signed_amount(entry_kind, amount))
    if entry_kind == "transfer" and transfer_to_asset is not None:
        apply_balance_delta(db, transfer_to_asset, amount)


def _revert_effect(
    db: Session,
    asset: Asset,
    entry_kind: str,
    amount: Decimal,
    transfer_to_asset: Asset | None,
) -> None:
    apply_balance_delta(db, asset, -_signed_amount(entry_kind, amount))
    if entry_kind == "transfer" and transfer_to_asset is not None:
        apply_balance_delta(db, transfer_to_asset, -amount)


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
    transfer_to_asset: Asset | None = None,
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
        transfer_to_asset_id=transfer_to_asset.id if transfer_to_asset else None,
        memo=memo,
    )
    db.add(transaction)
    _apply_effect(db, asset, entry_kind, amount, transfer_to_asset)
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
    transfer_to_asset: Asset | None = None,
) -> Transaction:
    old_asset = db.get(Asset, transaction.asset_id)
    old_transfer_to_asset = (
        db.get(Asset, transaction.transfer_to_asset_id)
        if transaction.transfer_to_asset_id is not None
        else None
    )
    if old_asset is not None:
        _revert_effect(
            db, old_asset, transaction.entry_kind, transaction.amount, old_transfer_to_asset
        )

    transaction.date = date
    transaction.amount = amount
    transaction.entry_kind = entry_kind
    transaction.major_category_id = major_category_id
    transaction.expense_category_id = expense_category_id
    transaction.income_category_id = income_category_id
    transaction.asset_id = asset.id
    transaction.transfer_to_asset_id = transfer_to_asset.id if transfer_to_asset else None
    transaction.memo = memo

    _apply_effect(db, asset, entry_kind, amount, transfer_to_asset)
    db.commit()
    db.refresh(transaction)
    return transaction


def delete_transaction(db: Session, transaction: Transaction) -> None:
    asset = db.get(Asset, transaction.asset_id)
    transfer_to_asset = (
        db.get(Asset, transaction.transfer_to_asset_id)
        if transaction.transfer_to_asset_id is not None
        else None
    )
    if asset is not None:
        _revert_effect(db, asset, transaction.entry_kind, transaction.amount, transfer_to_asset)
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
