from pydantic import BaseModel


class UserData(BaseModel):
    username: str


class NodeData(BaseModel):
    x: int
    y: int
    size: int = 5
    color: str | None = None
