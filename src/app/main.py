from fastapi import FastAPI
from src.app.routers import analytics

app = FastAPI(
    title="Moniepoint Analytics API",
    version="1.0.0",
)

app.include_router(analytics.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Moniepoint Analytics API is running."}