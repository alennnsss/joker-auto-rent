from fastapi import APIRouter

from app.api.v1 import admin, auth, bookings, cars

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(cars.router)
api_router.include_router(bookings.router)
api_router.include_router(admin.router)
