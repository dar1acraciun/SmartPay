import os
import json
from pathlib import Path
from model.file_model import File
from db import SessionLocal
from fastapi import HTTPException
from hackathon_mastercard_regressor.evaluate_model import generate_shap_explanations
from model.report_model import Report
import datetime, uuid
from db import SessionLocal
import json


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


async def generate_report_controller(source_id: str) -> str:
    if not source_id:
        raise HTTPException(status_code=400, detail="Missing source_id")


    BASE_DIR = Path(__file__).resolve().parent
    session = SessionLocal()
    file = File.get_file(session, source_id)
    try:
        if file.brand == "mastercard":
            pkg_dir = (BASE_DIR / ".." / "hackathon_mastercard_regressor").resolve()
            from hackathon_mastercard_regressor.evaluate_model import generate_shap_explanations
            generate_shap_explanations(
                model_path=os.path.join(pkg_dir, "xgb_model_interchange_fee_rate.pkl"),
                x_test_path=os.path.join(pkg_dir, "x_test.csv"),
                full_txn_path=os.path.join(pkg_dir, "mastercard_transactions.csv")
            )
        elif file.brand == "visa":
            pkg_dir = (BASE_DIR / ".." / "hackathon_visa_regressor").resolve()
            from hackathon_visa_regressor.evaluate_model import generate_shap_explanations
            generate_shap_explanations(
                model_path=os.path.join(pkg_dir, "xgb_model_interchange_fee_rate.pkl"),
                x_test_path=os.path.join(pkg_dir, "x_test.csv"),
                full_txn_path=os.path.join(pkg_dir, "visa_transactions.csv")
            )

        report = Report(source_file=source_id, timestamp=datetime.datetime.now(datetime.timezone.utc))
        report.insert_report(session, brand="mastercard")

        return report.id
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()


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


