from fastapi import FastAPI
from .db import Base, engine
from .auth import router as auth_router
from .inference import router as infer_router

app = FastAPI(title="Skin Cancer Detection API")

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(infer_router)
