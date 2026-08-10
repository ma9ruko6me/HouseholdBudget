import calendar
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

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


def _month_end(year: int, month: int) -> date:
    return date(year, month, calendar.monthrange(year, month)[1])


def _shift_month(year: int, month: int, offset: int) -> tuple[int, int]:
    month -= offset
    while month <= 0:
        month += 12
        year -= 1
    return year, month


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

    response = client.get(
        "/api/reports/category-breakdown", params={"year": 2031, "month": 1}
    )

    assert response.status_code == 200
    body = response.json()
    items_by_id = {item["major_category_id"]: item for item in body["items"]}
    assert items_by_id[1]["amount"] == "10000"
    assert items_by_id[2]["amount"] == "5000"
    assert body["total"] == "15000"


def test_category_breakdown_empty_month_returns_empty_items(client: TestClient) -> None:
    response = client.get(
        "/api/reports/category-breakdown", params={"year": 2030, "month": 1}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == "0"


def test_asset_trend_reconstructs_past_balances(
    client: TestClient, db_session: Session
) -> None:
    today = date.today()
    prev_year, prev_month = _shift_month(today.year, today.month, 1)
    prev_month_end = _month_end(prev_year, prev_month)
    two_months_ago_year, two_months_ago_month = _shift_month(today.year, today.month, 2)
    two_months_ago_end = _month_end(two_months_ago_year, two_months_ago_month)

    baseline = client.get(
        "/api/reports/asset-trend", params={"months": 3}
    ).json()["items"]
    assert len(baseline) == 3

    asset = _create_asset(db_session, balance=5000)
    db_session.add_all(
        [
            Transaction(
                date=prev_month_end,
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

    after = client.get("/api/reports/asset-trend", params={"months": 3}).json()["items"]

    assert [p["date"] for p in after] == [
        two_months_ago_end.isoformat(),
        prev_month_end.isoformat(),
        today.isoformat(),
    ]

    deltas = [
        int(after[i]["total_balance"]) - int(baseline[i]["total_balance"])
        for i in range(3)
    ]
    assert deltas == [6000, 4000, 5000]


def test_asset_trend_rejects_unsupported_months(client: TestClient) -> None:
    response = client.get("/api/reports/asset-trend", params={"months": 4})

    assert response.status_code == 400
