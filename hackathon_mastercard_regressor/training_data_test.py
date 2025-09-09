import pandas as pd
import joblib

X_test = pd.read_csv("x_test.csv")
y_test = pd.read_csv("y_test.csv").squeeze()
model = joblib.load("xgb_model_interchange_fee_rate.pkl")

y_pred = model.predict(X_test)

df = pd.DataFrame({
    "actual": y_test,
    "predicted": y_pred,
    "abs_error": abs(y_test - y_pred),
    "pct_error": 100 * abs(y_test - y_pred) / y_test
})

print(df.describe())
print("\nAvg Percent Error:", df["pct_error"].mean())
