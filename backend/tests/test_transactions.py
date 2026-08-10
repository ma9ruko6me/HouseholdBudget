from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Asset, ExpenseCategory, IncomeCategory, Transaction


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


def test_create_expense_transaction_decreases_asset_balance(
    client: TestClient, db_session: Session
) -> None:
    asset = _create_asset(db_session, balance=10000)
    expense_category = _expense_category(db_session)

    response = client.post(
        "/api/transactions",
        json={
            "date": "2026-08-10",
            "amount": "1500",
            "entry_kind": "expense",
            "major_category_id": expense_category.major_category_id,
            "expense_category_id": expense_category.id,
            "asset_id": asset.id,
            "memo": "ランチ",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["entry_kind"] == "expense"
    assert body["entry_type"] == "normal"
    assert body["amount"] == "1500"

    db_session.refresh(asset)
    assert asset.balance == Decimal("8500")


def test_create_income_transaction_increases_asset_balance(
    client: TestClient, db_session: Session
) -> None:
    asset = _create_asset(db_session, balance=10000)
    income_category_id = _income_category_id(db_session)

    response = client.post(
        "/api/transactions",
        json={
            "date": "2026-08-08",
            "amount": "300000",
            "entry_kind": "income",
            "income_category_id": income_category_id,
            "asset_id": asset.id,
        },
    )

    assert response.status_code == 201
    db_session.refresh(asset)
    assert asset.balance == Decimal("310000")


def test_create_expense_without_expense_category_returns_422(
    client: TestClient, db_session: Session
) -> None:
    asset = _create_asset(db_session)

    response = client.post(
        "/api/transactions",
        json={
            "date": "2026-08-10",
            "amount": "1000",
            "entry_kind": "expense",
            "asset_id": asset.id,
        },
    )

    assert response.status_code == 422


def test_create_income_with_expense_category_returns_422(
    client: TestClient, db_session: Session
) -> None:
    asset = _create_asset(db_session)
    income_category_id = _income_category_id(db_session)
    expense_category = _expense_category(db_session)

    response = client.post(
        "/api/transactions",
        json={
            "date": "2026-08-10",
            "amount": "1000",
            "entry_kind": "income",
            "income_category_id": income_category_id,
            "expense_category_id": expense_category.id,
            "asset_id": asset.id,
        },
    )

    assert response.status_code == 422


def test_create_transaction_unknown_asset_returns_400(
    client: TestClient, db_session: Session
) -> None:
    income_category_id = _income_category_id(db_session)

    response = client.post(
        "/api/transactions",
        json={
            "date": "2026-08-10",
            "amount": "1000",
            "entry_kind": "income",
            "income_category_id": income_category_id,
            "asset_id": 999999,
        },
    )

    assert response.status_code == 400


def test_list_transactions_filters_by_month(client: TestClient, db_session: Session) -> None:
    asset = _create_asset(db_session)
    income_category_id = _income_category_id(db_session)
    db_session.add_all(
        [
            Transaction(
                date=date(2026, 8, 5),
                amount=1000,
                entry_kind="income",
                entry_type="normal",
                income_category_id=income_category_id,
                asset_id=asset.id,
            ),
            Transaction(
                date=date(2026, 7, 5),
                amount=2000,
                entry_kind="income",
                entry_type="normal",
                income_category_id=income_category_id,
                asset_id=asset.id,
            ),
        ]
    )
    db_session.commit()

    response = client.get("/api/transactions", params={"year": 2026, "month": 8})

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["amount"] == "1000"


def test_update_transaction_amount_adjusts_asset_balance(
    client: TestClient, db_session: Session
) -> None:
    asset = _create_asset(db_session, balance=10000)
    expense_category = _expense_category(db_session)
    create_response = client.post(
        "/api/transactions",
        json={
            "date": "2026-08-10",
            "amount": "1000",
            "entry_kind": "expense",
            "major_category_id": expense_category.major_category_id,
            "expense_category_id": expense_category.id,
            "asset_id": asset.id,
        },
    )
    transaction_id = create_response.json()["id"]
    db_session.refresh(asset)
    assert asset.balance == Decimal("9000")

    update_response = client.put(
        f"/api/transactions/{transaction_id}",
        json={
            "date": "2026-08-10",
            "amount": "4000",
            "entry_kind": "expense",
            "major_category_id": expense_category.major_category_id,
            "expense_category_id": expense_category.id,
            "asset_id": asset.id,
        },
    )

    assert update_response.status_code == 200
    db_session.refresh(asset)
    assert asset.balance == Decimal("6000")


def test_update_transaction_change_asset_moves_balance(
    client: TestClient, db_session: Session
) -> None:
    asset_a = _create_asset(db_session, balance=10000)
    asset_b = Asset(name="財布", type="cash", balance=5000, sort_order=2)
    db_session.add(asset_b)
    db_session.commit()
    db_session.refresh(asset_b)
    expense_category = _expense_category(db_session)

    create_response = client.post(
        "/api/transactions",
        json={
            "date": "2026-08-10",
            "amount": "1000",
            "entry_kind": "expense",
            "major_category_id": expense_category.major_category_id,
            "expense_category_id": expense_category.id,
            "asset_id": asset_a.id,
        },
    )
    transaction_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/transactions/{transaction_id}",
        json={
            "date": "2026-08-10",
            "amount": "1000",
            "entry_kind": "expense",
            "major_category_id": expense_category.major_category_id,
            "expense_category_id": expense_category.id,
            "asset_id": asset_b.id,
        },
    )

    assert update_response.status_code == 200
    db_session.refresh(asset_a)
    db_session.refresh(asset_b)
    assert asset_a.balance == Decimal("10000")
    assert asset_b.balance == Decimal("4000")


def test_update_transaction_not_found_returns_404(client: TestClient, db_session: Session) -> None:
    asset = _create_asset(db_session)
    income_category_id = _income_category_id(db_session)

    response = client.put(
        "/api/transactions/999999",
        json={
            "date": "2026-08-10",
            "amount": "1000",
            "entry_kind": "income",
            "income_category_id": income_category_id,
            "asset_id": asset.id,
        },
    )

    assert response.status_code == 404


def test_delete_transaction_reverts_asset_balance(client: TestClient, db_session: Session) -> None:
    asset = _create_asset(db_session, balance=10000)
    income_category_id = _income_category_id(db_session)
    create_response = client.post(
        "/api/transactions",
        json={
            "date": "2026-08-10",
            "amount": "2000",
            "entry_kind": "income",
            "income_category_id": income_category_id,
            "asset_id": asset.id,
        },
    )
    transaction_id = create_response.json()["id"]
    db_session.refresh(asset)
    assert asset.balance == Decimal("12000")

    response = client.delete(f"/api/transactions/{transaction_id}")

    assert response.status_code == 204
    db_session.refresh(asset)
    assert asset.balance == Decimal("10000")
    assert db_session.get(Transaction, transaction_id) is None


def test_delete_transaction_not_found_returns_404(client: TestClient) -> None:
    response = client.delete("/api/transactions/999999")
    assert response.status_code == 404


def test_monthly_summary_includes_adjustment_transactions(
    client: TestClient, db_session: Session
) -> None:
    asset = _create_asset(db_session, balance=10000)
    income_category_id = _income_category_id(db_session)
    expense_category = _expense_category(db_session)

    db_session.add_all(
        [
            Transaction(
                date=date(2026, 8, 1),
                amount=5000,
                entry_kind="income",
                entry_type="normal",
                income_category_id=income_category_id,
                asset_id=asset.id,
            ),
            Transaction(
                date=date(2026, 8, 2),
                amount=2000,
                entry_kind="expense",
                entry_type="normal",
                major_category_id=expense_category.major_category_id,
                expense_category_id=expense_category.id,
                asset_id=asset.id,
            ),
            Transaction(
                date=date(2026, 8, 3),
                amount=1000,
                entry_kind="income",
                entry_type="adjustment",
                asset_id=asset.id,
            ),
        ]
    )
    db_session.commit()

    response = client.get("/api/summary/monthly", params={"year": 2026, "month": 8})

    assert response.status_code == 200
    body = response.json()
    assert body["income_total"] == "6000"
    assert body["expense_total"] == "2000"
    assert body["balance"] == "4000"


def test_monthly_summary_empty_month_returns_zero(client: TestClient) -> None:
    response = client.get("/api/summary/monthly", params={"year": 2020, "month": 1})

    assert response.status_code == 200
    body = response.json()
    assert body["income_total"] == "0"
    assert body["expense_total"] == "0"
    assert body["balance"] == "0"


def _create_second_asset(db_session: Session, balance: int = 5000) -> Asset:
    asset = Asset(name="テスト財布", type="cash", balance=balance, sort_order=2)
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)
    return asset


def test_create_transfer_moves_balance_between_assets(
    client: TestClient, db_session: Session
) -> None:
    source = _create_asset(db_session, balance=10000)
    destination = _create_second_asset(db_session, balance=3000)

    response = client.post(
        "/api/transactions",
        json={
            "date": "2026-08-10",
            "amount": "1500",
            "entry_kind": "transfer",
            "asset_id": source.id,
            "transfer_to_asset_id": destination.id,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["entry_kind"] == "transfer"
    assert body["major_category_id"] is None
    assert body["expense_category_id"] is None
    assert body["income_category_id"] is None
    assert body["transfer_to_asset_id"] == destination.id

    db_session.refresh(source)
    db_session.refresh(destination)
    assert source.balance == Decimal("8500")
    assert destination.balance == Decimal("4500")


def test_transfer_with_category_returns_422(client: TestClient, db_session: Session) -> None:
    source = _create_asset(db_session)
    destination = _create_second_asset(db_session)
    income_category_id = _income_category_id(db_session)

    response = client.post(
        "/api/transactions",
        json={
            "date": "2026-08-10",
            "amount": "1000",
            "entry_kind": "transfer",
            "income_category_id": income_category_id,
            "asset_id": source.id,
            "transfer_to_asset_id": destination.id,
        },
    )

    assert response.status_code == 422


def test_transfer_without_transfer_to_asset_id_returns_422(
    client: TestClient, db_session: Session
) -> None:
    source = _create_asset(db_session)

    response = client.post(
        "/api/transactions",
        json={
            "date": "2026-08-10",
            "amount": "1000",
            "entry_kind": "transfer",
            "asset_id": source.id,
        },
    )

    assert response.status_code == 422


def test_transfer_to_same_asset_returns_422(client: TestClient, db_session: Session) -> None:
    source = _create_asset(db_session)

    response = client.post(
        "/api/transactions",
        json={
            "date": "2026-08-10",
            "amount": "1000",
            "entry_kind": "transfer",
            "asset_id": source.id,
            "transfer_to_asset_id": source.id,
        },
    )

    assert response.status_code == 422


def test_transfer_unknown_destination_asset_returns_400(
    client: TestClient, db_session: Session
) -> None:
    source = _create_asset(db_session)

    response = client.post(
        "/api/transactions",
        json={
            "date": "2026-08-10",
            "amount": "1000",
            "entry_kind": "transfer",
            "asset_id": source.id,
            "transfer_to_asset_id": 999999,
        },
    )

    assert response.status_code == 400


def test_update_transfer_amount_adjusts_both_assets(
    client: TestClient, db_session: Session
) -> None:
    source = _create_asset(db_session, balance=10000)
    destination = _create_second_asset(db_session, balance=3000)

    create_response = client.post(
        "/api/transactions",
        json={
            "date": "2026-08-10",
            "amount": "1000",
            "entry_kind": "transfer",
            "asset_id": source.id,
            "transfer_to_asset_id": destination.id,
        },
    )
    transaction_id = create_response.json()["id"]
    db_session.refresh(source)
    db_session.refresh(destination)
    assert source.balance == Decimal("9000")
    assert destination.balance == Decimal("4000")

    update_response = client.put(
        f"/api/transactions/{transaction_id}",
        json={
            "date": "2026-08-10",
            "amount": "4000",
            "entry_kind": "transfer",
            "asset_id": source.id,
            "transfer_to_asset_id": destination.id,
        },
    )

    assert update_response.status_code == 200
    db_session.refresh(source)
    db_session.refresh(destination)
    assert source.balance == Decimal("6000")
    assert destination.balance == Decimal("7000")


def test_update_transfer_change_destination_moves_balance(
    client: TestClient, db_session: Session
) -> None:
    source = _create_asset(db_session, balance=10000)
    destination_a = _create_second_asset(db_session, balance=3000)
    destination_b = Asset(name="テストカード", type="credit_card", balance=0, sort_order=3)
    db_session.add(destination_b)
    db_session.commit()
    db_session.refresh(destination_b)

    create_response = client.post(
        "/api/transactions",
        json={
            "date": "2026-08-10",
            "amount": "1000",
            "entry_kind": "transfer",
            "asset_id": source.id,
            "transfer_to_asset_id": destination_a.id,
        },
    )
    transaction_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/transactions/{transaction_id}",
        json={
            "date": "2026-08-10",
            "amount": "1000",
            "entry_kind": "transfer",
            "asset_id": source.id,
            "transfer_to_asset_id": destination_b.id,
        },
    )

    assert update_response.status_code == 200
    db_session.refresh(source)
    db_session.refresh(destination_a)
    db_session.refresh(destination_b)
    assert source.balance == Decimal("9000")
    assert destination_a.balance == Decimal("3000")
    assert destination_b.balance == Decimal("1000")


def test_delete_transfer_reverts_both_assets(client: TestClient, db_session: Session) -> None:
    source = _create_asset(db_session, balance=10000)
    destination = _create_second_asset(db_session, balance=3000)

    create_response = client.post(
        "/api/transactions",
        json={
            "date": "2026-08-10",
            "amount": "1000",
            "entry_kind": "transfer",
            "asset_id": source.id,
            "transfer_to_asset_id": destination.id,
        },
    )
    transaction_id = create_response.json()["id"]

    response = client.delete(f"/api/transactions/{transaction_id}")

    assert response.status_code == 204
    db_session.refresh(source)
    db_session.refresh(destination)
    assert source.balance == Decimal("10000")
    assert destination.balance == Decimal("3000")


def test_monthly_summary_excludes_transfer(client: TestClient, db_session: Session) -> None:
    source = _create_asset(db_session, balance=10000)
    destination = _create_second_asset(db_session, balance=3000)
    income_category_id = _income_category_id(db_session)

    db_session.add_all(
        [
            Transaction(
                date=date(2026, 8, 1),
                amount=5000,
                entry_kind="income",
                entry_type="normal",
                income_category_id=income_category_id,
                asset_id=source.id,
            ),
            Transaction(
                date=date(2026, 8, 2),
                amount=2000,
                entry_kind="transfer",
                entry_type="normal",
                asset_id=source.id,
                transfer_to_asset_id=destination.id,
            ),
        ]
    )
    db_session.commit()

    response = client.get("/api/summary/monthly", params={"year": 2026, "month": 8})

    assert response.status_code == 200
    body = response.json()
    assert body["income_total"] == "5000"
    assert body["expense_total"] == "0"
    assert body["balance"] == "5000"


def test_asset_referenced_as_transfer_destination_cannot_be_deleted(
    client: TestClient, db_session: Session
) -> None:
    source = _create_asset(db_session)
    destination = _create_second_asset(db_session)
    db_session.add(
        Transaction(
            date=date(2026, 8, 10),
            amount=1000,
            entry_kind="transfer",
            entry_type="normal",
            asset_id=source.id,
            transfer_to_asset_id=destination.id,
        )
    )
    db_session.commit()

    response = client.delete(f"/api/assets/{destination.id}")

    assert response.status_code == 400
