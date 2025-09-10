import joblib
import pandas as pd
import shap
import numpy as np
import json
from sklearn.inspection import permutation_importance


def generate_shap_explanations(model_path, x_file, full_file):
    # === Load model and data ===
    model = joblib.load(model_path)
    X_test = x_file
    df_txn = full_file

    print(x_file.head())

    y_pred = model.predict(X_test)

    # === Features used in the model ===
    FEATURES = [
        "visa_cross_border_indicator",  # binary categorical: 'Y' or 'N'
        "visa_channel_type",  # categorical: 'ecommerce', 'card_present', etc.
        "visa_eci_indicator",  # numeric or ordinal: integer (e.g., 2 to 7)
        "visa_cvv2_result_code",  # categorical: 'M', 'N', 'U', etc.
        "visa_avs_result_code",  # categorical: 'Y', 'N', 'A', 'Z', 'U', etc.
        "visa_pos_entry_mode",  # numeric: e.g., 1 = manual, 5 = chip, 7 = contactless
        "visa_terminal_capability_code",  # numeric: terminal risk profile (low = risky)
        "visa_merchant_category_code",  # categorical: MCC code, can be grouped or one-hot
    ]

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

    # === Compute global SHAP impact per feature value
    shap_impact_list = []
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
            shap_impact_list.append({
                "feature": feat,
                "value": "ALL",
                "shap_total": impact
            })

    print(shap_impact_list)

    # === Normalize SHAP values
    shap_impact_df = pd.DataFrame(shap_impact_list)
    shap_impact_df["shap_abs"] = shap_impact_df["shap_total"].abs()
    total_abs = shap_impact_df["shap_abs"].sum()
    shap_impact_df["shap_pct"] = (100 * shap_impact_df["shap_abs"] / total_abs).round(2)
    shap_impact_df.sort_values("shap_pct", ascending=False, inplace=True)

    # === Feature value reasons
    feature_reasons = {
        "cat__visa_cvv2_result_code_M": {"1.0": "CVV2 matched (M): Cardholder authentication successful."},
        "cat__visa_cvv2_result_code_N": {"1.0": "CVV2 did not match (N): Indicates potential fraud."},
        "cat__visa_cvv2_result_code_U": {"1.0": "CVV2 unavailable (U): May increase risk score."},

        "cat__visa_avs_result_code_Y": {"1.0": "AVS full match (Y): Billing address verified."},
        "cat__visa_avs_result_code_N": {"1.0": "AVS no match (N): Address verification failed."},
        "cat__visa_avs_result_code_A": {"1.0": "AVS partial match (A): Address number matched, ZIP failed."},
        "cat__visa_avs_result_code_Z": {"1.0": "AVS ZIP-only match (Z): ZIP matched, address did not."},
        "cat__visa_avs_result_code_U": {"1.0": "AVS unavailable (U): Address verification was not performed."},

        "cat__visa_channel_type_card_present": {"1.0": "Transaction was card-present (e.g., in-store)."},
        "cat__visa_channel_type_ecommerce": {"1.0": "E-commerce (card-not-present): Higher fraud risk."},

        "num__visa_pos_entry_mode": {"other": "How the card was entered (manual, chip, contactless)."},
        "num__visa_eci_indicator": {"other": "ECI indicates e-commerce security (lower = riskier)."},
        "num__visa_terminal_capability_code": {"other": "Device capability for fraud prevention (higher = better)."},
        "cat__visa_cross_border_indicator_Y": { "1.0":  "Transaction is cross-border: higher cost & risk."},
        "cat__visa_cross_border_indicator_N": { "1.0": "Transaction is  not cross-border: lower cost & risk."},
        "num__visa_merchant_category_code": {"other": "Defines type of merchant (e.g., grocery, travel, gambling)."},
    }

    # === Feature-level reasons (for global overview)
    feature_only_reasons = {
        "visa_cross_border_indicator": "Whether the transaction was international (higher risk and fees).",
        "visa_channel_type": "Transaction channel type (e.g., ecommerce or card-present).",
        "visa_eci_indicator": "Electronic Commerce Indicator (ECI) reflects transaction security.",
        "visa_cvv2_result_code": "Outcome of CVV2 security check (match, no match, unavailable).",
        "visa_avs_result_code": "Result of address verification system (AVS) used during checkout.",
        "visa_pos_entry_mode": "Method of card entry (manual, chip, swipe, contactless).",
        "visa_terminal_capability_code": "Security features supported by the terminal (e.g., EMV, NFC).",
        "visa_merchant_category_code": "Merchant category code (defines merchant business type).",
    }

    # === GLOBAL JSON — feature only (normalized, sorted)
    shap_feature_df = (
        shap_impact_df
        .groupby("feature", as_index=False)
        .agg({"shap_total": lambda x: np.sum(np.abs(x))})
        .rename(columns={"shap_total": "shap_abs"})
    )
    total_overall = shap_feature_df["shap_abs"].sum()
    norm_vals = [row["shap_abs"] / total_overall if total_overall else 0.0 for _, row in shap_feature_df.iterrows()]
    rounded = [round(v, 2) for v in norm_vals]
    diff = round(1.0 - sum(rounded), 2)
    if rounded:
        rounded[-1] += diff
    overall_features = []
    for i, (_, row) in enumerate(shap_feature_df.iterrows()):
        feature = row['feature']
        reason = feature_only_reasons.get(feature, "")
        overall_features.append({
            "feature_name": feature,
            "feature_reason": reason,
            "importance_normalized": float(rounded[i])
        })
    overall_features.sort(key=lambda x: x["importance_normalized"], reverse=True)

    global_json = {
        "overall": {
            "features": overall_features
        },
        "per_transaction": []
    }


    # === PER TRANSACTION JSON
    shap_lookup_pct = {
        f"{row['feature']}_{row['value']}": row["shap_pct"]
        for _, row in shap_impact_df.iterrows()
    }


    per_transaction_json = []
    for idx in range(min(len(df_txn), len(shap_df))):
        row = df_txn.iloc[idx]
        txn_features = []
        txn_importances = []

        for feat in FEATURES:
            if feat not in row:
                continue

            val = row[feat]
            val_str = str(val).strip()

            if feat in categorical_features:
                lookup_key = f"{feat}_{val_str}"
                key = f"cat__{feat}_{val_str}"
                reason = feature_reasons.get(key, {}).get("1.0", "")
            else:
                lookup_key = f"{feat}_ALL"
                key = f"num__{feat}"
                reason = feature_reasons.get(key, {}).get(str(val)) or feature_reasons.get(key, {}).get("other", "")

            shap_val = float(shap_lookup_pct.get(lookup_key, 0.0))
            txn_importances.append(abs(shap_val))
            txn_features.append({
                "feature_name": feat,
                "feature_value": val_str,
                "feature_reason": reason,
                "importance_normalized": shap_val  # will normalize below
            })

        # Normalize transaction feature importances to sum to exactly 1.0 (float, 2 decimals)
        total_txn = sum(txn_importances)
        norm_vals = [v / total_txn if total_txn else 0.0 for v in txn_importances]
        rounded_txn = [round(v, 2) for v in norm_vals]
        diff_txn = round(1.0 - sum(rounded_txn), 2)
        if rounded_txn:
            rounded_txn[-1] += diff_txn
        for i, f in enumerate(txn_features):
            f["importance_normalized"] = float(rounded_txn[i])
        txn_features.sort(key=lambda x: x["importance_normalized"], reverse=True)

        # Calculate downgrade (same logic as Mastercard: bool(row.get("downgrade", False)))
        downgrade = bool(row.get("downgrade", False))

        currency = row.get("currency", "N/A")
        actual_fee = row.get("fee_rate", "N/A")
        predicted_fee = float(y_pred[idx])

        per_transaction_json.append({
            "transaction_index": int(idx),
            "currency": currency,
            "actual_fee": actual_fee,
            "predicted_fee": predicted_fee,
            "downgrade": downgrade,
            "transaction_features": txn_features
        })

    per_txn_json = {
        "per_transaction": per_transaction_json
    }

    merged_json = {
        "overall": global_json.get("overall", {}),
        "per_transaction": per_txn_json.get("per_transaction", [])

    }

    with open("shap_all_with_transactions.json", "w") as f:
        json.dump(merged_json, f, indent=2)

    return merged_json

