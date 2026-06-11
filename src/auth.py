from typing import Optional

import bcrypt
from fastapi import Cookie, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.database import User, engine
from src.token import validate_token


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()

    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(password_bytes, salt)

    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    password_bytes = password.encode("utf-8")

    hash_bytes = password_hash.encode("utf-8")

    return bcrypt.checkpw(password_bytes, hash_bytes)


def get_current_user(access_token: str = Cookie(default=None)) -> dict:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token_data = validate_token(access_token)
    if token_data.get("status") != 1 or token_data.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    username = token_data.get("user")
    with Session(engine) as session:
        user = session.scalar(select(User).where(User.username == username))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        return {"user_id": user.id, "username": user.username}


def register_user(username: str, password: str) -> bool:
    with Session(engine) as session:
        existing_user = session.scalar(select(User).where(User.username == username))

        if existing_user:
            return False

        user = User(
            username=username,
            password_hash=hash_password(password),
        )

        session.add(user)
        session.commit()
        return True


def login_user(username: str, password: str) -> Optional[User]:
    with Session(engine) as session:
        user = session.scalar(select(User).where(User.username == username))

        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user


def update_refresh_token(username: str, token: str):
    with Session(engine) as session:
        user = session.scalar(select(User).where(User.username == username))
        if user:
            user.refresh_token = token
            session.commit()
