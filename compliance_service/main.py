# main.py
import argparse
import os, sys
import pandas as pd
import yaml

# permite importul din src/compliance/
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from compliance.facts import derive_facts
from compliance.evaluator import run_rules, SEV_MAP  # <- folosim SEV_MAP din evaluator.py
from compliance.impact import estimate_impact
from compliance.simulate import apply_simulation  # dacă vrei what-if
from compliance.mapper_mastercard import map_mastercard
from compliance.mapper_visa import map_visa


def load_yaml_rules(config_dir):
    with open(f"{config_dir}/rules_common.yaml") as f:
        common = yaml.safe_load(f)["rules"]
    with open(f"{config_dir}/schemes/visa.yaml") as f:
        visa = yaml.safe_load(f)["rules"]
    with open(f"{config_dir}/schemes/mastercard.yaml") as f:
        mc = yaml.safe_load(f)["rules"]
    return common + visa + mc


def load_thresholds(config_dir):
    with open(f"{config_dir}/thresholds.yaml") as f:
        return yaml.safe_load(f)


# auto-detect după prefixele coloanelor
def is_visa_like(df: pd.DataFrame) -> bool:
    return any(str(c).startswith("visa_") for c in df.columns)


def is_mastercard_like(df: pd.DataFrame) -> bool:
    return any(str(c).startswith("mc_") for c in df.columns)


def map_by_format(df_raw: pd.DataFrame, force_format: str | None) -> pd.DataFrame:
    if force_format == "visa":
        return map_visa(df_raw)
    if force_format == "mastercard":
        return map_mastercard(df_raw)
    if force_format in (None, "auto", "raw"):
        # auto-detect: VISA > MC; dacă niciunul, lăsăm raw
        if is_visa_like(df_raw):
            return map_visa(df_raw)
        if is_mastercard_like(df_raw):
            return map_mastercard(df_raw)
        return df_raw
    # fallback
    return df_raw


def main():
    parser = argparse.ArgumentParser(description="Compliance Checker – CSV in, CSV out")
    parser.add_argument("--input", required=True, help="Input transactions CSV path")
    parser.add_argument("--out", required=True, help="Output results CSV path")
    parser.add_argument("--config", default="config", help="Config folder path")
    parser.add_argument("--min_fail_severity", default="MEDIUM",
                        help="LOW/MEDIUM/HIGH/CRITICAL (mark non-compliant if severity >= threshold)")
    parser.add_argument("--force_format", choices=["mastercard","visa","raw","auto"], default="auto",
                        help="Force mapping to a specific scheme or let it auto-detect")
    args = parser.parse_args()

    # 1) load configs
    thresholds = load_thresholds(args.config)
    rules = load_yaml_rules(args.config)

    # 2) load data (raw)
    df_raw = pd.read_csv(args.input)


    # 3) mapping (Visa/Mastercard/Raw)
    df = map_by_format(df_raw, force_format=args.force_format)

    # 3a) asigurăm existența coloanei ID (după mapare, ca să nu fie aruncată de mapper)
    if "id" not in df.columns:
        df["id"] = range(1, len(df) + 1)

    # 4) derive facts
    df1 = derive_facts(df, thresholds)

    # 5) apply rules
    df2 = run_rules(df1, rules, min_fail_severity=args.min_fail_severity)

    # 6) estimate impact
    df3 = estimate_impact(df2)

    # 6a) adăugăm coloana risk_level pe baza COMPLIANCE_FINDINGS (NU 'findings')
    def get_risk_level(findings):
        if not findings:
            return "NONE"

        # normalizăm casing/whitespace și mapăm la rank
        severities = [str(f.get("severity", "")).strip().upper() for f in findings]
        ranks = [SEV_MAP.get(sev, 0) for sev in severities]
        max_rank = max(ranks or [0])

        # ESCALADARE cerută: dacă avem 3+ MEDIUM și nu există HIGH/CRITICAL, urcăm la HIGH
        medium_count = severities.count("MEDIUM")
        if medium_count >= 3 and max_rank < SEV_MAP["HIGH"]:
            max_rank = SEV_MAP["HIGH"]

        return {0: "NONE", 1: "LOW", 2: "MEDIUM", 3: "HIGH", 4: "CRITICAL"}[max_rank]

    def ensure_id_column(df: pd.DataFrame) -> pd.DataFrame:
        d = df.copy()
        if "id" in d.columns:
            d["id"] = d["id"].astype(str)
        else:
            if "transaction_id" in d.columns:
                d.insert(0, "id", d["transaction_id"].astype(str))
            else:
                d.insert(0, "id", [str(i) for i in range(1, len(d) + 1)])
        cols = ["id"] + [c for c in d.columns if c != "id"]
        return d[cols]

    df3 = ensure_id_column(df3)  # <<< AICI apelul, înainte de to_csv

    # aplicăm
    df3["risk_level"] = df3["compliance_findings"].apply(get_risk_level)

    # 7) write output
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    df3.to_csv(args.out, index=False)
    print(f"Done. Wrote {len(df3)} rows to {args.out}")
    print(f"Non-compliant rows: {(~df3['is_compliant']).sum()}")


if __name__ == "__main__":
    main()
