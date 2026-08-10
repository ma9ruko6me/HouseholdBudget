from datetime import date, datetime
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.crud.recurring_transaction import generate_due_transactions
from app.models import Asset, ExpenseCategory, IncomeCategory, RecurringTransaction, Transaction


def _create_asset(db_session: Session, balance: int = 10000) -> Asset:
    asset = Asset(name="テスト銀行", type="bank", balance=balance, sort_order=1)
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)
    return asset


def _expense_category(db_session: Session) -> ExpenseCategory:
    category = db_session.query(ExpenseCategory).first()
    assert category is not None
    return category


def _income_category_id(db_session: Session) -> int:
    category = db_session.query(IncomeCategory).first()
    assert category is not None
    return category.id


def test_create_recurring_transaction(client: TestClient, db_session: Session) -> None:
    asset = _create_asset(db_session)
    expense_category = _expense_category(db_session)

    response = client.post(
        "/api/recurring-transactions",
        json={
            "name": "家賃",
            "amount": "78000",
            "entry_kind": "expense",
            "major_category_id": expense_category.major_category_id,
            "expense_category_id": expense_category.id,
            "asset_id": asset.id,
            "day_of_month": 27,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "家賃"
    assert body["day_of_month"] == 27
    assert body["last_generated_date"] is None


def test_create_recurring_transaction_invalid_day_returns_422(
    client: TestClient, db_session: Session
) -> None:
    asset = _create_asset(db_session)
    income_category_id = _income_category_id(db_session)

    response = client.post(
        "/api/recurring-transactions",
        json={
            "name": "給与",
            "amount": "300000",
            "entry_kind": "income",
            "income_category_id": income_category_id,
            "asset_id": asset.id,
            "day_of_month": 32,
        },
    )

    assert response.status_code == 422


def test_update_recurring_transaction(client: TestClient, db_session: Session) -> None:
    asset = _create_asset(db_session)
    income_category_id = _income_category_id(db_session)
    recurring = RecurringTransaction(
        name="給与",
        amount=300000,
        entry_kind="income",
        income_category_id=income_category_id,
        asset_id=asset.id,
        day_of_month=25,
    )
    db_session.add(recurring)
    db_session.commit()

    response = client.put(
        f"/api/recurring-transactions/{recurring.id}",
        json={
            "name": "給与(改)",
            "amount": "310000",
            "entry_kind": "income",
            "income_category_id": income_category_id,
            "asset_id": asset.id,
            "day_of_month": 25,
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "給与(改)"
    assert response.json()["amount"] == "310000"


def test_update_recurring_transaction_not_found_returns_404(
    client: TestClient, db_session: Session
) -> None:
    asset = _create_asset(db_session)
    income_category_id = _income_category_id(db_session)

    response = client.put(
        "/api/recurring-transactions/999999",
        json={
            "name": "給与",
            "amount": "300000",
            "entry_kind": "income",
            "income_category_id": income_category_id,
            "asset_id": asset.id,
            "day_of_month": 25,
        },
    )

    assert response.status_code == 404


def test_delete_recurring_transaction(client: TestClient, db_session: Session) -> None:
    asset = _create_asset(db_session)
    income_category_id = _income_category_id(db_session)
    recurring = RecurringTransaction(
        name="給与",
        amount=300000,
        entry_kind="income",
        income_category_id=income_category_id,
        asset_id=asset.id,
        day_of_month=25,
    )
    db_session.add(recurring)
    db_session.commit()

    response = client.delete(f"/api/recurring-transactions/{recurring.id}")

    assert response.status_code == 204
    assert db_session.get(RecurringTransaction, recurring.id) is None


def test_delete_recurring_transaction_not_found_returns_404(client: TestClient) -> None:
    response = client.delete("/api/recurring-transactions/999999")
    assert response.status_code == 404


def test_generate_due_transactions_creates_transaction_on_or_after_created_month(
    db_session: Session,
) -> None:
    asset = _create_asset(db_session, balance=10000)
    income_category_id = _income_category_id(db_session)
    recurring = RecurringTransaction(
        name="給与",
        amount=300000,
        entry_kind="income",
        income_category_id=income_category_id,
        asset_id=asset.id,
        day_of_month=25,
    )
    db_session.add(recurring)
    db_session.commit()
    # created_at defaults to now(); simulate creation happened in 2026-08 for deterministic testing
    recurring.created_at = datetime(2026, 8, 1)
    db_session.commit()

    generate_due_transactions(db_session, today=date(2026, 8, 25))

    db_session.refresh(recurring)
    assert recurring.last_generated_date == date(2026, 8, 25)
    transactions = db_session.query(Transaction).all()
    assert len(transactions) == 1
    assert transactions[0].date == date(2026, 8, 25)
    assert transactions[0].amount == Decimal("300000")
    assert transactions[0].entry_type == "normal"

    db_session.refresh(asset)
    assert asset.balance == Decimal("310000")


def test_generate_due_transactions_does_not_generate_future_month(db_session: Session) -> None:
    asset = _create_asset(db_session)
    income_category_id = _income_category_id(db_session)
    recurring = RecurringTransaction(
        name="給与",
        amount=300000,
        entry_kind="income",
        income_category_id=income_category_id,
        asset_id=asset.id,
        day_of_month=25,
    )
    db_session.add(recurring)
    db_session.commit()
    recurring.created_at = datetime(2026, 8, 1)
    db_session.commit()

    generate_due_transactions(db_session, today=date(2026, 8, 10))

    assert db_session.query(Transaction).count() == 0
    db_session.refresh(recurring)
    assert recurring.last_generated_date is None


def test_generate_due_transactions_backfills_missed_months(db_session: Session) -> None:
    asset = _create_asset(db_session, balance=0)
    expense_category = _expense_category(db_session)
    recurring = RecurringTransaction(
        name="サブスク",
        amount=1000,
        entry_kind="expense",
        major_category_id=expense_category.major_category_id,
        expense_category_id=expense_category.id,
        asset_id=asset.id,
        day_of_month=1,
    )
    db_session.add(recurring)
    db_session.commit()
    recurring.created_at = datetime(2026, 6, 1)
    db_session.commit()

    generate_due_transactions(db_session, today=date(2026, 8, 15))

    transactions = db_session.query(Transaction).order_by(Transaction.date).all()
    assert [t.date for t in transactions] == [date(2026, 6, 1), date(2026, 7, 1), date(2026, 8, 1)]
    db_session.refresh(asset)
    assert asset.balance == Decimal("-3000")


def test_generate_due_transactions_clamps_to_month_end(db_session: Session) -> None:
    asset = _create_asset(db_session)
    expense_category = _expense_category(db_session)
    recurring = RecurringTransaction(
        name="月末支払い",
        amount=500,
        entry_kind="expense",
        major_category_id=expense_category.major_category_id,
        expense_category_id=expense_category.id,
        asset_id=asset.id,
        day_of_month=31,
    )
    db_session.add(recurring)
    db_session.commit()
    recurring.created_at = datetime(2026, 2, 1)
    db_session.commit()

    generate_due_transactions(db_session, today=date(2026, 2, 28))

    transactions = db_session.query(Transaction).all()
    assert len(transactions) == 1
    assert transactions[0].date == date(2026, 2, 28)


def test_generate_due_transactions_is_idempotent(db_session: Session) -> None:
    asset = _create_asset(db_session)
    income_category_id = _income_category_id(db_session)
    recurring = RecurringTransaction(
        name="給与",
        amount=300000,
        entry_kind="income",
        income_category_id=income_category_id,
        asset_id=asset.id,
        day_of_month=25,
    )
    db_session.add(recurring)
    db_session.commit()
    recurring.created_at = datetime(2026, 8, 1)
    db_session.commit()

    generate_due_transactions(db_session, today=date(2026, 8, 25))
    generate_due_transactions(db_session, today=date(2026, 8, 25))
    generate_due_transactions(db_session, today=date(2026, 8, 31))

    assert db_session.query(Transaction).count() == 1


def test_deleting_recurring_transaction_keeps_generated_transactions(
    db_session: Session,
) -> None:
    asset = _create_asset(db_session)
    income_category_id = _income_category_id(db_session)
    recurring = RecurringTransaction(
        name="給与",
        amount=300000,
        entry_kind="income",
        income_category_id=income_category_id,
        asset_id=asset.id,
        day_of_month=25,
    )
    db_session.add(recurring)
    db_session.commit()
    recurring.created_at = datetime(2026, 8, 1)
    db_session.commit()

    generate_due_transactions(db_session, today=date(2026, 8, 25))
    assert db_session.query(Transaction).count() == 1

    db_session.delete(recurring)
    db_session.commit()

    assert db_session.query(Transaction).count() == 1


def test_list_transactions_endpoint_triggers_generation(
    client: TestClient, db_session: Session
) -> None:
    asset = _create_asset(db_session)
    income_category_id = _income_category_id(db_session)
    recurring = RecurringTransaction(
        name="給与",
        amount=300000,
        entry_kind="income",
        income_category_id=income_category_id,
        asset_id=asset.id,
        day_of_month=1,
    )
    db_session.add(recurring)
    db_session.commit()
    recurring.created_at = datetime(2020, 1, 1)
    db_session.commit()

    response = client.get(
        "/api/transactions",
        params={"year": date.today().year, "month": date.today().month},
    )

    assert response.status_code == 200
    assert len(response.json()["items"]) >= 1
