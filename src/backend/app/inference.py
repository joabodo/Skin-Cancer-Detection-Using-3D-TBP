from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from .db import get_db
from .models import Detection, Patient
import torch
from torchvision import transforms
from PIL import Image
import uuid, os

router = APIRouter(prefix="/predict", tags=["predict"])

MODEL_PATH = os.getenv("MODEL_PATH", "/app/model/best_model.pth")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = None
def load_model():
    global model
    if model is None:
        if os.path.exists(MODEL_PATH):
            model = torch.load(MODEL_PATH, map_location=device)
            model.eval()
        else:
            model = None

preprocess = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
])

@router.post("/upload/{patient_id}")
async def predict_upload(patient_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    load_model()
    out_dir = os.getenv("UPLOAD_DIR", "/app/uploads")
    os.makedirs(out_dir, exist_ok=True)
    fname = f"{uuid.uuid4().hex}_{file.filename}"
    path = os.path.join(out_dir, fname)
    with open(path, "wb") as f:
        f.write(await file.read())

    if model is None:
        raise HTTPException(500, "Model not found on server")

    img = Image.open(path).convert("RGB")
    x = preprocess(img).unsqueeze(0).to(device)
    with torch.no_grad():
        out = model(x)
        probs = torch.softmax(out, dim=1).cpu().numpy()[0]
        pred_idx = int(probs.argmax())
        label = "malignant" if pred_idx==1 else "benign"
        confidence = float(probs[pred_idx])

    det = Detection(patient_id=patient_id, image_path=path, prediction=label, confidence=confidence)
    db.add(det); db.commit(); db.refresh(det)
    return {"prediction": label, "confidence": confidence, "detection_id": det.id}
