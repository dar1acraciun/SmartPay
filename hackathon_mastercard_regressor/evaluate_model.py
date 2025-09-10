import joblib
import pandas as pd
import shap
import numpy as np
import json
from sklearn.inspection import permutation_importance


def generate_shap_explanations(model_path, file_only_features, file_source):
    # === Load model and data ===
    model = joblib.load(model_path)
    X_test = file_only_features
    df_txn = file_source

    #save in csv file only features
    df_txn.to_csv("file_only_features_123.csv", index=False)

    # Ensure model is a pipeline and has a preprocessor step
    if not hasattr(model, 'named_steps') or 'preprocessor' not in model.named_steps:
        raise ValueError("Loaded model is not a pipeline with a 'preprocessor' step. Please check your model export.")

    # Pass raw features to pipeline for prediction
    try:
        y_pred = model.predict(X_test)
        #save y_pred to file
        np.savetxt("y_pred.csv", y_pred, delimiter=",")
    except ValueError as e:
        raise ValueError(f"Error during prediction. Ensure X_test contains raw, unencoded features matching the pipeline's expected columns. Details: {e}")

    # === Features used in the model ===
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

    # === Normalize SHAP values
    shap_impact_df = pd.DataFrame(shap_impact_list)
    shap_impact_df["shap_abs"] = shap_impact_df["shap_total"].abs()
    total_abs = shap_impact_df["shap_abs"].sum()
    shap_impact_df["shap_pct"] = (100 * shap_impact_df["shap_abs"] / total_abs).round(2)
    shap_impact_df.sort_values("shap_pct", ascending=False, inplace=True)

    # === Feature value reasons
    feature_reasons = {
        "cat__mc_cvv2_result_code_M": {
            "1.0": "CVV2 matched (M). The security code provided by the cardholder matched the issuer’s records. This strongly indicates that the buyer had the physical card details, reducing fraud probability and lowering the interchange fee.",
            "0.0": "CVV2 match (M) did not apply. Without this confirmation, the transaction does not benefit from the reduced fraud risk normally associated with a positive match."
        },
        "cat__mc_cvv2_result_code_N": {
            "1.0": "CVV2 did not match (N). A mismatch signals possible misuse or mistyping, which raises fraud and dispute likelihood. Issuers price for this higher risk by applying higher interchange fees.",
            "0.0": "No CVV2 mismatch detected. The absence of this negative signal helps avoid higher fee pressure."
        },
        "cat__mc_cvv2_result_code_P": {
            "1.0": "CVV2 was not processed (P). Skipping this check removes an important fraud control, creating more uncertainty for the issuer and pushing fees higher.",
            "0.0": "The transaction did not skip CVV2 processing, so it avoids the higher risk pricing that comes from missing this verification."
        },
        "cat__mc_cvv2_result_code_U": {
            "1.0": "CVV2 not provided/available (U). Without this code, issuers lose a key fraud detection tool. This uncertainty increases expected fraud losses and leads to higher interchange.",
            "0.0": "The CVV2 was provided or processed, helping maintain lower expected fee levels."
        },
        "cat__mc_avs_result_code_A": {
            "1.0": "AVS partial match (A). Some address details matched, giving limited reassurance. Risk remains higher than with a full match, so fee reductions are limited.",
            "0.0": "No partial AVS match applied for this transaction."
        },
        "cat__mc_avs_result_code_N": {
            "1.0": "AVS did not match (N). The billing address provided does not align with issuer records, which is a strong fraud signal. This increases issuer exposure and raises the interchange fee.",
            "0.0": "No AVS mismatch. The transaction avoids this high-risk outcome."
        },
        "cat__mc_avs_result_code_R": {
            "1.0": "AVS system unavailable (R). When address verification cannot be checked, issuers face more uncertainty and treat the transaction as higher risk. This leads to higher fees.",
            "0.0": "The AVS system was available or not relevant, avoiding the uncertainty premium."
        },
        "cat__mc_avs_result_code_U": {
            "1.0": "AVS not provided (U). Skipping address verification removes a low-cost control, increasing fraud risk and fee levels.",
            "0.0": "AVS was provided or checked, helping to maintain lower interchange costs."
        },
        "cat__mc_avs_result_code_Y": {
            "1.0": "AVS full match (Y). Both street and postal code matched issuer records, strongly confirming cardholder identity. This reduces fraud risk and usually lowers the fee.",
            "0.0": "No AVS full match available, so the fee does not benefit from this strong fraud protection."
        },
        "cat__mc_avs_result_code_Z": {
            "1.0": "AVS ZIP-only match (Z). The postal code matched, but the full address did not. This gives partial reassurance but still leaves some risk, moderating the benefit.",
            "0.0": "No ZIP-only AVS match in this transaction."
        },
        "cat__mcc_group_airline": {
            "1.0": "Airline merchant. Airlines typically have high ticket values, frequent refunds/changes, and dispute complexity. Issuers face higher exposure, so interchange rates in this sector are often higher or specialized.",
            "0.0": "Not an airline merchant, so the transaction avoids airline-specific interchange rules."
        },
        "cat__mcc_group_other": {
            "1.0": "Other merchant type. Interchange fees here follow general rules. The actual fee depends more on channel type and authentication strength.",
            "0.0": "Not categorized as 'other'."
        },
        "cat__channel_type_card_present": {
            "1.0": "Card-present. The card was physically present and likely verified using EMV chip or tap. Strong hardware-based protections reduce fraud risk, which lowers the interchange fee.",
            "0.0": "The transaction was not card-present, so it does not benefit from the security advantages of physical card usage."
        },
        "cat__channel_type_ecommerce": {
            "1.0": "E-commerce (card-not-present). These transactions lack the physical card and depend on digital authentication. Fraud risk and chargeback exposure are higher, so interchange fees tend to be higher.",
            "0.0": "Not an e-commerce transaction."
        },
        "num__mc_pos_entry_mode": {
            "81": "POS entry mode 81 (chip). Chip transactions create cryptographic proof that reduces counterfeit risk. This strong protection lowers issuer risk and therefore the fee.",
            "5": "POS entry mode 5 (manual entry). Typing card details bypasses EMV and correlates with higher fraud and chargebacks. Issuers compensate by charging higher interchange.",
            "other": "This POS entry mode carries scheme-specific risk. Interchange is adjusted according to the associated fraud likelihood."
        },
        "num__mc_eci_indicator": {
            "5": "ECI 05 (treated as card-present). Indicates an in-person or highly secure environment with low fraud risk, leading to lower interchange.",
            "6": "ECI 06 (card-not-present unauthenticated). No strong authentication was performed, which increases fraud risk and the resulting fee.",
            "7": "ECI 07 (card-not-present authenticated). Authentication (e.g., 3D Secure) reduces some risk but still leaves higher exposure than card-present. The fee remains above CP transactions.",
            "other": "Special ECI value. Impact depends on network rules and authentication strength."
        },
        "num__mc_ucaf_collection_indicator": {
            "0": "No UCAF data collected (e.g., no 3D Secure). Missing this authentication makes the issuer more vulnerable to fraud, increasing fees.",
            "2": "UCAF data collected (e.g., 3D Secure present). This provides strong authentication proof, reducing issuer risk and lowering interchange.",
            "other": "Special UCAF setting. Effect varies by scheme and liability rules."
        },
        "num__mc_cross_border_indicator": {
            "True": "Cross-border transaction. Issuer and acquirer are in different countries, which adds FX processing, regulatory differences, and higher fraud probability. These extra risks and costs drive higher interchange.",
            "False": "Domestic transaction. Card used in country of issue with lower fraud and operational complexity, leading to lower interchange."
        }
    }

    # === Feature-level reasons (for global overview)
    feature_only_reasons = {
    "mc_pos_entry_mode": "The way the card is entered affects fraud risk and fee tier—EMV chip or contactless usually qualifies for lower card-present interchange, while magstripe fallback or manual key entry often causes downgrades to higher fees.",
    "mc_eci_indicator": "The e-commerce security level determines eligibility for secure vs. non-secure programs—authenticated 3-D Secure (high ECI) lowers interchange, while low/no ECI often triggers higher non-secure rates.",
    "mc_ucaf_collection_indicator": "Use of UCAF/3-D Secure data helps qualify for secure e-commerce interchange with reduced fees, while missing UCAF typically results in more expensive standard e-commerce rates.",
    "mc_cvv2_result_code": "Passing CVV2 in card-not-present transactions supports lower interchange by meeting security requirements, while absent or failed CVV2 checks often force a downgrade to higher-fee categories.",
    "mc_avs_result_code": "Submitting and matching AVS data (address verification) helps card-not-present transactions qualify for lower interchange, whereas no or poor match results commonly increase the fee.",
    "mc_cross_border_indicator": "Domestic transactions qualify for local interchange programs with lower fees, while cross-border transactions almost always incur higher interchange and additional assessments.",
    "mcc_group": "The merchant category code defines the base interchange program—preferred sectors like grocery, fuel, charity, or transit often have reduced rates, while higher-risk or standard retail MCCs carry higher fees.",
    "channel_type": "Card-present transactions generally receive lower interchange due to reduced fraud risk, while card-not-present channels (e-commerce, mail/phone) incur higher fees unless strong authentication is used."
}

    # === GLOBAL JSON — feature only (template match)
    shap_feature_df = (
        shap_impact_df
        .groupby("feature", as_index=False)
        .agg({"shap_total": lambda x: np.sum(np.abs(x))})
        .rename(columns={"shap_total": "shap_abs"})
    )
    shap_feature_df["shap_pct"] = (100 * shap_feature_df["shap_abs"] / shap_feature_df["shap_abs"].sum()).round(2)


    # Normalize overall feature importances to sum to exactly 1.0 (float, 2 decimals)
    total_overall = shap_feature_df["shap_abs"].sum()
    norm_vals = []
    for _, row in shap_feature_df.iterrows():
        norm = row["shap_abs"] / total_overall if total_overall else 0.0
        norm_vals.append(norm)
    # Round and adjust last value
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
    # Sort overall_features by importance_normalized descending
    overall_features.sort(key=lambda x: x["importance_normalized"], reverse=True)

    # === PER TRANSACTION JSON (template match)
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
        rounded = [round(v, 2) for v in norm_vals]
        diff = round(1.0 - sum(rounded), 2)
        if rounded:
            rounded[-1] += diff
        for i, f in enumerate(txn_features):
            f["importance_normalized"] = float(rounded[i])
        # Sort txn_features by importance_normalized descending
        txn_features.sort(key=lambda x: x["importance_normalized"], reverse=True)

        predicted_fee = float(y_pred[idx])
        actual_fee = float(row.get("interchange_fee", predicted_fee)) # fallback if not present
        downgrade = bool(predicted_fee > actual_fee)

        per_transaction_json.append({
            "transaction_index": int(idx),
            "predicted_fee": str(round(predicted_fee, 2)),
            "actual_fee": str(round(actual_fee, 2)),
            "downgrade": downgrade,
            "transaction_features": txn_features
        })

    # Final output matches template
    output_json = {
        "overall": {
            "features": overall_features
        },
        "per_transaction": per_transaction_json
    }

    #save to file for inspection
    with open("shap_explanations.json", "w") as f:
        json.dump(output_json, f, indent=4)

    return output_json
