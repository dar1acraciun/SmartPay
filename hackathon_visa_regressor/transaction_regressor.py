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
INPUT_CSV = "visa_transactions_final.csv"
TARGET = "fee_rate"
OUTPUT_MODEL = "xgb_model_interchange_fee_rate.pkl"

FEATURES = [
    "visa_cross_border_indicator",         # binary categorical: 'Y' or 'N'
    "visa_channel_type",                   # categorical: 'ecommerce', 'card_present', etc.
    "visa_eci_indicator",                  # numeric or ordinal: integer (e.g., 2 to 7)
    "visa_cvv2_result_code",              # categorical: 'M', 'N', 'U', etc.
    "visa_avs_result_code",               # categorical: 'Y', 'N', 'A', 'Z', 'U', etc.
    "visa_pos_entry_mode",                # numeric: e.g., 1 = manual, 5 = chip, 7 = contactless
    "visa_terminal_capability_code",      # numeric: terminal risk profile (low = risky)
    "visa_merchant_category_code",        # categorical: MCC code, can be grouped or one-hot
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
        n_estimators=200,
        learning_rate=0.07,
        max_depth=5,
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

