import joblib
import pandas as pd
import shap
import numpy as np
from sklearn.inspection import permutation_importance

# === Load trained model and test data ===
model = joblib.load("xgb_model_interchange_fee_rate.pkl")
X_test = pd.read_csv("x_test.csv")
y_test = pd.read_csv("y_test.csv").squeeze()

# === Original features used during training ===
FEATURES = [
    "mc_pos_entry_mode",
    "mc_eci_indicator",
    "mc_ucaf_collection_indicator",
    "mc_cvv2_result_code",
    "mc_avs_result_code",
    "mc_cross_border_indicator",
    "mcc_group",
    "channel_type",
]

# === Permutation Importance (Model-Agnostic Global Ranking) ===
result = permutation_importance(
    model, X_test, y_test,
    n_repeats=5,
    random_state=42,
    n_jobs=1
)

importance_df = pd.DataFrame({
    "feature": FEATURES,
    "importance": result.importances_mean,
    "stdev": result.importances_std
}).sort_values("importance", ascending=False)

# === Normalize permutation importance
importance_total = importance_df["importance"].sum()
importance_df["importance_pct"] = 100 * importance_df["importance"] / importance_total
importance_df["importance_pct"] = importance_df["importance_pct"].round(2)

print("\n📊 Top 10 Influential Features (Permutation Importance) [Normalized %]:")
print(importance_df[["feature", "importance_pct", "stdev"]].head(10).to_string(index=False))

# === SHAP Analysis ===
booster = model.named_steps["xgb"]
preprocessor = model.named_steps["preprocessor"]
X_transformed = preprocessor.transform(X_test)
feature_names = preprocessor.get_feature_names_out()

explainer = shap.Explainer(booster)
shap_values = explainer(X_transformed)
shap_df = pd.DataFrame(shap_values.values, columns=feature_names)

# === Detect categorical vs numeric
categorical_features = preprocessor.transformers_[0][2]
numeric_features = preprocessor.transformers_[1][2]

# === SHAP Attribution Per Feature + Value
shap_impact_list = []

print("\n🔍 Feature Value Attribution (SHAP) — All Features:")

for feat in FEATURES:
    if feat not in X_test.columns:
        continue

    if feat in categorical_features:
        for val in X_test[feat].dropna().unique():
            mask = X_test[feat] == val
            val_str = str(val).strip()
            col_matches = [c for c in feature_names if f"{feat}_{val_str}" in c]
            if not col_matches:
                continue
            impact = shap_df[col_matches].loc[mask].sum().sum()
            print(f"   • {feat} = {val_str:<20} → total SHAP impact: {impact:.5f}")
            shap_impact_list.append({
                "feature": feat,
                "value": val_str,
                "shap_total": impact
            })
    else:
        col_matches = [c for c in feature_names if c.endswith(feat)]
        if not col_matches:
            continue
        impact = shap_df[col_matches].sum().sum()
        print(f"   • {feat:<20} → total SHAP impact: {impact:.5f}")
        shap_impact_list.append({
            "feature": feat,
            "value": "ALL",
            "shap_total": impact
        })

# === Normalize SHAP Values
shap_impact_df = pd.DataFrame(shap_impact_list)
shap_impact_df["shap_abs"] = shap_impact_df["shap_total"].abs()
total_abs = shap_impact_df["shap_abs"].sum()
shap_impact_df["shap_pct"] = 100 * shap_impact_df["shap_abs"] / total_abs
shap_impact_df["shap_pct"] = shap_impact_df["shap_pct"].round(2)
shap_impact_df.sort_values("shap_pct", ascending=False, inplace=True)

# === Print Final SHAP Summary
print("\n📤 SHAP impact summary (top, normalized %):")
print(shap_impact_df[["feature", "value", "shap_total", "shap_pct"]].head(100).to_string(index=False))

# Optional export
# importance_df.to_csv("normalized_permutation_importance.csv", index=False)
# shap_impact_df.to_csv("normalized_shap_impact_per_value.csv", index=False)
