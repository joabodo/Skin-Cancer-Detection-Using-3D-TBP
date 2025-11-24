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

### 🔒 Authentication & Security
- Email + Password authentication  
- **Two-Factor Authentication (TOTP via Google Authenticator)**  
- JWT-based sessions  
- Email verification  
- Forgot password workflow  
- Secure role-based access  
- CORS, rate limiting, logging  

### 🧑‍⚕️ Patient Management
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
↓ /api requests
nginx reverse proxy
↓
backend (FastAPI)
↓
PostgreSQL + Redis
↓
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
```bash
git clone <your-repo-url>
cd Skin-Cancer-Detection-Using-3D-TBP
### 2. Create Environment File
## System Architecture

