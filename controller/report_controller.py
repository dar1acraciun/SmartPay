import os
import json
from fastapi import HTTPException

async def get_report_controller(report_id: str):
	if not report_id:
		raise HTTPException(status_code=404, detail="Report not found")
	# Caută fișierul JSON în folderul reports
	report_path = os.path.join(os.path.dirname(__file__), '..', 'reports', f'{report_id}.json')
	report_path = os.path.abspath(report_path)
	if not os.path.exists(report_path):
		raise HTTPException(status_code=404, detail="Report not found")
	try:
		with open(report_path, 'r', encoding='utf-8') as f:
			data = json.load(f)
		return data
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error reading report: {str(e)}")


async def generate_report_controller(source_id: str):
	return {"message": f"Report generation for source file {source_id} is not implemented yet."}

async def get_all_reports_controller():
	session = SessionLocal()
	try:
		reports = session.query(Report).all()
		result = [
			{
				"id": r.id,
				"source_file_id": getattr(r, "source_file_id", None),
				"path": getattr(r, "path", None),
				"brand": getattr(r, "brand", None),
				"timestamp": str(getattr(r, "timestamp", ""))
			} for r in reports
		]
		return {"reports": result}
	except Exception as e:
		return {"error": str(e)}
	finally:
		session.close()


