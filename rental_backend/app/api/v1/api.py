from fastapi import APIRouter
from app.api.v1.endpoints import auth, houses, rooms, customers, utilities, payments, eom, issues, dashboard, history

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(houses.router, tags=["houses"])
api_router.include_router(rooms.router, tags=["rooms"])
api_router.include_router(customers.router, tags=["customers"])
api_router.include_router(utilities.router, tags=["utilities"])
api_router.include_router(payments.router, tags=["payments"])
api_router.include_router(eom.router, tags=["eom"])
api_router.include_router(issues.router, tags=["issues"])
api_router.include_router(dashboard.router, tags=["dashboard"])
api_router.include_router(history.router, tags=["history"])
