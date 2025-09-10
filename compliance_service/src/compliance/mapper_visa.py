# src/compliance/mapper_visa.py
import os
from pathlib import Path
import pandas as pd

# unde căutăm bin_table (același fișier ca pentru MC)
PACKAGE_ROOT = Path(__file__).resolve().parents[2]    # .../ (rădăcina pachetului tău feesense/compliance_checker)
DATA_DIR = PACKAGE_ROOT / "data"

EU = {
    "AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IE","IT",
    "LV","LT","LU","MT","NL","PL","PT","RO","SK","SI","ES","SE"
}

def _merchant_region(cc: str) -> str:
    if not isinstance(cc, str) or cc == "":
        return "ROW"
    cc = cc.upper()
    if cc == "GB": return "UK"
    if cc == "US": return "US"
    return "EU" if cc in EU else "ROW"

def _bool_from_str(s: pd.Series) -> pd.Series:
    return s.astype(str).str.upper().isin(["Y","YES","TRUE","T","1"])

def _load_bin_map():
    for cand in ["bin_table.csv", "bin_table_inferred.csv"]:
        p = DATA_DIR / cand
        if p.exists():
            tbl = pd.read_csv(p, dtype=str)
            tbl.columns = [c.lower().strip() for c in tbl.columns]
            if "bin6" in tbl.columns and "country" in tbl.columns:
                return dict(zip(tbl["bin6"].str.strip(),
                                tbl["country"].str.strip().str.upper()))
    return {}

def map_visa(df_in: pd.DataFrame) -> pd.DataFrame:
    """
    Transformă dataset-ul VISA (clearing-like) la schema internă a Compliance Checker.
    Se așteaptă coloane cu prefix `visa_...` (similar cu fișierul tău).
    """
    df = df_in.copy()

    # ---------- Merchant / geo ----------
    df["merchant_country"] = df["visa_merchant_country_code"].astype(str).str.upper()
    df["merchant_region"]  = df["merchant_country"].map(_merchant_region)

    # ---------- Amount & currency ----------
    df["amount"]   = pd.to_numeric(df.get("visa_transaction_amount", 0), errors="coerce").fillna(0.0)
    df["currency"] = df.get("visa_transaction_currency_code").astype(str)

    # ---------- Brand ----------
    df["brand"] = "Visa"

    # ---------- Channel / POS ----------
    # ai `visa_channel_type` (ex: ecommerce_3ds, ecommerce_non3ds, card_present_chip, swipe etc.)
    ch = df.get("visa_channel_type", "").astype(str).str.lower()
    df["channel"] = ch.map(lambda x: "ECOM" if "ecom" in x else ("POS" if "card_present" in x else "POS"))

    # opțional: pos_entry_mode dacă există (uneori în VISA: 05 chip, 02 swipe, 81 ecom keyed etc.)
    if "visa_pos_entry_mode" in df.columns:
        df["pos_entry_mode"] = df["visa_pos_entry_mode"].astype(str)
    else:
        df["pos_entry_mode"] = ""

    # ---------- AVS / CVV ----------
    # În multe feed-uri: `visa_avs_result_code` în {Y,Z,A,N,U}; `visa_cvv2_result_code` în {M,N,U,P}
    if "visa_avs_result_code" in df.columns:
        df["avs_used"] = df["visa_avs_result_code"].astype(str).str.upper().isin(["Y","Z","A"])
    else:
        df["avs_used"] = False

    # ---------- ECI / 3DS ----------
    # Pentru VISA: 05=Strong, 06=Attempt, 07/00=None
    # Unele feed-uri au `visa_eci_indicator`, altele `visa_eci_3ds_auth`. Le combinăm inteligent.
    eci_col = None
    for c in ["visa_eci_indicator", "visa_eci_3ds_auth"]:
        if c in df.columns:
            eci_col = c; break
    if eci_col:
        df["eci"] = df[eci_col].fillna("NA").astype(str).str.upper().str.zfill(2).replace({"00":"0"})
    else:
        df["eci"] = "NA"

    # `sca_applied`: dacă e eCom și (ECI 05/06) sau channel_type conține "3ds"
    df["sca_applied"] = (df["channel"].eq("ECOM") &
                         (df["eci"].isin(["05","06"]) |
                          ch.str.contains("3ds")))

    # ---------- Product (consumer/commercial) ----------
    # dacă ai `visa_product_code`, poți marca anumite coduri drept "commercial_corporate"
    df["product"] = "consumer"
    commercial_codes = set(["B","C","G","J","K"])  # exemplu: adaptează la codurile voastre
    if "visa_product_code" in df.columns:
        df.loc[df["visa_product_code"].astype(str).str.upper().isin(commercial_codes), "product"] = "commercial_corporate"

    df["enhanced_fields_present"] = False
    df["enhanced_validated"]     = False

    # ---------- Cross-border flag (din fișier) ----------
    # uneori vine ca TRUE/FALSE, alteori ca 1/0. Dacă ai și `issuer_country`, îl copiem.
    if "visa_cross_border_indicator" in df.columns:
        df["cross_border"] = df["visa_cross_border_indicator"].astype(str).str.upper().isin(["TRUE","T","1","Y"])
    else:
        df["cross_border"] = False

    # ---------- BIN → card_country ----------
    # bazat pe visa_issuer_bin (6 digits)
    df["card_country"] = pd.NA
    bin_map = _load_bin_map()
    if bin_map:
        cc = df["visa_issuer_bin"].astype(str).str[:6].map(bin_map)
        df.loc[cc.notna(), "card_country"] = cc

    # dacă fișierul are deja `issuer_country`, poți folosi ca fallback
    if "issuer_country" in df.columns:
        df["card_country"] = df["card_country"].fillna(df["issuer_country"].astype(str).str.upper())

    # ---------- Settlement delay ----------
    # prezentăm delay=0 dacă nu avem auth_date
    if "visa_presentment_date" in df.columns and "visa_auth_date" in df.columns:
        pres = pd.to_datetime(df["visa_presentment_date"], errors="coerce")
        auth = pd.to_datetime(df["visa_auth_date"], errors="coerce")
        df["settlement_delay_hours"] = (pres - auth).dt.total_seconds() / 3600.0
    else:
        df["settlement_delay_hours"] = 0.0

    # ---------- MOTO / MIT ----------
    df["moto_indicator"] = ch.str.contains("moto")
    df["mit_indicator"]  = False
    df["mit_expected"]   = False

    # ---------- IDs / altele utile ----------
    # RRN/ARN – dacă ai 'visa_arn' sau 'visa_retrieval_reference_number'
    if "visa_arn" in df.columns:
        df["transaction_id"] = df["visa_arn"].astype(str)
    elif "visa_retrieval_reference_number" in df.columns:
        df["transaction_id"] = df["visa_retrieval_reference_number"].astype(str)
    else:
        df["transaction_id"] = ""

    # merchant_id & merchant_name (dacă există)
    if "visa_card_acceptor_id_code" in df.columns:
        df["merchant_id"] = df["visa_card_acceptor_id_code"].astype(str)
    if "merchant_name" in df.columns:
        df["merchant_name"] = df["merchant_name"].astype(str)

    return df
