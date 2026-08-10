from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud import asset as asset_crud
from app.crud import recurring_transaction as recurring_transaction_crud
from app.crud import transaction as transaction_crud
from app.db.session import get_db
from app.models import Asset, Transaction
from app.schemas.transaction import (
    MonthlySummary,
    TransactionCreate,
    TransactionListRead,
    TransactionRead,
    TransactionUpdate,
)

router = APIRouter()


def _get_asset_or_400(db: Session, asset_id: int) -> Asset:
    asset = asset_crud.get_asset(db, asset_id)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="指定された資産が存在しません"
        )
    return asset


def _get_transaction_or_404(db: Session, transaction_id: int) -> Transaction:
    transaction = transaction_crud.get_transaction(db, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="取引が見つかりません")
    return transaction


@router.get("/transactions", response_model=TransactionListRead)
def list_transactions(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
) -> TransactionListRead:
    recurring_transaction_crud.generate_due_transactions(db)
    items = transaction_crud.get_transactions_by_month(db, year, month)
    return TransactionListRead(items=items)


@router.post("/transactions", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate, db: Session = Depends(get_db)
) -> TransactionRead:
    asset = _get_asset_or_400(db, payload.asset_id)
    transfer_to_asset = (
        _get_asset_or_400(db, payload.transfer_to_asset_id)
        if payload.transfer_to_asset_id is not None
        else None
    )
    try:
        return transaction_crud.create_transaction(
            db,
            asset=asset,
            date=payload.date,
            amount=payload.amount,
            entry_kind=payload.entry_kind,
            major_category_id=payload.major_category_id,
            expense_category_id=payload.expense_category_id,
            income_category_id=payload.income_category_id,
            memo=payload.memo,
            transfer_to_asset=transfer_to_asset,
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="指定されたカテゴリが存在しません",
        ) from exc


@router.put("/transactions/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int, payload: TransactionUpdate, db: Session = Depends(get_db)
) -> TransactionRead:
    transaction = _get_transaction_or_404(db, transaction_id)
    asset = _get_asset_or_400(db, payload.asset_id)
    transfer_to_asset = (
        _get_asset_or_400(db, payload.transfer_to_asset_id)
        if payload.transfer_to_asset_id is not None
        else None
    )
    try:
        return transaction_crud.update_transaction(
            db,
            transaction=transaction,
            asset=asset,
            date=payload.date,
            amount=payload.amount,
            entry_kind=payload.entry_kind,
            major_category_id=payload.major_category_id,
            expense_category_id=payload.expense_category_id,
            income_category_id=payload.income_category_id,
            memo=payload.memo,
            transfer_to_asset=transfer_to_asset,
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="指定されたカテゴリが存在しません",
        ) from exc


@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)) -> None:
    transaction = _get_transaction_or_404(db, transaction_id)
    transaction_crud.delete_transaction(db, transaction)


@router.get("/summary/monthly", response_model=MonthlySummary)
def get_monthly_summary(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
) -> MonthlySummary:
    totals = transaction_crud.get_monthly_summary(db, year, month)
    return MonthlySummary(year=year, month=month, **totals)
