# HouseholdBudget

マネーフォワード ME のような個人向け家計簿Webアプリケーション。銀行・クレジットカード連携による自動取得は行わず、手動入力を前提とすることで、自分の生活に合わせたカテゴリ設計や機能を自由にカスタマイズできることを目指した学習課題として開発している。

個人(単一ユーザー)での利用を前提に、以下の機能を備える。

- **取引管理**: 収入・支出を日付/金額/カテゴリ/資産/メモ付きで記録し、月別に一覧表示する
- **資産管理**: 銀行口座・現金・クレジットカードを資産として登録し、残高を一元管理する。実際の残高を入力するだけで差額を自動的に取引として記録する「残高調整」、資産間でお金を移動する「振替」にも対応
- **定期取引**: 家賃・サブスクなど毎月発生する取引を登録しておくと、該当日に自動で取引として登録される
- **レポート**: 月別収支サマリ、カテゴリ別支出、資産全体の残高推移をグラフで可視化する

詳細な背景・機能要件は [docs/requirements.md](docs/requirements.md) を参照。

## デモ

<!-- TODO: アプリの動作確認用スクリーンショット・画面録画をここに貼り付ける -->

## ドキュメント

| ドキュメント | 内容 |
|--------------|------|
| [docs/requirements.md](docs/requirements.md) | 要件定義書。想定利用者、機能要件、データ項目など |
| [docs/basic-design.md](docs/basic-design.md) | 基本設計書。技術スタック、API設計、DB物理設計、ディレクトリ構成 |
| [docs/wireframes.html](docs/wireframes.html) | 画面のワイヤーフレーム(配色・タイポグラフィの決定にも使用) |

## 技術スタック

| 領域 | 技術 |
|------|------|
| バックエンド | Python 3.12+ / FastAPI / SQLAlchemy / Alembic / uv |
| フロントエンド | Next.js(App Router) / TypeScript / Tailwind CSS(CSR中心のSPA構成) |
| データベース | MySQL 8.0(Docker Composeで起動) |

選定理由の詳細は [docs/basic-design.md 1章](docs/basic-design.md#1-技術スタック) を参照。

## ディレクトリ構成

```
.
├── backend/    # FastAPI(REST API)
├── frontend/   # Next.js(画面)
└── docs/       # 要件定義書・基本設計書・ワイヤーフレーム
```

バックエンド・フロントエンドそれぞれの内部構成は [docs/basic-design.md 5章](docs/basic-design.md#5-ディレクトリ構成) を参照。

## セットアップ

### 前提

- Python 3.12+
- uv(Pythonパッケージ管理)
- Node.js(npm)
- Docker(MySQLをコンテナで起動するため)

### 1. データベースの起動

```bash
cd backend
docker compose up -d
```

`backend/docker-compose.yml` により、MySQL 8.0 がポート `3306` で起動する(DB名・ユーザー名・パスワードは `household_budget` / `household` / `household`)。

### 2. バックエンドの起動(ポート8000)

```bash
cd backend
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

起動後、以下で疎通確認・API仕様確認ができる。

- Swagger UI: `http://localhost:8000/docs`

### 3. フロントエンドの起動(ポート3000)

```bash
cd frontend
npm install
npm run dev
```

`http://localhost:3000/` にアクセスすると取引一覧画面が表示される。

> [!IMPORTANT]
> フロントエンドは `http://localhost:8000` (既定ポート)のバックエンドにAPIリクエストする構成のため、両方とも既定ポート(バックエンド`8000`／フロントエンド`3000`)で起動すること。ポート競合時に別ポートへフォールバックしたまま起動すると、通信が成立せず正しく動作しない。

## API

| メソッド | パス | 概要 |
|---------|------|------|
| GET | `/api/transactions` | 取引一覧取得(`year`・`month`クエリで月別絞り込み) |
| POST | `/api/transactions` | 取引の新規登録(通常の収入/支出のほか、`entry_kind=transfer`で資産間振替も登録) |
| PUT | `/api/transactions/{id}` | 取引の編集 |
| DELETE | `/api/transactions/{id}` | 取引の削除 |
| GET | `/api/summary/monthly` | 月別収支サマリ取得 |
| GET | `/api/reports/category-breakdown` | 月別・大カテゴリ別支出集計取得 |
| GET | `/api/reports/asset-trend` | 資産全体の残高推移取得(3・6・12ヶ月から期間切替) |
| GET | `/api/assets` | 資産一覧取得(残高・合計資産額を含む) |
| POST | `/api/assets` | 資産の新規登録 |
| PUT | `/api/assets/{id}` | 資産の編集 |
| DELETE | `/api/assets/{id}` | 資産の削除 |
| POST | `/api/assets/{id}/adjust` | 資産残高調整(実際の残高との差額を調整取引として自動登録) |
| GET | `/api/recurring-transactions` | 定期取引一覧取得 |
| POST | `/api/recurring-transactions` | 定期取引の新規登録 |
| PUT | `/api/recurring-transactions/{id}` | 定期取引の編集 |
| DELETE | `/api/recurring-transactions/{id}` | 定期取引の削除 |
| GET | `/api/major-categories` | 支出大カテゴリ一覧取得(固定4件、参照のみ) |
| GET | `/api/expense-categories` | 支出中カテゴリ一覧取得 |
| POST | `/api/expense-categories` | 支出中カテゴリの新規登録 |
| DELETE | `/api/expense-categories/{id}` | 支出中カテゴリの削除 |
| GET | `/api/income-categories` | 収入カテゴリ一覧取得 |
| POST | `/api/income-categories` | 収入カテゴリの新規登録 |
| DELETE | `/api/income-categories/{id}` | 収入カテゴリの削除 |

詳細(リクエスト・レスポンス例など)は [docs/basic-design.md 4章](docs/basic-design.md#4-api設計) を参照。

## 開発ルール

Issue駆動・PRベースの開発フローに従う。詳細は [CLAUDE.md](CLAUDE.md) を参照。
