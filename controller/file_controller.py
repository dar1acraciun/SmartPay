from fastapi import UploadFile, File as FastAPIFile
import os
from fastapi import HTTPException
from model.file_model import File
from db import SessionLocal

UPLOAD_DIR = "files"

async def get_file(file_id: str):
    if not file_id:
        raise HTTPException(status_code=404, detail="File not found")
    session = SessionLocal()
    try:
        file = File.get_file(session, file_id)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        return {
            "id": file.id,
            "name": file.name,
            "path": file.path,
            "timestamp": str(file.timestamp)
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

async def get_all_files_controller():
    session = SessionLocal()
    try:
        files = File.get_files(session)
        result = [
            {
                "id": f.id,
                "name": f.name,
                "path": f.path,
                "timestamp": str(f.timestamp)
            } for f in files
        ]
        return {"files": result}
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

async def upload_file_controller(file: UploadFile = FastAPIFile(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    import datetime
    session = SessionLocal()
    try:
        new_file = File(name=file.filename, timestamp=datetime.datetime.now(datetime.timezone.utc))
        new_file.insert_file(session)
        # id-ul este generat automat de SQLAlchemy
        file_path = os.path.join(UPLOAD_DIR, f"{new_file.id}.csv")
        with open(file_path, "wb") as f:
            f.write(await file.read())
        new_file.path = f"/files/{new_file.id}.csv"
        session.commit()  # salvează path-ul actualizat
        # returnează id-ul și path-ul cât timp sesiunea e deschisă
        return {"message": "File uploaded", "file_id": new_file.id, "path": new_file.path}
    finally:
        session.close()