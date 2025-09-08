from fastapi import APIRouter, UploadFile, File
from .router import upload_file_controller, get_report_controller, generate_report_controller

router = APIRouter()

@router.post("/files/upload")
async def upload_file(file: UploadFile = File(...)):
    return await upload_file_controller(file)

@router.get("/report/{report_id}")
async def get_report(report_id):
    return await get_report_controller(report_id)

@router.post("/reports/generate/{source_id}")
async def generate_report(source_id: str):
    return await generate_report_controller(source_id)

@router.get("/files/all")
async def get_all_files():
    pass