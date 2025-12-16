from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, rooms, customers, utilities, payments, dashboard, issues, history, eom, electric_bill

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(rooms.router, tags=["rooms"])
api_router.include_router(customers.router, tags=["customers"])
api_router.include_router(utilities.router, tags=["utilities"])
api_router.include_router(payments.router, tags=["payments"])
api_router.include_router(dashboard.router, tags=["dashboard"])
api_router.include_router(issues.router, tags=["issues"])
api_router.include_router(history.router, tags=["history"])
api_router.include_router(eom.router, tags=["end-of-month"])
api_router.include_router(electric_bill.router, tags=["electric-bill"])
