# app/train.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import mlflow

# 1. Create fake training data
np.random.seed(42)
data = pd.DataFrame({
    'unit_price': np.random.randint(50, 500, 100),
    'quantity': np.random.randint(1, 20, 100),
    'is_pro_customer': np.random.choice([0, 1], 100)
})
data['bulk_discount_applied'] = (data['quantity'] * data['is_pro_customer'] > 10).astype(int)

# 2. Split data
X = data[['unit_price', 'quantity', 'is_pro_customer']]
y = data['bulk_discount_applied']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 3. Train model
mlflow.set_experiment("bulk-discount-model")
with mlflow.start_run():
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    acc = model.score(X_test, y_test)
    mlflow.log_metric("accuracy", acc)

# 4. Save model
joblib.dump(model, "app/model.pkl")
print(f"Model trained. Accuracy: {acc:.2f}")
