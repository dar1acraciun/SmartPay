# src/compliance/facts.py
import pandas as pd
import numpy as np

EU = {
    "AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IE","IT",
    "LV","LT","LU","MT","NL","PL","PT","RO","SK","SI","ES","SE"
}

def _region_from_country(cc: str) -> str:
    if not isinstance(cc, str) or cc == "":
        return "ROW"
    cc = cc.upper()
    if cc == "GB": return "UK"
    if cc == "US": return "US"
    return "EU" if cc in EU else "ROW"

def _to_bool_series(s, default=False) -> pd.Series:
    if isinstance(s, pd.Series):
        if s.dtype == bool:
            return s
        return s.astype(str).str.upper().isin(["TRUE","T","1","Y"])
    # fallback dacă lipsește coloana
    return pd.Series(default, index=None)

def derive_facts(df: pd.DataFrame, thresholds: dict) -> pd.DataFrame:
    out = df.copy()

    # ---------------------------
    # 0) Praguri din config (cu fallback-uri sigure)
    # ---------------------------
    thr_def = thresholds.get("defaults", {}) if isinstance(thresholds, dict) else {}
    out["cfg_pos_hours"] = thr_def.get("pos_clearing_hours", 24)
    out["cfg_cnp_hours"] = thr_def.get("cnp_clearing_hours", 72)
    low_value_threshold = float(thr_def.get("low_value_threshold", 30))
    # amount numeric
    out["amount"] = pd.to_numeric(out.get("amount", 0), errors="coerce").fillna(0.0)

    # ---------------------------
    # 1) Canale
    # ---------------------------
    ch = out.get("channel", "").astype(str).str.upper()
    out["is_pos"]  = ch.eq("POS")
    out["is_ecom"] = ch.eq("ECOM")
    # MOTO: ia în considerare și flagul din mapper (dacă există)
    out["is_moto"] = out.get("moto_indicator", False)
    if "is_moto" in out.columns and out["is_moto"].dtype != bool:
        out["is_moto"] = _to_bool_series(out["is_moto"], default=False)
    out["is_moto"] = out["is_moto"] | ch.eq("MOTO")

    # ---------------------------
    # 2) Regiuni merchant / issuer
    # ---------------------------
    # merchant_region există deja din mapper; derivăm doar is_eu_uk
    mr = out.get("merchant_region")
    if mr is None:
        out["merchant_region"] = out.get("merchant_country", "").astype(str).map(_region_from_country)
    out["is_eu_uk"] = out["merchant_region"].isin(["EU","UK"])

    # issuer (card) country poate lipsi pe unele rânduri -> tratăm corect
    out["card_country"] = out.get("card_country", pd.Series([np.nan]*len(out))).astype("object")
    out.loc[out["card_country"].astype(str).isin(["", "nan", "None"]), "card_country"] = np.nan

    out["issuer_region"] = out["card_country"].fillna("").astype(str).map(_region_from_country)
    out["issuer_known"]  = out["card_country"].notna()
    out["issuer_eu_uk"]  = out["issuer_region"].isin(["EU","UK"])

    # ---------------------------
    # 3) ECI strength (fără regex warnings)
    #    Visa: 5 = STRONG, 6 = ATTEMPT, 7/0 = NONE
    #    MC:   2 = STRONG, 1 = ATTEMPT, 0 = NONE
    # ---------------------------
    eci = out.get("eci", "NA").astype(str).str.upper().str.strip()
    strong_vals  = {"ECOM_5","ECI5","5","05","ECI2","2","02"}
    attempt_vals = {"ECOM_6","ECI6","6","06","ECI1","1","01"}
    out["eci_strength"] = "NONE"
    out.loc[eci.isin(strong_vals),  "eci_strength"] = "STRONG"
    out.loc[eci.isin(attempt_vals), "eci_strength"] = "ATTEMPT"

    # ---------------------------
    # 4) Cross-border: calc vs. flag
    # ---------------------------
    # normalizează flagul din input la boolean
    cb_flag = _to_bool_series(out.get("cross_border", False), default=False)
    # dacă știm țara issuer-ului (măcar pe unele rânduri), comparăm țările; altfel, fallback pe flag
    if out["issuer_known"].any():
        out["cross_border_calc"] = (out.get("card_country").fillna("") != out.get("merchant_country").fillna(""))
    else:
        out["cross_border_calc"] = cb_flag
    out["cross_border"] = cb_flag  # păstrează flagul normalizat

    # ---------------------------
    # 5) SCA required (EU/UK only, one-leg-out aware)
    # ---------------------------
    low_value = out["amount"] < low_value_threshold
    # dacă NU știm issuer country: dacă merchant e EU/UK și NU e cross-border => tratăm issuer ca EU/UK (domestic)
    issuer_eu_uk_inferred = (~out["issuer_known"]) & out["is_eu_uk"] & (~cb_flag)
    issuer_eu_uk_final    = out["issuer_eu_uk"] | issuer_eu_uk_inferred

    # Dacă sca_required vine deja din mapper, nu-l suprascriem; altfel îl setăm aici
    if "sca_required" not in out.columns:
        out["sca_required"] = (
            out["is_eu_uk"] & issuer_eu_uk_final & out["is_ecom"]
            & (~out["is_moto"]) & (~out.get("mit_indicator", False)) & (~low_value)
        )
    else:
        # asigură boolean
        out["sca_required"] = _to_bool_series(out["sca_required"], default=False)

    # ---------------------------
    # 6) Comercial vs consumer + sanitize booleans
    # ---------------------------
    out["is_commercial"] = out.get("product", "").fillna("").astype(str).str.lower().str.startswith("commercial")

    for col in ["sca_applied","avs_used","enhanced_fields_present","enhanced_validated","mit_indicator"]:
        if col in out.columns:
            out[col] = _to_bool_series(out[col], default=False)
        else:
            out[col] = False

    return out
