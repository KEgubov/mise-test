from fastapi import APIRouter


from src.api.bookings import router as bookings_router

main_router = APIRouter()

main_router.include_router(bookings_router)
