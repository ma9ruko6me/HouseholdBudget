from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.assets import router as assets_router
from app.api.routes.categories import router as categories_router
from app.api.routes.transactions import router as transactions_router
from app.core.config import settings

app = FastAPI(title="HouseholdBudget API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories_router, prefix="/api")
app.include_router(assets_router, prefix="/api")
app.include_router(transactions_router, prefix="/api")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
