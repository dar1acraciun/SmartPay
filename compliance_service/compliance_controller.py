# controller/compliance_controller.py
import io, os, sys, uuid
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import pandas as pd
import yaml

# permite import din pachet
BASE_DIR = os.path.dirname(os.path.dirname(__file__))          # smartpay/
PKG_SRC = os.path.join(BASE_DIR, "compliance_service", "src")
sys.path.append(PKG_SRC)

# pipeline
from src.compliance.facts import derive_facts
from src.compliance.evaluator import run_rules
from src.compliance.impact import estimate_impact
from src.compliance.mapper_mastercard import map_mastercard
from src.compliance.mapper_visa import map_visa   # <-- NOU

router = APIRouter(prefix="/api/compliance", tags=["compliance"])

CONFIG_DIR = os.path.join(BASE_DIR, "compliance_service", "config")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

def _load_rules_thresholds():
    with open(os.path.join(CONFIG_DIR, "thresholds.yaml"), encoding="utf-8") as f:
        thresholds = yaml.safe_load(f)
    rules: List[dict] = []
    for rel in ["rules_common.yaml", os.path.join("schemes", "visa.yaml"), os.path.join("schemes", "mastercard.yaml")]:
        with open(os.path.join(CONFIG_DIR, rel), encoding="utf-8") as f:
            rules += yaml.safe_load(f)["rules"]
    return thresholds, rules

THRESHOLDS, RULES = _load_rules_thresholds()

# -------- helpers format detection --------
def is_visa_like(df: pd.DataFrame) -> bool:
    return any(c.startswith("visa_") for c in df.columns)

def is_mastercard_like(df: pd.DataFrame) -> bool:
    return any(c.startswith("mc_") for c in df.columns)

def map_by_format(df_raw: pd.DataFrame, force_format: str) -> pd.DataFrame:
    """Decide mapper-ul: forțat prin parametru sau auto-detect după prefixul coloanelor."""
    force_format = (force_format or "auto").lower()
    if force_format == "visa":
        return map_visa(df_raw)
    if force_format == "mastercard":
        return map_mastercard(df_raw)
    # auto
    if is_visa_like(df_raw):
        return map_visa(df_raw)
    if is_mastercard_like(df_raw):
        return map_mastercard(df_raw)
    # fallback: lasă nemapat (în caz de format necunoscut)
    return df_raw

def _run(df_raw: pd.DataFrame, min_fail_severity="MEDIUM", force_format: str = "auto") -> pd.DataFrame:
    df = map_by_format(df_raw, force_format=force_format)
    df1 = derive_facts(df, THRESHOLDS)
    df2 = run_rules(df1, RULES, min_fail_severity=min_fail_severity)
    df3 = estimate_impact(df2)
    return df3

# -------- response model --------
class CheckSummary(BaseModel):
    rows: int
    non_compliant: int
    compliance_rate: float
    total_estimated_impact: float
    rule_counts: Dict[str, int]
    download: Optional[str] = None
    results: Optional[list] = None

# -------- endpoints --------
@router.get("/health")
def health():
    return {"ok": True}

@router.post("/check", response_model=CheckSummary)
async def check_csv(
    file_id: str = Form(...),
    min_fail_severity: str = Form("MEDIUM"),
    force_format: str = Form("auto"),     # "auto" | "mastercard" | "visa"
    return_csv: bool = Form(False),
):
    # 1) citește fișierul din /files
    files_dir = os.path.join(BASE_DIR, "files")
    file_path = os.path.join(files_dir, f"{file_id}.csv")
    if not os.path.exists(file_path):
        raise HTTPException(404, f"Fișierul cu id '{file_id}' nu există în /files.")
    try:
        df_raw = pd.read_csv(file_path, encoding="utf-8")
    except Exception as e:
        raise HTTPException(400, f"Eroare la citirea fișierului: {e}")

    # 2) rulează pipeline-ul (cu mapping Visa/MC)
    res = _run(df_raw, min_fail_severity=min_fail_severity, force_format=force_format)

    # 3) sumar & (opțional) CSV out
    n = len(res)
    non = int((~res["is_compliant"]).sum()) if n else 0
    impact = float(res.get("impact_estimated_total", pd.Series(0.0, index=res.index)).sum())
    counts = (
        res.get("findings_ids", pd.Series([""]*n)).fillna("").astype(str)
          .str.split(",").explode().value_counts()
          .to_dict()
    )
    counts.pop("", None) if "" in counts else None
    rule_counts = {k:int(v) for k,v in counts.items()}

    # Build per-transaction results array: only transactions with findings (violated rules)
    results = []
    for idx, row in res.iterrows():
        findings = row.get("compliance_findings", [])
        # If findings is a string, try to parse as list (from eval or json)
        if isinstance(findings, str):
            import ast
            try:
                findings_list = ast.literal_eval(findings)
                if isinstance(findings_list, list):
                    findings = findings_list
                else:
                    findings = [findings] if findings else []
            except Exception:
                findings = [findings] if findings else []
        # Only include transactions with non-empty findings list
        if findings and isinstance(findings, list) and len(findings) > 0:
            # Determine riskLevel as the highest severity in findings
            severity_order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
            max_severity = "Unknown"
            if all(isinstance(f, dict) for f in findings):
                severities = [f.get("severity", "Unknown") for f in findings]
                # Pick the highest severity
                if severities:
                    max_sev = max(severities, key=lambda s: severity_order.get(str(s).upper(), 0))
                    max_severity = max_sev
            results.append({
                "id": str(row.get("transaction_id", idx)),
                "riskLevel": max_severity,
                "findings": findings
            })

    download = None
    if return_csv:
        token = uuid.uuid4().hex[:8]
        out_path = os.path.join(REPORTS_DIR, f"results_{token}.csv")
        res.to_csv(out_path, index=False)
        download = out_path

    return CheckSummary(
        rows=n,
        non_compliant=non,
        compliance_rate=((n-non)/n if n else 1.0),
        total_estimated_impact=impact,
        rule_counts=rule_counts,
        download=download,
        results=results,
    )
