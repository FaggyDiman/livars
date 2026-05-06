from fastapi import APIRouter

from .mainpage import router as mainpage_router

api_router = APIRouter()

api_router.include_router(mainpage_router)
