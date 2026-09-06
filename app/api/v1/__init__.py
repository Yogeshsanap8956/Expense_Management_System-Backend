from fastapi import APIRouter

from app.api.v1 import aarti, announcements, auth, dashboard, events, expenses, inventory, mahaprasad, members, reports, vargani

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(members.router)
api_router.include_router(vargani.router)
api_router.include_router(expenses.router)
api_router.include_router(announcements.router)
api_router.include_router(events.router)
api_router.include_router(aarti.router)
api_router.include_router(mahaprasad.router)
api_router.include_router(inventory.router)
api_router.include_router(reports.router)
