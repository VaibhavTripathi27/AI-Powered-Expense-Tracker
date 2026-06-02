from fastapi import APIRouter

from app.api.v1 import alerts, analytics, auth, budgets, expenses, insights

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(expenses.router)
api_router.include_router(budgets.router)
api_router.include_router(alerts.router)
api_router.include_router(analytics.router)
api_router.include_router(insights.router)
