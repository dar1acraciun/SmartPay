# src/compliance/evaluator.py
import pandas as pd
from typing import List, Dict, Any

SEV_MAP = {"LOW":1, "MEDIUM":2, "HIGH":3, "CRITICAL":4}

def _mask(df: pd.DataFrame, expr: str) -> pd.Series:
    expr2 = expr.replace(" and ", " & ").replace(" or ", " | ")
    try:
        return df.eval(expr2)
    except Exception:
        return pd.Series(False, index=df.index)

def run_rules(df: pd.DataFrame, rules: List[Dict[str, Any]], min_fail_severity: str = "MEDIUM") -> pd.DataFrame:
    out = df.copy()
    findings = [[] for _ in range(len(out))]
    hint_bps = [0.0]*len(out)
    hint_fee = [0.0]*len(out)

    for r in rules:
        m = _mask(out, r["when"])
        idxs = out.index[m]
        for i in idxs:
            findings[i].append({
                "id": r["id"],
                "title": r["title"],
                "severity": r["severity"],
                "message": r["message"],
                "remediation": r["remediation"],
                "impact_hint_bps": r.get("impact_hint_bps", 0.0),
                "impact_hint_per_item": r.get("impact_hint_per_item", 0.0),
            })
            hint_bps[i] += r.get("impact_hint_bps", 0.0)
            hint_fee[i] += r.get("impact_hint_per_item", 0.0)

    out["compliance_findings"] = findings
    out["impact_hint_bps_sum"] = hint_bps
    out["impact_hint_per_item_sum"] = hint_fee

    cutoff = SEV_MAP.get(min_fail_severity.upper(), 2)
    noncomp = []
    for fs in findings:
        fail = any(SEV_MAP.get(f["severity"], 2) >= cutoff for f in fs)
        noncomp.append(fail)
    out["is_compliant"] = [not x for x in noncomp]

    out["findings_ids"] = out["compliance_findings"].apply(lambda L: ",".join(f["id"] for f in L) if L else "")
    out["findings_text"] = out["compliance_findings"].apply(lambda L: " | ".join(f["message"] for f in L) if L else "")
    return out
