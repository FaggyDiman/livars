from fastapi import APIRouter, Cookie, Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from src.auth import login_user, register_user, update_refresh_token
from src.token import create_access_token, create_refresh_token, validate_token

router = APIRouter()
templates = Jinja2Templates(directory="templates")


class RegisterData(BaseModel):
    username: str
    password: str


class LoginData(BaseModel):
    username: str
    password: str


@router.post("/register")
async def register_endpoint(data: RegisterData):

    success = register_user(
        username=data.username,
        password=data.password,
    )

    if not success:
        return {
            "status": "error",
            "message": "user already exists",
        }

    return {
        "status": "ok",
    }


@router.post("/login")
async def login_endpoint(data: LoginData, response: Response):

    user = login_user(
        username=data.username,
        password=data.password,
    )

    if not user:
        return {
            "status": "error",
            "message": "invalid credentials",
        }

    access_token = create_access_token(user.username)
    refresh_token = create_refresh_token(user.username)

    update_refresh_token(user.username, refresh_token)

    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    return {
        "status": "ok",
    }


@router.post("/logout")
async def logout_endpoint(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"status": "ok"}


@router.get("/getme")
async def get_user_data(access_token=Cookie(default=None)):
    if not access_token:
        return {"authorized": False}
    else:
        return validate_token(access_token)
