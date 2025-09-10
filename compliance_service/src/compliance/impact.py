# src/compliance/impact.py
import pandas as pd

def estimate_impact(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["impact_estimated_bps_amt"] = out["amount"] * (out["impact_hint_bps_sum"] / 10000.0)
    out["impact_estimated_per_item_amt"] = out["impact_hint_per_item_sum"]
    out["impact_estimated_total"] = out["impact_estimated_bps_amt"] + out["impact_estimated_per_item_amt"]
    return out
