from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..utils import decode_token
from ..models import User

router = APIRouter(prefix="/users", tags=["users"])


def get_current_user(token: str, db: Session):
    payload = decode_token(token)
    email = payload["sub"]
    user = db.query(User).filter(User.email == email).first()
    return user


@router.get("/me")
def me(authorization: str = "", db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    return get_current_user(token, db)


@router.put("/me")
def update_me(payload: dict, authorization: str = "", db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    user = get_current_user(token, db)

    # Updatable fields
    user.name = payload.get("name", user.name)
    db.commit()
    db.refresh(user)
    return {"ok": True}
