from fastapi import APIRouter, Cookie, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from src.token import validate_token

router = APIRouter()
templates = Jinja2Templates(directory="templates")


class UserInfo(BaseModel):
    username: str
    access_token: str


@router.get("/", response_class=HTMLResponse)
async def read_items(request: Request, access_token: str = Cookie(default=None)):
    user_data = None
    if access_token:
        res = validate_token(access_token)
        if res.get("status") == 1:
            user_data = {"username": res.get("user")}

    return templates.TemplateResponse(
        request=request, name="mainpage.html", context={"user": user_data}
    )
