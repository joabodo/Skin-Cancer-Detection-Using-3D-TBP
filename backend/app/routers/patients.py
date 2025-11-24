from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from app.models import Patient, Detection
from app.schemas import PatientCreate, DetectionOut
from typing import List

router = APIRouter(prefix="/patients", tags=["patients"])

@router.post("/", response_model=dict)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    p = Patient(name=payload.name, dob=payload.dob)
    db.add(p); db.commit(); db.refresh(p)
    return {"id": p.id, "name": p.name}

@router.get("/{patient_id}/detections", response_model=List[DetectionOut])
def list_detections(patient_id: int, db: Session = Depends(get_db)):
    dets = db.query(Detection).filter(Detection.patient_id==patient_id).order_by(Detection.created_at.desc()).all()
    return dets
