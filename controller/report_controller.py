import app
from fastapi import HTTPException
from model.report_model import Report
import datetime, uuid
from db import SessionLocal 
    

async def get_report_controller(report_id: str):
	if not report_id:
		raise HTTPException(status_code=404, detail="Report not found")
	session = SessionLocal()
	try:
		report = Report.get_report(session, report_id)
		if not report:
			raise HTTPException(status_code=404, detail="Report not found")
		return {
			"id": report.id,
			"source_file_id": getattr(report, "source_file_id", None),
			"path": getattr(report, "path", None),
			"brand": getattr(report, "brand", None),
			"timestamp": str(getattr(report, "timestamp", ""))
		}
	except Exception as e:
		return {"error": str(e)}
	finally:
		session.close()


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


