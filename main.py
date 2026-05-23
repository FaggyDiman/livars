import time

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import OperationalError

from routes import api_router
from src.database import init_db

while True:
    try:
        init_db()
        break
    except OperationalError:
        print("Waiting for database...")
        time.sleep(2)

app = FastAPI()
app.include_router(api_router)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
