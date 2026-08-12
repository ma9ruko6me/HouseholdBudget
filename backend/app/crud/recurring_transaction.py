import calendar
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.asset import apply_balance_delta
from app.crud.transaction import _signed_amount
from app.models import Asset, RecurringTransaction, Transaction


def get_recurring_transactions(db: Session) -> list[RecurringTransaction]:
    stmt = select(RecurringTransaction).order_by(RecurringTransaction.id)
    return list(db.scalars(stmt).all())


def get_recurring_transaction(
    db: Session, recurring_transaction_id: int
) -> RecurringTransaction | None:
    return db.get(RecurringTransaction, recurring_transaction_id)


def create_recurring_transaction(
    db: Session,
    amount: Decimal,
    entry_kind: str,
    major_category_id: int | None,
    expense_category_id: int | None,
    income_category_id: int | None,
    asset_id: int,
    day_of_month: int,
    memo: str | None,
) -> RecurringTransaction:
    recurring = RecurringTransaction(
        amount=amount,
        entry_kind=entry_kind,
        major_category_id=major_category_id,
        expense_category_id=expense_category_id,
        income_category_id=income_category_id,
        asset_id=asset_id,
        day_of_month=day_of_month,
        memo=memo,
    )
    db.add(recurring)
    db.commit()
    db.refresh(recurring)
    return recurring


def update_recurring_transaction(
    db: Session,
    recurring: RecurringTransaction,
    amount: Decimal,
    entry_kind: str,
    major_category_id: int | None,
    expense_category_id: int | None,
    income_category_id: int | None,
    asset_id: int,
    day_of_month: int,
    memo: str | None,
) -> RecurringTransaction:
    recurring.amount = amount
    recurring.entry_kind = entry_kind
    recurring.major_category_id = major_category_id
    recurring.expense_category_id = expense_category_id
    recurring.income_category_id = income_category_id
    recurring.asset_id = asset_id
    recurring.day_of_month = day_of_month
    recurring.memo = memo
    db.commit()
    db.refresh(recurring)
    return recurring


def delete_recurring_transaction(db: Session, recurring: RecurringTransaction) -> None:
    db.delete(recurring)
    db.commit()


def _next_month(year: int, month: int) -> tuple[int, int]:
    if month == 12:
        return year + 1, 1
    return year, month + 1


def _target_date(year: int, month: int, day_of_month: int) -> date:
    last_day_of_month = calendar.monthrange(year, month)[1]
    return date(year, month, min(day_of_month, last_day_of_month))


def generate_due_transactions(db: Session, today: date | None = None) -> None:
    today = today or date.today()
    recurring_list = db.scalars(select(RecurringTransaction)).all()

    for recurring in recurring_list:
        if recurring.last_generated_date is None:
            year, month = recurring.created_at.year, recurring.created_at.month
        else:
            year, month = _next_month(
                recurring.last_generated_date.year, recurring.last_generated_date.month
            )

        while True:
            target = _target_date(year, month, recurring.day_of_month)
            if target > today:
                break

            asset = db.get(Asset, recurring.asset_id)
            if asset is not None:
                transaction = Transaction(
                    date=target,
                    amount=recurring.amount,
                    entry_kind=recurring.entry_kind,
                    entry_type="normal",
                    major_category_id=recurring.major_category_id,
                    expense_category_id=recurring.expense_category_id,
                    income_category_id=recurring.income_category_id,
                    asset_id=recurring.asset_id,
                    memo=recurring.memo,
                )
                db.add(transaction)
                apply_balance_delta(
                    db, asset, _signed_amount(recurring.entry_kind, recurring.amount)
                )

            recurring.last_generated_date = target
            year, month = _next_month(year, month)

    db.commit()
