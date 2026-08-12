import calendar
from datetime import date as date_type
from datetime import timedelta
from decimal import Decimal

from sqlalchemy import case, extract, func, select
from sqlalchemy.orm import Session

from app.crud.asset import get_total_balance
from app.models import MajorCategory, Transaction

TREND_PERIOD_MONTHS = {"3m": 3, "6m": 6, "1y": 12}


def get_category_breakdown(db: Session, year: int, month: int) -> list[dict]:
    stmt = (
        select(
            MajorCategory.id,
            MajorCategory.name,
            func.sum(Transaction.amount),
        )
        .join(Transaction, Transaction.major_category_id == MajorCategory.id)
        .where(
            Transaction.entry_kind == "expense",
            extract("year", Transaction.date) == year,
            extract("month", Transaction.date) == month,
        )
        .group_by(MajorCategory.id, MajorCategory.name, MajorCategory.sort_order)
        .order_by(MajorCategory.sort_order)
    )
    return [
        {"major_category_id": row[0], "major_category_name": row[1], "amount": row[2]}
        for row in db.execute(stmt).all()
    ]


def _months_before(target: date_type, months: int) -> date_type:
    month = target.month - months
    year = target.year
    while month <= 0:
        month += 12
        year -= 1
    last_day = calendar.monthrange(year, month)[1]
    return date_type(year, month, min(target.day, last_day))


def _daily_signed_amounts(db: Session, start_date: date_type, end_date: date_type) -> dict:
    signed = case(
        (Transaction.entry_kind == "income", Transaction.amount),
        else_=-Transaction.amount,
    )
    stmt = (
        select(Transaction.date, func.sum(signed))
        .where(Transaction.date > start_date, Transaction.date <= end_date)
        .group_by(Transaction.date)
    )
    return {row[0]: Decimal(row[1]) for row in db.execute(stmt).all()}


def get_asset_trend(db: Session, period: str) -> list[dict]:
    today = date_type.today()
    total_now = get_total_balance(db)

    if period == "all":
        earliest = db.scalar(select(func.min(Transaction.date)))
        start_date = earliest if earliest is not None else today
    else:
        start_date = _months_before(today, TREND_PERIOD_MONTHS[period])

    deltas = _daily_signed_amounts(db, start_date, today)

    points: list[dict] = []
    running_balance = total_now
    current_date = today
    while current_date >= start_date:
        points.append({"date": current_date, "total_balance": running_balance})
        running_balance -= deltas.get(current_date, Decimal(0))
        current_date -= timedelta(days=1)

    points.reverse()
    return points
