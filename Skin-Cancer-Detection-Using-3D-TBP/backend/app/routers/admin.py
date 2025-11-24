from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models import User
from ..core.config import settings
import os, uuid

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/upload-model")
async def upload_model(file: UploadFile = File(...)):
    if not file.filename.endswith(('.pth','.pt')):
        raise HTTPException(400, "Invalid model file")
    model_dir = os.path.dirname(settings.MODEL_PATH)
    os.makedirs(model_dir, exist_ok=True)
    tmp_path = os.path.join(model_dir, f"{uuid.uuid4().hex}_{file.filename}")
    with open(tmp_path, "wb") as f:
        f.write(await file.read())
    # atomically replace model
    os.replace(tmp_path, settings.MODEL_PATH)
    # signal reload by removing cached model in routers.inference
    try:
        import importlib
        m = importlib.import_module("app.routers.inference")
        if hasattr(m, "_model"):
            setattr(m, "_model", None)
    except Exception:
        pass
    return {"status":"ok", "model_path": settings.MODEL_PATH}
