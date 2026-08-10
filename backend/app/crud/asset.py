from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Asset, RecurringTransaction, Transaction


def get_assets(db: Session) -> list[Asset]:
    stmt = select(Asset).order_by(Asset.sort_order)
    return list(db.scalars(stmt).all())


def get_total_balance(db: Session) -> Decimal:
    return db.scalar(select(func.coalesce(func.sum(Asset.balance), 0))) or Decimal(0)


def create_asset(db: Session, name: str, type_: str, balance: Decimal) -> Asset:
    next_sort_order = (db.scalar(select(func.max(Asset.sort_order))) or 0) + 1
    asset = Asset(name=name, type=type_, balance=balance, sort_order=next_sort_order)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def get_asset(db: Session, asset_id: int) -> Asset | None:
    return db.get(Asset, asset_id)


def update_asset(db: Session, asset: Asset, name: str, type_: str) -> Asset:
    asset.name = name
    asset.type = type_
    db.commit()
    db.refresh(asset)
    return asset


def is_asset_referenced(db: Session, asset_id: int) -> bool:
    in_transactions = db.scalar(
        select(Transaction.id).where(Transaction.asset_id == asset_id).limit(1)
    )
    if in_transactions is not None:
        return True
    in_recurring = db.scalar(
        select(RecurringTransaction.id).where(RecurringTransaction.asset_id == asset_id).limit(1)
    )
    return in_recurring is not None


def delete_asset(db: Session, asset: Asset) -> None:
    db.delete(asset)
    db.commit()


def apply_balance_delta(db: Session, asset: Asset, delta: Decimal) -> None:
    asset.balance = asset.balance + delta
    db.flush()


def adjust_asset_balance(db: Session, asset: Asset, actual_balance: Decimal) -> Transaction | None:
    diff = actual_balance - asset.balance
    if diff == 0:
        return None

    transaction = Transaction(
        date=date.today(),
        amount=abs(diff),
        entry_kind="income" if diff > 0 else "expense",
        entry_type="adjustment",
        asset_id=asset.id,
    )
    db.add(transaction)
    asset.balance = actual_balance
    db.commit()
    db.refresh(asset)
    db.refresh(transaction)
    return transaction
