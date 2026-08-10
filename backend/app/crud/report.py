import calendar
from datetime import date as date_type
from decimal import Decimal

from sqlalchemy import case, extract, func, select
from sqlalchemy.orm import Session

from app.crud.asset import get_total_balance
from app.models import MajorCategory, Transaction


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


def _signed_amount_after(db: Session, cutoff: date_type) -> Decimal:
    signed = case(
        (Transaction.entry_kind == "income", Transaction.amount),
        else_=-Transaction.amount,
    )
    stmt = select(func.coalesce(func.sum(signed), 0)).where(Transaction.date > cutoff)
    return Decimal(db.scalar(stmt) or 0)


def get_asset_trend(db: Session, months: int) -> list[dict]:
    today = date_type.today()
    total_now = get_total_balance(db)

    points: list[dict] = []
    for offset in range(months - 1, -1, -1):
        year = today.year
        month = today.month - offset
        while month <= 0:
            month += 12
            year -= 1

        if offset == 0:
            point_date = today
        else:
            last_day = calendar.monthrange(year, month)[1]
            point_date = date_type(year, month, last_day)

        total_balance = total_now - _signed_amount_after(db, point_date)
        points.append({"date": point_date, "total_balance": total_balance})

    return points
