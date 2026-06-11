import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.auth import get_current_user
from src.database import Node, User, engine
from src.models import NodeData

router = APIRouter(prefix="/api", tags=["nodes"])


def get_db():
    from sqlalchemy.orm import sessionmaker

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_random_color():
    """Генерирует случайный цвет в формате #RRGGBB"""
    return f"#{random.randint(0, 0xFFFFFF):06x}"


def check_collision(db: Session, x: int, y: int, radius: int = 50):
    """
    Проверяет, есть ли другие ноды рядом (в радиусе 50px от центра).
    Возвращает True, если коллизия найдена, иначе False.
    """
    nearby_nodes = (
        db.query(Node)
        .filter((Node.x - x) * (Node.x - x) + (Node.y - y) * (Node.y - y) <= radius * radius)
        .all()
    )
    return len(nearby_nodes) > 0


def format_node(node: Node, creator_username: str) -> dict:
    return {
        "id": node.id,
        "x": node.x,
        "y": node.y,
        "size": node.size,
        "color": node.color,
        "creator_id": node.creator_id,
        "creator_username": creator_username,
        "created_at": node.created_at.isoformat() if node.created_at else None,
    }


def update_node_size(db: Session, user_id: int):
    """
    Увеличивает размер ноды на 5px, если прошло 24 часа с последнего увеличения.
    """
    node = db.query(Node).filter(Node.creator_id == user_id).first()
    if node:
        now = datetime.utcnow()
        time_diff = now - node.created_at

        # Проверяем, прошло ли 24 часа
        if time_diff >= timedelta(hours=24):
            growth_periods = int(time_diff.total_seconds() / (24 * 3600))
            node.size = 5 + (growth_periods * 5)
            node.created_at = now
            db.commit()


@router.post("/node/create")
async def create_node(
    node_data: NodeData,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Создает новую ноду для текущего пользователя.
    Только новые зарегистрированные пользователи могут создать точку.
    """
    user = db.query(User).filter(User.id == current_user.get("user_id")).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.created_node:
        raise HTTPException(status_code=400, detail="You already have a node")

    # Проверяем коллизии
    if check_collision(db, node_data.x, node_data.y):
        raise HTTPException(status_code=400, detail="Node collision with existing node")

    # Проверяем границы карты
    if node_data.x < 0 or node_data.x > 2000 or node_data.y < 0 or node_data.y > 1000:
        raise HTTPException(status_code=400, detail="Node position out of bounds")

    # Создаем новую ноду
    color = generate_random_color()
    new_node = Node(
        creator_id=user.id,
        x=node_data.x,
        y=node_data.y,
        size=5,
        color=color,
        created_at=datetime.utcnow(),
    )

    db.add(new_node)
    user.created_node = True
    db.commit()
    db.refresh(new_node)

    return {"status": "ok", "node": format_node(new_node, user.username)}


@router.get("/nodes")
async def get_all_nodes(db: Session = Depends(get_db)):
    """
    Возвращает все ноды на карте с информацией о их позиции и размере.
    """
    rows = db.query(Node, User.username).join(User, Node.creator_id == User.id).all()
    return {"nodes": [format_node(node, username) for node, username in rows]}


@router.get("/node/{node_id}")
async def get_node_details(node_id: int, db: Session = Depends(get_db)):
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    user = db.query(User).filter(User.id == node.creator_id).first()
    creator_username = user.username if user else "unknown"
    return {"node": format_node(node, creator_username)}


@router.post("/node/grow")
async def grow_node(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Увеличивает размер ноды пользователя на 5px (если прошло 24 часа).
    Вызывается при заходе пользователя на сайт каждые 24 часа.
    """
    user_id = current_user.get("user_id")
    update_node_size(db, user_id)

    node = db.query(Node).filter(Node.creator_id == user_id).first()

    if not node:
        return {"status": "no_node", "message": "User has no node"}

    return {"status": "ok", "node": {"id": node.id, "size": node.size, "color": node.color}}
