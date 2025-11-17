from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .db import get_db
from .models import User
from .utils import hash_password, verify_password, create_access_token
from .twofactor import generate_totp_secret, get_totp_uri, verify_totp
from datetime import timedelta
import jwt, os
from dotenv import load_dotenv
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "change_me")
JWT_ALGORITHM = "HS256"

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email==email).first():
        raise HTTPException(400, "Email already registered")
    user = User(email=email, hashed_password=hash_password(password), totp_secret=generate_totp_secret())
    db.add(user); db.commit(); db.refresh(user)
    uri = get_totp_uri(user.email, user.totp_secret)
    return {"email": user.email, "totp_uri": uri}

@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email==email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"sub": user.email, "twofa_pending": True}, expires_delta=timedelta(minutes=5))
    return {"twofa_token": token}

@router.post("/verify-2fa")
def verify_2fa(token: str, totp_code: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except Exception:
        raise HTTPException(401, "Invalid token")
    email = payload.get("sub")
    user = db.query(User).filter(User.email==email).first()
    if not user:
        raise HTTPException(401, "Invalid token")
    if verify_totp(user.totp_secret, totp_code):
        access = create_access_token({"sub": user.email})
        return {"access_token": access}
    raise HTTPException(401, "Invalid 2FA code")
