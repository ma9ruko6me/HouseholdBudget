from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.crud.report import _months_before
from app.models import Asset, ExpenseCategory, Transaction


def _create_asset(db_session: Session, balance: int = 0) -> Asset:
    asset = Asset(name="テスト銀行", type="bank", balance=balance, sort_order=99)
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)
    return asset


def _expense_category(db_session: Session, major_category_id: int) -> ExpenseCategory:
    category = (
        db_session.query(ExpenseCategory)
        .filter(ExpenseCategory.major_category_id == major_category_id)
        .first()
    )
    assert category is not None
    return category


def test_category_breakdown_groups_expense_by_major_category(
    client: TestClient, db_session: Session
) -> None:
    asset = _create_asset(db_session, balance=100000)
    fixed_cost = _expense_category(db_session, major_category_id=1)
    food_cost = _expense_category(db_session, major_category_id=2)

    db_session.add_all(
        [
            Transaction(
                date=date(2031, 1, 5),
                amount=8000,
                entry_kind="expense",
                entry_type="normal",
                major_category_id=1,
                expense_category_id=fixed_cost.id,
                asset_id=asset.id,
            ),
            Transaction(
                date=date(2031, 1, 10),
                amount=2000,
                entry_kind="expense",
                entry_type="normal",
                major_category_id=1,
                expense_category_id=fixed_cost.id,
                asset_id=asset.id,
            ),
            Transaction(
                date=date(2031, 1, 15),
                amount=5000,
                entry_kind="expense",
                entry_type="normal",
                major_category_id=2,
                expense_category_id=food_cost.id,
                asset_id=asset.id,
            ),
            # 収入は集計対象外
            Transaction(
                date=date(2031, 1, 20),
                amount=300000,
                entry_kind="income",
                entry_type="normal",
                asset_id=asset.id,
            ),
            # 対象月外は集計対象外
            Transaction(
                date=date(2031, 2, 1),
                amount=9999,
                entry_kind="expense",
                entry_type="normal",
                major_category_id=1,
                expense_category_id=fixed_cost.id,
                asset_id=asset.id,
            ),
        ]
    )
    db_session.commit()

    response = client.get("/api/reports/category-breakdown", params={"year": 2031, "month": 1})

    assert response.status_code == 200
    body = response.json()
    items_by_id = {item["major_category_id"]: item for item in body["items"]}
    assert items_by_id[1]["amount"] == "10000"
    assert items_by_id[2]["amount"] == "5000"
    assert body["total"] == "15000"


def test_category_breakdown_empty_month_returns_empty_items(client: TestClient) -> None:
    response = client.get("/api/reports/category-breakdown", params={"year": 2030, "month": 1})

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == "0"


def test_asset_trend_returns_one_point_per_day(client: TestClient) -> None:
    today = date.today()
    start_date = _months_before(today, 3)

    response = client.get("/api/reports/asset-trend", params={"period": "3m"})

    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == (today - start_date).days + 1
    assert items[0]["date"] == start_date.isoformat()
    assert items[-1]["date"] == today.isoformat()


def test_asset_trend_reconstructs_daily_balances(client: TestClient, db_session: Session) -> None:
    today = date.today()
    yesterday = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)

    baseline = {
        p["date"]: int(p["total_balance"])
        for p in client.get("/api/reports/asset-trend", params={"period": "3m"}).json()["items"]
    }

    asset = _create_asset(db_session, balance=5000)
    db_session.add_all(
        [
            Transaction(
                date=yesterday,
                amount=2000,
                entry_kind="expense",
                entry_type="normal",
                asset_id=asset.id,
            ),
            Transaction(
                date=today,
                amount=1000,
                entry_kind="income",
                entry_type="normal",
                asset_id=asset.id,
            ),
        ]
    )
    db_session.commit()

    after = {
        p["date"]: int(p["total_balance"])
        for p in client.get("/api/reports/asset-trend", params={"period": "3m"}).json()["items"]
    }

    assert after[two_days_ago.isoformat()] - baseline[two_days_ago.isoformat()] == 6000
    assert after[yesterday.isoformat()] - baseline[yesterday.isoformat()] == 4000
    assert after[today.isoformat()] - baseline[today.isoformat()] == 5000


def test_asset_trend_all_period_starts_at_earliest_transaction(
    client: TestClient, db_session: Session
) -> None:
    asset = _create_asset(db_session, balance=1000)
    old_date = date(2020, 1, 15)
    db_session.add(
        Transaction(
            date=old_date,
            amount=500,
            entry_kind="income",
            entry_type="normal",
            asset_id=asset.id,
        )
    )
    db_session.commit()

    response = client.get("/api/reports/asset-trend", params={"period": "all"})

    assert response.status_code == 200
    items = response.json()["items"]
    assert items[0]["date"] <= old_date.isoformat()
    assert items[-1]["date"] == date.today().isoformat()


def test_asset_trend_rejects_unsupported_period(client: TestClient) -> None:
    response = client.get("/api/reports/asset-trend", params={"period": "5m"})

    assert response.status_code == 400


def test_category_breakdown_excludes_transfer(client: TestClient, db_session: Session) -> None:
    source = _create_asset(db_session, balance=100000)
    destination = Asset(name="テスト財布", type="cash", balance=0, sort_order=98)
    db_session.add(destination)
    db_session.commit()
    db_session.refresh(destination)
    fixed_cost = _expense_category(db_session, major_category_id=1)

    db_session.add_all(
        [
            Transaction(
                date=date(2031, 3, 5),
                amount=8000,
                entry_kind="expense",
                entry_type="normal",
                major_category_id=1,
                expense_category_id=fixed_cost.id,
                asset_id=source.id,
            ),
            Transaction(
                date=date(2031, 3, 10),
                amount=20000,
                entry_kind="transfer",
                entry_type="normal",
                asset_id=source.id,
                transfer_to_asset_id=destination.id,
            ),
        ]
    )
    db_session.commit()

    response = client.get("/api/reports/category-breakdown", params={"year": 2031, "month": 3})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == "8000"
