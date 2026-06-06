import os
from typing import Optional
from datetime import datetime

from sqlalchemy import String, create_engine, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_node: Mapped[bool] = mapped_column(nullable=False, default=False)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r})"


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    size: Mapped[int] = mapped_column(nullable=False, default=5)
    x: Mapped[int] = mapped_column(nullable=False)
    y: Mapped[int] = mapped_column(nullable=False)
    color: Mapped[str] = mapped_column(String(7), nullable=False)

    def __repr__(self) -> str:
        return f"Node(id={self.id!r}, creator_id={self.creator_id!r}, x={self.x}, y={self.y})"


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypassword@localhost:5432/mydatabase")

engine = create_engine(DATABASE_URL)


def init_db():
    Base.metadata.create_all(bind=engine)
