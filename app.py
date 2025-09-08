from fastapi import FastAPI
from controller import router
from fastapi.middleware.cors import CORSMiddleware

from db import SessionLocal

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Înregistrează rutele definite în controller/routes.py
app.include_router(router.router)

# Pentru rulare locală cu: uvicorn app:app --reload