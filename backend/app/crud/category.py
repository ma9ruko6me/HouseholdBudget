from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ExpenseCategory, IncomeCategory, MajorCategory


def get_major_categories(db: Session) -> list[MajorCategory]:
    stmt = select(MajorCategory).order_by(MajorCategory.sort_order)
    return list(db.scalars(stmt).all())


def get_expense_categories(db: Session) -> list[ExpenseCategory]:
    stmt = select(ExpenseCategory).order_by(ExpenseCategory.sort_order)
    return list(db.scalars(stmt).all())


def create_expense_category(db: Session, major_category_id: int, name: str) -> ExpenseCategory:
    stmt = select(func.max(ExpenseCategory.sort_order)).where(
        ExpenseCategory.major_category_id == major_category_id
    )
    next_sort_order = (db.scalar(stmt) or 0) + 1
    category = ExpenseCategory(
        major_category_id=major_category_id, name=name, sort_order=next_sort_order
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_expense_category(db: Session, category_id: int) -> ExpenseCategory | None:
    return db.get(ExpenseCategory, category_id)


def delete_expense_category(db: Session, category: ExpenseCategory) -> None:
    db.delete(category)
    db.commit()


def get_income_categories(db: Session) -> list[IncomeCategory]:
    stmt = select(IncomeCategory).order_by(IncomeCategory.sort_order)
    return list(db.scalars(stmt).all())


def create_income_category(db: Session, name: str) -> IncomeCategory:
    next_sort_order = (db.scalar(select(func.max(IncomeCategory.sort_order))) or 0) + 1
    category = IncomeCategory(name=name, sort_order=next_sort_order)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_income_category(db: Session, category_id: int) -> IncomeCategory | None:
    return db.get(IncomeCategory, category_id)


def delete_income_category(db: Session, category: IncomeCategory) -> None:
    db.delete(category)
    db.commit()
