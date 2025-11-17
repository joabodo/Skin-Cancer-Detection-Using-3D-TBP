from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str

class PatientCreate(BaseModel):
    name: str
    dob: Optional[datetime] = None

class DetectionOut(BaseModel):
    id: int
    patient_id: int
    image_path: str
    prediction: str
    confidence: Optional[float]
    created_at: datetime

    class Config:
        orm_mode = True
