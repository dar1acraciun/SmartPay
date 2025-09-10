import os
import json
from fastapi import HTTPException
from hackathon_mastercard_regressor.evaluate_model import generate_shap_explanations as generate_shap_explanations_mc
from hackathon_visa_regressor.evaluate_model import generate_shap_explanations as generate_shap_explanations_visa
from model.report_model import Report
from model.file_model import File
import datetime, uuid
from db import SessionLocal
import pandas as pd
import json

FEATURES_MASTERCARD = [
    "mc_pos_entry_mode",
    "mc_eci_indicator",
    "mc_ucaf_collection_indicator",
    "mc_cvv2_result_code",
    "mc_avs_result_code",
    "mc_cross_border_indicator",
    "mcc_group",
    "channel_type",
]

FEATURES_VISA = [
        "visa_cross_border_indicator",  # binary categorical: 'Y' or 'N'
        "visa_channel_type",  # categorical: 'ecommerce', 'card_present', etc.
        "visa_eci_indicator",  # numeric or ordinal: integer (e.g., 2 to 7)
        "visa_cvv2_result_code",  # categorical: 'M', 'N', 'U', etc.
        "visa_avs_result_code",  # categorical: 'Y', 'N', 'A', 'Z', 'U', etc.
        "visa_pos_entry_mode",  # numeric: e.g., 1 = manual, 5 = chip, 7 = contactless
        "visa_terminal_capability_code",  # numeric: terminal risk profile (low = risky)
        "visa_merchant_category_code",  # categorical: MCC code, can be grouped or one-hot
    ]
    

UPLOAD_DIR = "reports"


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

def save_report_json(report_json, report_id):
    reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, f"{report_id}.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_json, f, ensure_ascii=False, indent=2)

async def generate_report_controller(source_id: str) -> str:
    
    if not source_id:
        raise HTTPException(status_code=400, detail="Missing source_id")
    file = File.get_file(SessionLocal(), source_id)
    if not file:
        raise HTTPException(status_code=404, detail="Source file not found in database")
    

    # Caută fișierul CSV în folderul files
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'files', f'{file.id}.csv')
    csv_path = os.path.abspath(csv_path)
    file_source = pd.read_csv(csv_path)
    file_only_features = None
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Source CSV file not found")

    report_json = {}
    if file.brand.lower() == "mastercard":
        file_only_features = file_source[FEATURES_MASTERCARD]
        base_path = os.path.join(os.path.dirname(__file__), '..', 'hackathon_mastercard_regressor')
        report_json = generate_shap_explanations_mc(
            model_path=os.path.join(base_path, "xgb_model_interchange_fee_rate.pkl"),
            file_only_features=file_only_features,
            file_source=file_source
        )
    elif file.brand.lower() == "visa":
        file_only_features = file_source[FEATURES_VISA]
        base_path = os.path.join(os.path.dirname(__file__), '..', 'hackathon_visa_regressor')
        report_json = generate_shap_explanations_visa(
            model_path=os.path.join(base_path, "xgb_model_interchange_fee_rate.pkl"),
            x_file=file_only_features,
            full_file=file_source
        )
    
    with SessionLocal() as session:
        report = Report(
            source_file=source_id,
            timestamp=datetime.datetime.utcnow(),
            brand=file.brand
        )
        report.insert_report(session, file.brand)
        report.path = f"/reports/{report.id}.json"
        session.commit()
        file_db = File.get_file(session, source_id)
        if file_db:
            file_db.update_transaction(session, report_json)
            session.commit()
        save_report_json(report_json, report.id)
        return {"message": "Report JSON saved.", "report_id": report.id, "path": report.path}
    
	#Error if not returned
    return HTTPException(status_code=500, detail="Failed to generate report")


async def get_all_reports_controller():
    session = SessionLocal()
    try:
        reports = session.query(Report).all()
        result = [
            {
                "id": r.id,
                "source_file": getattr(r, "source_file", None),
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


