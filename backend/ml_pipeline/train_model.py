import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import joblib
import os

file_path = "data/synthetic_data.csv"
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Dataset not found at {file_path}. Please generate it first.")

df = pd.read_csv(file_path)

X = df.drop("dispatch_score", axis=1)
y = df["dispatch_score"]

print(f"Score Range: {y.min():.2f} to {y.max():.2f}")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Optimized for faster GA inference & smaller file size
model = RandomForestRegressor(
    n_estimators=150,   
    max_depth=15,       
    random_state=42,
    n_jobs=-1
)

print("\nTraining model...")
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

# Expanded Metrics
print("\nMODEL PERFORMANCE")
print("-" * 30)
print(f"R² Score            : {r2_score(y_test, y_pred):.4f}")
print(f"Mean Absolute Error : {mean_absolute_error(y_test, y_pred):.4f}")

# Feature Importance to ensure logical routing
print("\nFEATURE IMPORTANCES")
print("-" * 30)
importances = model.feature_importances_
feature_names = X.columns
for name, importance in sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True):
    print(f"{name:<18}: {importance:.4f}")

os.makedirs("models", exist_ok=True)
joblib.dump(model, "artifacts/saved_model.pkl")

print("\nModel saved successfully to artifacts/saved_model.pkl!")