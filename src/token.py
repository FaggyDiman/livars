from datetime import datetime, timedelta, timezone

import jwt

key = "okaym8"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(username: str):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": username, "exp": expire, "type": "access"}
    return jwt.encode(to_encode, key, algorithm=ALGORITHM)


def create_refresh_token(username: str):
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": username, "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, key, algorithm=ALGORITHM)


def validate_token(token: str):
    try:
        payload = jwt.decode(token, key, algorithms=[ALGORITHM])
        return {"status": 1, "user": payload.get("sub"), "type": payload.get("type")}
    except jwt.ExpiredSignatureError:
        return {"status": "expired", "message": "EXPIRED"}
    except jwt.InvalidTokenError:
        return {"status": "invalid", "message": "NON-VALID"}
