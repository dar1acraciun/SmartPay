from fastapi import APIRouter, UploadFile, File
from controller.file_controller import upload_file_controller, get_all_files_controller, get_file
from controller.report_controller import get_report_controller, generate_report_controller, get_all_reports_controller

files_router = APIRouter(prefix="/files", tags=["Files"])
reports_router = APIRouter(prefix="/reports", tags=["Reports"])

# Files routes
@files_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    return await upload_file_controller(file)

@files_router.get("/all")
async def get_all_files():
    return await get_all_files_controller()

@files_router.get("/{file_id}")
async def get_file_route(file_id: str):
    return await get_file(file_id)

# Reports routes
@reports_router.get("/all")
async def get_all_reports():
    return await get_all_reports_controller()

@reports_router.get("/{report_id}")
async def get_report(report_id):
    return await get_report_controller(report_id)

@reports_router.post("/generate/{source_id}")
async def generate_report(source_id: str):
    return await generate_report_controller(source_id)

# Include routers in main router
from fastapi import APIRouter
router = APIRouter()
router.include_router(files_router)
router.include_router(reports_router)