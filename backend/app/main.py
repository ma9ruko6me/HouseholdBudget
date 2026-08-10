from fastapi import FastAPI

from app.api.routes.categories import router as categories_router

app = FastAPI(title="HouseholdBudget API")

app.include_router(categories_router, prefix="/api")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
