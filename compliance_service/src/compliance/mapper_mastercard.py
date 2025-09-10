import pandas as pd
import os, sys

def _norm_and_strip(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase + remove 'mc_' prefix din header-e."""
    d = df.copy()
    d.columns = [str(c).strip().lower() for c in d.columns]
    d.columns = [c[3:] if c.startswith("mc_") else c for c in d.columns]
    return d

def _pick(df: pd.DataFrame, names, default=None):
    """Ia prima coloană existentă dintre aliasuri."""
    for n in names:
        n = n.lower().strip()
        if n in df.columns:
            return df[n]
    return pd.Series([default] * len(df))

def map_mastercard(df_in: pd.DataFrame) -> pd.DataFrame:
    """
    Mapper pentru fișierul tău MC cu headere fixe:
    mc_mti, mc_processing_code, mc_acquirer_bin, mc_issuer_bin, mc_merchant_category_code,
    mc_merchant_country_code, mc_card_acceptor_id_code, mc_card_acceptor_name_location,
    mc_transaction_currency_code, mc_settlement_currency_code, mc_transaction_amount,
    mc_settlement_amount, mc_exchange_rate, mc_presentment_date, mc_pos_entry_mode,
    mc_eci_indicator, mc_ucaf_collection_indicator, mc_cvv2_result_code, mc_avs_result_code,
    mc_cross_border_indicator, mc_retrieval_reference_number, mc_auth_id_response,
    interchange_fee, rate_pct, fixed_fee, downgraded, channel_type, eci_3ds_auth
    """
    df = df_in.copy()

    # --- Merchant & geo ---
    df["merchant_country"] = df["mc_merchant_country_code"].astype(str).str.upper()
    df["card_country"] = pd.NA
    df["issuer_country_source"] = "unknown"

    # 2) caută un tabel bin→country (preferă oficialul; dacă nu există, folosește inferred)
    bin_map = {}
    bin_source = None
    for cand in ["data/bin_table.csv", "data/bin_table_inferred.csv"]:
        if os.path.exists(cand):
            tbl = pd.read_csv(cand, dtype=str)
            tbl.columns = [c.lower().strip() for c in tbl.columns]
            if "bin6" in tbl.columns and "country" in tbl.columns:
                bin_map = dict(zip(tbl["bin6"].str.strip(),
                                   tbl["country"].str.strip().str.upper()))
                bin_source = os.path.basename(cand)
                break

    if bin_map:
        cc = df["mc_issuer_bin"].astype(str).str[:6].map(bin_map)
        df.loc[cc.notna(), "card_country"] = cc
        df.loc[cc.notna(), "issuer_country_source"] = bin_source

    # # 3) fallback final (MVP): dacă nu știm țara cardului, punem "US" ca să nu pice pipeline-ul
    # df["card_country"] = df["card_country"].fillna("US")

    # regiune simplificată
    EU = {"AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IE","IT","LV","LT","LU","MT","NL","PL","PT","RO","SK","SI","ES","SE"}
    df["merchant_region"] = df["merchant_country"].map(
        lambda cc: "UK" if cc == "GB" else ("EU" if cc in EU else ("US" if cc == "US" else "ROW"))
    )

    # --- Amount & currency ---
    df["amount"] = pd.to_numeric(df["mc_transaction_amount"], errors="coerce").fillna(0.0)
    df["currency"] = df["mc_transaction_currency_code"].astype(str).str.upper()
    df["settlement_amount"] = pd.to_numeric(df["mc_settlement_amount"], errors="coerce").fillna(0.0)
    df["settlement_currency"] = df["mc_settlement_currency_code"].astype(str).str.upper()

    # --- Channel / POS ---
    ch_raw = df["channel_type"].astype(str).str.lower()
    df["channel"] = ch_raw.apply(lambda x: "ECOM" if "ecommerce" in x or "ecom" in x else "POS")
    df["pos_entry_mode"] = df["mc_pos_entry_mode"].astype(str)

    # --- AVS / CVV2 ---
    avs = df["mc_avs_result_code"].astype(str).str.upper()
    df["avs_used"] = avs.isin(["Y","Z","A"])  # match / zip-only / addr-only

    # --- ECI / 3DS ---
    eci = df["mc_eci_indicator"].astype(str).str.upper().replace({"NA": "NA"})
    df["eci"] = eci

    # SCA aplicată (demo): eCom și ECI 05/06 sau canal marcat 3DS
    df["sca_applied"] = ((df["channel"] == "ECOM") & (eci.isin(["05","06"]) | ch_raw.str.contains("3ds")))
    df["sca_required"] = None  # se calculează în facts.py

    # --- Commercial flags (simplu) ---
    mcc = df["mc_merchant_category_code"].astype(str)
    df["product"] = "consumer"
    COMM_MCC = {"5045","7399"}  # modifică dacă ai listă internă
    df.loc[mcc.isin(COMM_MCC), "product"] = "commercial_corporate"
    df["enhanced_fields_present"] = False
    df["enhanced_validated"] = False

    # --- Clearing delay ---
    # Nu avem auth_date, deci setăm 0 (ok pentru MVP)
    df["settlement_delay_hours"] = 0.0

    # --- MOTO / MIT ---
    df["moto_indicator"] = df["mc_pos_entry_mode"].astype(str).eq("81")  # schimbă dacă aveți alt flag MOTO
    df["mit_indicator"] = False
    df["mit_expected"] = False

    # --- Cross-border (flag direct din input) ---
    xb = df["mc_cross_border_indicator"].astype(str).str.upper()
    df["cross_border"] = xb.isin(["TRUE","T","1","Y"])

    # --- ID & brand (utile în output) ---
    df["transaction_id"] = df["mc_retrieval_reference_number"].astype(str)
    df["brand"] = "Mastercard"

    return df[[
        # câmpuri așteptate de checker:
        "merchant_country","card_country","merchant_region",
        "amount","currency","settlement_amount","settlement_currency",
        "channel","pos_entry_mode","avs_used","eci","sca_applied","sca_required",
        "product","enhanced_fields_present","enhanced_validated",
        "settlement_delay_hours","moto_indicator","mit_indicator","mit_expected",
        "cross_border","transaction_id","brand"
    ]]
