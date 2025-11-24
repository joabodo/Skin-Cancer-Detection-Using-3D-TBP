# Skin Cancer Detection System (Full-Stack AI Platform)

## Overview
The **Skin Cancer Detection System** is a full production-ready platform that uses Artificial Intelligence (AI) to classify skin lesions as *benign* or *malignant*.  
It offers an advanced clinician dashboard, secure authentication with **Two-Factor Authentication (2FA)**, patient record management, AI inference with **Grad-CAM explainability**, and admin-level model management.

The platform is built with:

- **Frontend:** React  
- **Backend:** FastAPI (Python)  
- **Database:** PostgreSQL  
- **Caching / Rate Limiting:** Redis  
- **Model Engine:** PyTorch  
- **Reverse Proxy:** Nginx  
- **Deployment:** Docker Compose  
- **CI/CD:** GitHub Actions  

---

## Features

### Authentication & Security
- Email + Password authentication  
- **Two-Factor Authentication (TOTP via Google Authenticator)**  
- JWT-based sessions  
- Email verification  
- Forgot password workflow  
- Secure role-based access  
- CORS, rate limiting, logging  

### Patient Management
- Create and manage patient profiles  
- Upload lesion images  
- View detection history  
- Patient timeline  

### AI Diagnosis
- PyTorch-based classifier  
- Prediction + confidence score  
- Grad-CAM heatmap for explainability  
- Image storage and retrieval  
- Hot model reload  

### Admin Console
- Manage user accounts  
- Upload new AI models  
- Regenerate model cache  
- View logs  

### DevOps & Deployment
- Production-ready Docker Compose  
- Reverse proxy routing (Nginx)  
- Redis rate limiting  
- PostgreSQL persistent storage  
- CI/CD pipeline with GitHub Actions  

---
frontend (React)
/api requests
nginx reverse proxy
backend (FastAPI)
PostgreSQL + Redis
PyTorch AI Model

---

## Requirements
- Docker Desktop  
- Python 3.10+ (for development)  
- Node.js 18+ (for local UI development)  
- 8GB RAM minimum  
- Port 80 open  

---

## Installation

### 1. Clone the Repository

git clone <your-repo-url>
cd Skin-Cancer-Detection

### 2. Create Environment File
cp .env.example .env

Edit .env:
SECRET_KEY=CHANGE_ME
DATABASE_URL=postgresql://skinuser:sk!npass@db/skinapp
MODEL_PATH=/app/model/best_model.pth
UPLOAD_DIR=/app/uploads
REDIS_URL=redis://redis:6379/0
CORS_ORIGINS=*

### 3. Add Your Model

Place your trained model here:
model/best_model.pth

### 4. Run with Docker
docker-compose -f docker-compose.prod.yml up --build -d

### 5. Create Database Tables
docker-compose -f docker-compose.prod.yml exec backend bash
python3 -c "from app.core.database import Base, engine; Base.metadata.create_all(engine)"

## Frontend
Development:
cd frontend
npm install
npm start

## Production:

Served automatically by Nginx on:
http://localhost/

## Pages:

- / → Login
- /register → Create account
- /2fa → Two-factor verification
- /setup-2fa → QR code page
- /dashboard → Overview
- /patient/:id → Patient details
- /profile → User profile
- /admin → Admin console
- /forgot → Forgot password
- /verify?token= → Email verification

## Backend (FastAPI)
Development:
cd backend
uvicorn app.main:app --reload

## API URL:
http://localhost:8000

## Main Endpoints
### Authentication
POST /auth/register
POST /auth/login
POST /auth/verify-2fa
POST /auth/forgot-password
POST /auth/reset-password
POST /auth/verify-email

### User
GET /users/me
PUT /users/me

### Patients
POST /patients/
GET /patients/
GET /patients/{id}/detections

### AI Inference
POST /predict/upload/{patient_id}
POST /predict/gradcam/{detection_id}

### Admin
POST /admin/upload-model

## CI/CD Pipeline

Located at:
.github/workflows/ci-cd.yml

Pipeline includes:
- Lint checks
- Build validation
- Docker image build
- Push to registry
- Optional deploy step

## Project Structure
backend/
  app/
    core/
      config.py
      database.py
      logging_conf.py
    routers/
      auth.py
      patients.py
      inference.py
      users.py
      admin.py
    models.py
    utils.py
    twofactor.py
    main.py
  requirements.txt
  Dockerfile

frontend/
  public/
    index.html
  src/
    api.js
    App.js
    pages/
      Login.js
      Register.js
      TwoFA.js
      Setup2FA.js
      Dashboard.js
      Patient.js
      Admin.js
      ProfileSettings.js
      ForgotPassword.js
      EmailVerification.js
    styles/
      theme.css
  Dockerfile

nginx/
  nginx.conf

docker-compose.prod.yml
.env.example
uploads/
model/

## Troubleshooting
### 502 Bad Gateway
- Ensure frontend container is running
- Ensure public/index.html exists
- Ensure API_BASE = "/api" in frontend

### Missing Python packages
Run:
docker-compose build --no-cache backend

### Database tables missing
Run:
python3 -c "from app.core.database import Base, engine; Base.metadata.create_all(engine)"

### 2FA not verifying
Check device time sync
Ensure secret is stored in DB
