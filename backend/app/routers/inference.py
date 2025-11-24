from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models import Detection, Patient
import torch
from torchvision import transforms
from PIL import Image
import uuid, os
from ..core.config import settings
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

router = APIRouter(prefix="/predict", tags=["predict"])

MODEL_PATH = settings.MODEL_PATH
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_model = None

def load_model():
    global _model
    if _model is None:
        if os.path.exists(MODEL_PATH):
            try:
                _model = torch.load(MODEL_PATH, map_location=device)
                _model.eval()
            except Exception:
                from torchvision import models
                m = models.resnet18(weights=None)
                m.fc = torch.nn.Linear(m.fc.in_features, 2)
                m.load_state_dict(torch.load(MODEL_PATH, map_location=device))
                m.eval()
                _model = m
        else:
            _model = None

preprocess = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
])

@router.post("/upload/{patient_id}")
async def predict_upload(patient_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    load_model()
    out_dir = settings.UPLOAD_DIR
    os.makedirs(out_dir, exist_ok=True)
    fname = f"{uuid.uuid4().hex}_{file.filename}"
    path = os.path.join(out_dir, fname)
    with open(path, "wb") as f:
        f.write(await file.read())

    if _model is None:
        raise HTTPException(500, "Model not found on server")

    img = Image.open(path).convert("RGB")
    x = preprocess(img).unsqueeze(0).to(device)
    with torch.no_grad():
        out = _model(x)
        probs = torch.softmax(out, dim=1).cpu().numpy()[0]
        pred_idx = int(probs.argmax())
        label = "malignant" if pred_idx==1 else "benign"
        confidence = float(probs[pred_idx])

    det = Detection(patient_id=patient_id, image_path=path, prediction=label, confidence=confidence)
    db.add(det); db.commit(); db.refresh(det)
    return {"prediction": label, "confidence": confidence, "detection_id": det.id}

# Grad-CAM implementation
def get_last_conv_name(model):
    for name, module in reversed(list(model.named_modules())):
        if isinstance(module, torch.nn.Conv2d):
            return name
    return None

def compute_gradcam(model, input_tensor, class_idx=None):
    model.eval()
    # find last conv
    last_conv = None
    last_conv_name = get_last_conv_name(model)
    if last_conv_name is None:
        raise RuntimeError("No conv layer found for Grad-CAM")
    activations = {}
    gradients = {}

    def save_activation(name):
        def hook(module, input, output):
            activations[name] = output.detach()
        return hook

    def save_gradient(name):
        def hook(module, grad_in, grad_out):
            gradients[name] = grad_out[0].detach()
        return hook

    for name, module in model.named_modules():
        if name == last_conv_name:
            module.register_forward_hook(save_activation(name))
            module.register_full_backward_hook(save_gradient(name))

    outputs = model(input_tensor)
    if class_idx is None:
        class_idx = int(outputs.argmax(dim=1).item())
    loss = outputs[0, class_idx]
    model.zero_grad()
    loss.backward(retain_graph=True)

    act = activations[last_conv_name][0].cpu().numpy()
    grad = gradients[last_conv_name][0].cpu().numpy()
    weights = np.mean(grad, axis=(1,2))
    cam = np.zeros(act.shape[1:], dtype=np.float32)
    for i, w in enumerate(weights):
        cam += w * act[i, :, :]
    cam = np.maximum(cam, 0)
    cam = cv2.resize(cam, (input_tensor.shape[3], input_tensor.shape[2]))
    cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
    return cam

@router.post("/gradcam/{detection_id}")
def gradcam(detection_id: int, db: Session = Depends(get_db)):
    det = db.query(Detection).filter(Detection.id==detection_id).first()
    if not det:
        raise HTTPException(404, "Detection not found")
    load_model()
    if _model is None:
        raise HTTPException(500, "Model not loaded")
    # load image
    img = Image.open(det.image_path).convert("RGB")
    x = preprocess(img).unsqueeze(0).to(device)
    cam = compute_gradcam(_model, x, None)
    # overlay heatmap
    img_np = np.array(img.resize((x.shape[3], x.shape[2]))).astype(np.float32)/255.0
    heatmap = plt.cm.jet(cam)[:,:,:3]
    overlay = (0.6*heatmap + 0.4*img_np).clip(0,1)
    out_path = det.image_path + "_gradcam.png"
    plt.imsave(out_path, overlay)
    return {"gradcam_path": out_path}
