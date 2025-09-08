from fastapi import FastAPI
from controller import routes  # presupunem că ai un fișier routes.py în controller/

app = FastAPI()

# Înregistrează rutele definite în controller/routes.py
app.include_router(routes.router)

# Pentru rulare locală cu: uvicorn app:app --reload