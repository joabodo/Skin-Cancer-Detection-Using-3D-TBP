from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models import User
from ..utils import hash_password, verify_password, create_access_token, decode_token
from ..twofactor import generate_totp_secret, verify_totp, get_totp_uri

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------- REGISTER ----------
@router.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(400, "Email already registered")

    secret = generate_totp_secret()

    user = User(
        email=email,
        hashed_password=hash_password(password),
        totp_secret=secret,
        email_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    uri = get_totp_uri(email, secret)

    return {"email": email, "totp_uri": uri}


# ---------- LOGIN ----------
@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(401, "Invalid credentials")
    if not verify_password(password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token({"sub": email, "twofa_pending": True}, expires_minutes=5)
    return {"twofa_token": token}


# ---------- VERIFY 2FA ----------
@router.post("/verify-2fa")
def verify2fa(token: str, totp_code: str, db: Session = Depends(get_db)):
    payload = decode_token(token)
    if "twofa_pending" not in payload:
        raise HTTPException(401, "Invalid login stage")

    email = payload["sub"]
    user = db.query(User).filter(User.email == email).first()

    if not verify_totp(user.totp_secret, totp_code):
        raise HTTPException(401, "Invalid 2FA code")

    final_token = create_access_token({"sub": email})
    return {"access_token": final_token}
