from fastapi import APIRouter

from .mainpage import router as mainpage_router
from .user_auth import router as user_auth_router

api_router = APIRouter()

api_router.include_router(mainpage_router)
api_router.include_router(user_auth_router)
