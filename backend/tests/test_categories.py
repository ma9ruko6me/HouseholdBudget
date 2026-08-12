from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Asset, ExpenseCategory, IncomeCategory, MajorCategory, Transaction


def test_list_major_categories(client: TestClient) -> None:
    response = client.get("/api/major-categories")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 4
    assert [item["name"] for item in body] == ["固定費", "食費", "生活費", "娯楽費"]


def test_list_expense_categories(client: TestClient) -> None:
    response = client.get("/api/expense-categories")
    assert response.status_code == 200
    assert len(response.json()) == 10


def test_create_expense_category(client: TestClient, db_session: Session) -> None:
    major_category = db_session.query(MajorCategory).filter_by(name="食費").one()

    response = client.post(
        "/api/expense-categories",
        json={"major_category_id": major_category.id, "name": "お菓子"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "お菓子"
    assert body["major_category_id"] == major_category.id
    assert body["sort_order"] == 3  # 食費配下の既存2件("食材","外食")の次


def test_create_expense_category_duplicate_name_returns_400(client: TestClient) -> None:
    major_category_id = 1
    existing = client.post(
        "/api/expense-categories",
        json={"major_category_id": major_category_id, "name": "水道光熱費"},
    )
    assert existing.status_code == 400


def test_create_expense_category_unknown_major_category_returns_400(client: TestClient) -> None:
    response = client.post(
        "/api/expense-categories",
        json={"major_category_id": 9999, "name": "新カテゴリ"},
    )
    assert response.status_code == 400


def test_delete_expense_category(client: TestClient, db_session: Session) -> None:
    category = ExpenseCategory(major_category_id=1, name="テスト用", sort_order=99)
    db_session.add(category)
    db_session.commit()

    response = client.delete(f"/api/expense-categories/{category.id}")

    assert response.status_code == 204
    assert db_session.get(ExpenseCategory, category.id) is None


def test_delete_expense_category_not_found_returns_404(client: TestClient) -> None:
    response = client.delete("/api/expense-categories/999999")
    assert response.status_code == 404


def test_delete_expense_category_referenced_by_transaction_sets_null(
    client: TestClient, db_session: Session
) -> None:
    asset = Asset(name="テスト口座", type="bank", balance=0, sort_order=1)
    category = ExpenseCategory(major_category_id=1, name="参照テスト用", sort_order=98)
    db_session.add_all([asset, category])
    db_session.commit()

    transaction = Transaction(
        date=date(2026, 8, 1),
        amount=1000,
        entry_kind="expense",
        entry_type="normal",
        major_category_id=1,
        expense_category_id=category.id,
        asset_id=asset.id,
    )
    db_session.add(transaction)
    db_session.commit()

    response = client.delete(f"/api/expense-categories/{category.id}")
    assert response.status_code == 204

    db_session.refresh(transaction)
    assert transaction.expense_category_id is None


def test_list_income_categories(client: TestClient) -> None:
    response = client.get("/api/income-categories")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_create_income_category(client: TestClient) -> None:
    response = client.post("/api/income-categories", json={"name": "利子"})

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "利子"
    assert body["sort_order"] == 4


def test_create_income_category_duplicate_name_returns_400(client: TestClient) -> None:
    response = client.post("/api/income-categories", json={"name": "給与"})
    assert response.status_code == 400


def test_delete_income_category(client: TestClient, db_session: Session) -> None:
    category = IncomeCategory(name="テスト用収入", sort_order=99)
    db_session.add(category)
    db_session.commit()

    response = client.delete(f"/api/income-categories/{category.id}")

    assert response.status_code == 204
    assert db_session.get(IncomeCategory, category.id) is None


def test_delete_income_category_not_found_returns_404(client: TestClient) -> None:
    response = client.delete("/api/income-categories/999999")
    assert response.status_code == 404
