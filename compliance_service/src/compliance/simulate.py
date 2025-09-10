# src/compliance/simulate.py
import pandas as pd

def apply_simulation(df: pd.DataFrame, toggles: dict) -> pd.DataFrame:
    sim = df.copy()
    if toggles.get("apply_sca"):
        sim.loc[sim["is_eu_uk"] & sim["is_ecom"], "sca_applied"] = True
    if toggles.get("force_avs"):
        sim.loc[sim["is_ecom"], "avs_used"] = True
    if toggles.get("validate_enhanced"):
        mask = sim["is_commercial"]
        sim.loc[mask, "enhanced_fields_present"] = True
        sim.loc[mask, "enhanced_validated"] = True
    if "reduce_delay_to" in toggles:
        sim["settlement_delay_hours"] = sim["settlement_delay_hours"].clip(upper=int(toggles["reduce_delay_to"]))
    return sim
