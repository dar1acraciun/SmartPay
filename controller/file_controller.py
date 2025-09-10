from fastapi import UploadFile, File as FastAPIFile
import os
from fastapi import HTTPException
from model.file_model import File
from db import SessionLocal
 
UPLOAD_DIR = "files"
 
mastercard_fields = [
    "mc_mti",
    "mc_processing_code",
    "mc_acquirer_bin",
    "mc_issuer_bin",
    "mc_merchant_category_code",
    "mc_merchant_country_code",
    "mc_card_acceptor_id_code",
    "mc_card_acceptor_name_location",
    "mc_transaction_currency_code",
    "mc_settlement_currency_code",
    "mc_transaction_amount",
    "mc_settlement_amount",
    "mc_exchange_rate",
    "mc_presentment_date",
    "mc_pos_entry_mode",
    "mc_eci_indicator",
    "mc_ucaf_collection_indicator",
    "mc_cvv2_result_code",
    "mc_avs_result_code",
    "mc_cross_border_indicator",
    "mc_retrieval_reference_number",
    "mc_auth_id_response",
    "interchange_fee",
    "rate_pct",
    "fixed_fee",
    "mcc_group",
    "downgraded",
    "channel_type",
    "cross_border_flag",
    "eci_3ds_auth"
]
 
visa_fields = [
        "visa_cross_border_indicator",  # binary categorical: 'Y' or 'N'
        "visa_channel_type",  # categorical: 'ecommerce', 'card_present', etc.
        "visa_eci_indicator",  # numeric or ordinal: integer (e.g., 2 to 7)
        "visa_cvv2_result_code",  # categorical: 'M', 'N', 'U', etc.
        "visa_avs_result_code",  # categorical: 'Y', 'N', 'A', 'Z', 'U', etc.
        "visa_pos_entry_mode",  # numeric: e.g., 1 = manual, 5 = chip, 7 = contactless
        "visa_terminal_capability_code",  # numeric: terminal risk profile (low = risky)
        "visa_merchant_category_code",  # categorical: MCC code, can be grouped or one-hot
    ]
 
 
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
            "brand": file.brand,
            "downgraded_transaction": file.downgraded_transaction,
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
                "brand": f.brand,
                "downgraded_transaction": f.downgraded_transaction,
                "timestamp": str(f.timestamp)
            } for f in files
        ]
        return {"files": result}
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()
 
 
import csv
def detect_brand_and_validate_fields(header):
    # Prima coloană decide brandul
    first_col = header[0].lower()
    if first_col.startswith("mc_") or any(f in first_col for f in ["mastercard", "mc_"]):
        brand = "mastercard"
        required_fields = set(mastercard_fields)
    elif first_col.startswith("visa_") or any(f in first_col for f in ["visa", "visa_"]):
        brand = "visa"
        required_fields = set(visa_fields)
    else:
        brand = None
        required_fields = set()
    missing = required_fields - set(header)
    return brand, missing
 
async def upload_file_controller(file: UploadFile = FastAPIFile(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    import datetime
    session = SessionLocal()
    try:
        # Citește headerul CSV direct din UploadFile
        content = await file.read()
        lines = content.decode("utf-8").splitlines()
        reader = csv.reader(lines)
        header = next(reader)
        brand, missing = detect_brand_and_validate_fields(header)
        if not brand:
            raise HTTPException(status_code=400, detail="Could not determine brand from the first column of the CSV.")
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing required fields for {brand}: {', '.join(missing)}")
 
        # Creează fișierul și salvează în DB
        new_file = File(name=file.filename, timestamp=datetime.datetime.now(datetime.timezone.utc))
        new_file.insert_file(session, brand=brand)
        file_path = os.path.join(UPLOAD_DIR, f"{new_file.id}.csv")
        with open(file_path, "wb") as f:
            f.write(content)
        new_file.path = f"/files/{new_file.id}.csv"
        session.commit()
        return {"message": "File uploaded", "file_id": new_file.id, "path": new_file.path, "brand": new_file.brand, "downgraded_transaction": new_file.downgraded_transaction}
    finally:
        session.close()