# src/compliance/pipeline.py
import yaml, pandas as pd
from .facts import derive_facts
from .evaluator import run_rules
from .impact import estimate_impact

def run_compliance(df: pd.DataFrame, config_dir: str, min_fail_severity: str = "MEDIUM") -> pd.DataFrame:
    thr = yaml.safe_load(open(f"{config_dir}/thresholds.yaml"))
    rules = []
    rules += yaml.safe_load(open(f"{config_dir}/rules_common.yaml"))["rules"]
    rules += yaml.safe_load(open(f"{config_dir}/schemes/visa.yaml"))["rules"]
    rules += yaml.safe_load(open(f"{config_dir}/schemes/mastercard.yaml"))["rules"]

    df1 = derive_facts(df, thr)
    df2 = run_rules(df1, rules, min_fail_severity=min_fail_severity)
    df3 = estimate_impact(df2)
    return df3
