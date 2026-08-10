from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud import recurring_transaction as recurring_crud
from app.db.session import get_db
from app.models import RecurringTransaction
from app.schemas.recurring_transaction import (
    RecurringTransactionCreate,
    RecurringTransactionListRead,
    RecurringTransactionRead,
    RecurringTransactionUpdate,
)

router = APIRouter()


def _get_recurring_or_404(db: Session, recurring_transaction_id: int) -> RecurringTransaction:
    recurring = recurring_crud.get_recurring_transaction(db, recurring_transaction_id)
    if recurring is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="定期取引が見つかりません"
        )
    return recurring


@router.get("/recurring-transactions", response_model=RecurringTransactionListRead)
def list_recurring_transactions(db: Session = Depends(get_db)) -> RecurringTransactionListRead:
    recurring_crud.generate_due_transactions(db)
    items = recurring_crud.get_recurring_transactions(db)
    return RecurringTransactionListRead(items=items)


@router.post(
    "/recurring-transactions",
    response_model=RecurringTransactionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_recurring_transaction(
    payload: RecurringTransactionCreate, db: Session = Depends(get_db)
) -> RecurringTransactionRead:
    try:
        return recurring_crud.create_recurring_transaction(
            db,
            name=payload.name,
            amount=payload.amount,
            entry_kind=payload.entry_kind,
            major_category_id=payload.major_category_id,
            expense_category_id=payload.expense_category_id,
            income_category_id=payload.income_category_id,
            asset_id=payload.asset_id,
            day_of_month=payload.day_of_month,
            memo=payload.memo,
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="指定された資産またはカテゴリが存在しません",
        ) from exc


@router.put(
    "/recurring-transactions/{recurring_transaction_id}", response_model=RecurringTransactionRead
)
def update_recurring_transaction(
    recurring_transaction_id: int,
    payload: RecurringTransactionUpdate,
    db: Session = Depends(get_db),
) -> RecurringTransactionRead:
    recurring = _get_recurring_or_404(db, recurring_transaction_id)
    try:
        return recurring_crud.update_recurring_transaction(
            db,
            recurring,
            name=payload.name,
            amount=payload.amount,
            entry_kind=payload.entry_kind,
            major_category_id=payload.major_category_id,
            expense_category_id=payload.expense_category_id,
            income_category_id=payload.income_category_id,
            asset_id=payload.asset_id,
            day_of_month=payload.day_of_month,
            memo=payload.memo,
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="指定された資産またはカテゴリが存在しません",
        ) from exc


@router.delete(
    "/recurring-transactions/{recurring_transaction_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_recurring_transaction(
    recurring_transaction_id: int, db: Session = Depends(get_db)
) -> None:
    recurring = _get_recurring_or_404(db, recurring_transaction_id)
    recurring_crud.delete_recurring_transaction(db, recurring)
