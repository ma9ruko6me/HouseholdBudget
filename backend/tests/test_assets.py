from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Asset, RecurringTransaction, Transaction


def _create_asset(db_session: Session, balance: int = 10000) -> Asset:
    asset = Asset(name="テスト銀行", type="bank", balance=balance, sort_order=1)
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)
    return asset


def test_list_assets_empty(client: TestClient) -> None:
    response = client.get("/api/assets")
    assert response.status_code == 200
    assert response.json() == {"items": [], "total_balance": "0"}


def test_create_asset(client: TestClient) -> None:
    response = client.post("/api/assets", json={"name": "現金", "type": "cash", "balance": 5000})
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "現金"
    assert body["type"] == "cash"
    assert body["balance"] == "5000"
    assert body["sort_order"] == 1


def test_create_asset_invalid_type_returns_400(client: TestClient) -> None:
    response = client.post("/api/assets", json={"name": "現金", "type": "invalid", "balance": 0})
    assert response.status_code == 400


def test_list_assets_returns_total_balance(client: TestClient, db_session: Session) -> None:
    _create_asset(db_session, balance=10000)
    asset2 = Asset(name="財布", type="cash", balance=3000, sort_order=2)
    db_session.add(asset2)
    db_session.commit()

    response = client.get("/api/assets")
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 2
    assert body["total_balance"] == "13000"


def test_update_asset(client: TestClient, db_session: Session) -> None:
    asset = _create_asset(db_session)

    response = client.put(f"/api/assets/{asset.id}", json={"name": "改名後", "type": "credit_card"})

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "改名後"
    assert body["type"] == "credit_card"
    assert body["balance"] == "10000"  # balanceは変わらない


def test_update_asset_not_found_returns_404(client: TestClient) -> None:
    response = client.put("/api/assets/999999", json={"name": "x", "type": "cash"})
    assert response.status_code == 404


def test_delete_asset(client: TestClient, db_session: Session) -> None:
    asset = _create_asset(db_session)

    response = client.delete(f"/api/assets/{asset.id}")

    assert response.status_code == 204
    assert db_session.get(Asset, asset.id) is None


def test_delete_asset_not_found_returns_404(client: TestClient) -> None:
    response = client.delete("/api/assets/999999")
    assert response.status_code == 404


def test_delete_asset_referenced_by_transaction_returns_400(
    client: TestClient, db_session: Session
) -> None:
    asset = _create_asset(db_session)
    transaction = Transaction(
        date=date(2026, 8, 1),
        amount=1000,
        entry_kind="expense",
        entry_type="normal",
        asset_id=asset.id,
    )
    db_session.add(transaction)
    db_session.commit()

    response = client.delete(f"/api/assets/{asset.id}")

    assert response.status_code == 400
    assert db_session.get(Asset, asset.id) is not None


def test_delete_asset_referenced_by_recurring_transaction_returns_400(
    client: TestClient, db_session: Session
) -> None:
    asset = _create_asset(db_session)
    recurring = RecurringTransaction(
        amount=50000,
        entry_kind="expense",
        asset_id=asset.id,
        day_of_month=1,
    )
    db_session.add(recurring)
    db_session.commit()

    response = client.delete(f"/api/assets/{asset.id}")

    assert response.status_code == 400


def test_adjust_asset_balance_increase_creates_income_transaction(
    client: TestClient, db_session: Session
) -> None:
    asset = _create_asset(db_session, balance=10000)

    response = client.post(f"/api/assets/{asset.id}/adjust", json={"actual_balance": 12000})

    assert response.status_code == 200
    body = response.json()
    assert body["asset"]["balance"] == "12000"
    assert body["transaction"]["entry_kind"] == "income"
    assert body["transaction"]["entry_type"] == "adjustment"
    assert body["transaction"]["amount"] == "2000"


def test_adjust_asset_balance_decrease_creates_expense_transaction(
    client: TestClient, db_session: Session
) -> None:
    asset = _create_asset(db_session, balance=10000)

    response = client.post(f"/api/assets/{asset.id}/adjust", json={"actual_balance": 7000})

    assert response.status_code == 200
    body = response.json()
    assert body["asset"]["balance"] == "7000"
    assert body["transaction"]["entry_kind"] == "expense"
    assert body["transaction"]["amount"] == "3000"


def test_adjust_asset_balance_no_diff_creates_no_transaction(
    client: TestClient, db_session: Session
) -> None:
    asset = _create_asset(db_session, balance=10000)

    response = client.post(f"/api/assets/{asset.id}/adjust", json={"actual_balance": 10000})

    assert response.status_code == 200
    body = response.json()
    assert body["transaction"] is None
    assert body["asset"]["balance"] == "10000"


def test_adjust_asset_not_found_returns_404(client: TestClient) -> None:
    response = client.post("/api/assets/999999/adjust", json={"actual_balance": 100})
    assert response.status_code == 404
