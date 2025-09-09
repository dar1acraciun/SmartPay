import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib

# === Config ===
INPUT_CSV = "mastercard_transactions.csv"
TARGET = "rate_pct"
OUTPUT_MODEL = "xgb_model_interchange_fee_rate.pkl"
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


# === Load data ===
df = pd.read_csv(INPUT_CSV)
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]


df[TARGET] = (
    df[TARGET]
    .astype(str)
    .str.replace("%", "")
    .str.replace(",", ".")
    .str.strip()
)
X = df[FEATURES].copy()
y = pd.to_numeric(df[TARGET], errors="coerce")

# Drop rows with missing target
X = X.loc[y.notna()]
y = y.loc[y.notna()]

# === Preprocessing ===
categorical = [c for c in FEATURES if X[c].dtype == "object"]
numeric = [c for c in FEATURES if c not in categorical]

preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
    ("num", "passthrough", numeric)
])

# === Model pipeline ===
model = Pipeline([
    ("preprocessor", preprocessor),
    ("xgb", XGBRegressor(
        n_estimators=100,
        learning_rate=0.07,
        max_depth=4,
        subsample=0.9,
        colsample_bytree=0.90,
        tree_method="hist",
        shuffle=False,
        n_jobs=1
    ))
])

# === Train/test split ===
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.01, shuffle=True
)

# === Train model ===
model.fit(X_train, y_train)

# === Predict ===
y_pred = model.predict(X_test)




# === Print sample predictions ===
preview = pd.DataFrame({
    "actual_fee_rate": y_test.values,
    "predicted_fee_rate": y_pred
}, index=X_test.index)

preview["abs_error"] = np.abs(preview["actual_fee_rate"] - preview["predicted_fee_rate"])
preview["percent_error"] = 100 * preview["abs_error"] / preview["actual_fee_rate"]


average_percent_error = preview["percent_error"].mean()



print("\n🔍 Sample predictions:")
print(preview.head(2000).to_string(index=False))

print(f"📊 Average Percent Error: {average_percent_error:.2f}%")


X_test.to_csv("x_test.csv", index=False)
y_test.to_csv("y_test.csv", index=False)
joblib.dump(model, OUTPUT_MODEL)

