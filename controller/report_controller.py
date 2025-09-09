import os
import json
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

    # Caută fișierul CSV în folderul files
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'files', f'{source_id}.csv')
    csv_path = os.path.abspath(csv_path)
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Source CSV file not found")

    try:
        import shutil
        base_path = os.path.join(os.path.dirname(__file__), '..', 'hackathon_mastercard_regressor')
        x_test_path = os.path.join(base_path, "x_test.csv")
        # Copiază fișierul CSV sursă ca x_test.csv
        shutil.copyfile(csv_path, x_test_path)

        generate_shap_explanations(
            model_path=os.path.join(base_path, "xgb_model_interchange_fee_rate.pkl"),
            x_test_path=x_test_path,
            full_txn_path=csv_path
        )

        # Citește fișierul JSON generat (presupunem că se numește shap_per_transaction_only.json)
        json_path = os.path.join(base_path, "shap_per_transaction_only.json")
        if not os.path.exists(json_path):
            return {"error": "JSON report file not found after generation."}
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Salvează conținutul JSON în folderul reports cu numele <source_id>.json
        reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        report_file_path = os.path.join(reports_dir, f"{source_id}.json")
        with open(report_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return {"success": True, "message": "Report JSON saved.", "file": f"{source_id}.json"}
    except Exception as e:
        return {"error": str(e)}


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


