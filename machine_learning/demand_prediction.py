"""
Smart Retail Sales Analytics & Visualization System
Machine Learning: Product Demand Prediction Engine
Predicts sales demand (quantity) using Random Forest Regressor & What-If scenario simulations.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

class DemandPredictor:
    """Supervised learning pipeline to model and predict order quantity demand."""

    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        self.feature_columns = []
        self.metrics = {}
        self.is_trained = False
        self.category_list = []
        self.region_list = []
        self.segment_list = []

    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Encodes features and separates targets for demand prediction."""
        df_feat = df.copy()
        
        # Ensure dates
        df_feat["Order Date"] = pd.to_datetime(df_feat["Order Date"])
        df_feat["Month"] = df_feat["Order Date"].dt.month
        df_feat["DayOfWeek"] = df_feat["Order Date"].dt.dayofweek

        # Extract unique categories for simulation
        self.category_list = sorted(list(df_feat["Category"].dropna().unique()))
        self.region_list = sorted(list(df_feat["Region"].dropna().unique()))
        self.segment_list = sorted(list(df_feat["Customer Segment"].dropna().unique()))

        # One-Hot Encoding
        cat_encoded = pd.get_dummies(df_feat[["Category", "Region", "Customer Segment"]], drop_first=True)
        
        numeric_cols = ["Unit Price", "Discount", "Month", "DayOfWeek"]
        X = pd.concat([df_feat[numeric_cols], cat_encoded], axis=1)
        # Fill any missing
        X = X.fillna(0)
        y = df_feat["Quantity"].fillna(1)

        self.feature_columns = list(X.columns)
        return X, y

    def train(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Trains the Random Forest Demand Prediction model and returns evaluation metrics."""
        if "Quantity" not in df.columns or len(df) < 30:
            return {}

        X, y = self.prepare_features(df)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model.fit(X_train, y_train)
        self.is_trained = True

        y_pred = self.model.predict(X_test)
        mae = float(mean_absolute_error(y_test, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        r2 = float(r2_score(y_test, y_pred))

        # Feature Importances
        importances = pd.DataFrame({
            "Feature": self.feature_columns,
            "Importance": self.model.feature_importances_
        }).sort_values(by="Importance", ascending=False).head(8)

        self.metrics = {
            "MAE": round(mae, 2),
            "RMSE": round(rmse, 2),
            "R2_Score": round(max(0.0, r2), 3),
            "Feature_Importance": importances
        }
        return self.metrics

    def predict_scenario(
        self,
        unit_price: float,
        discount: float,
        category: str,
        region: str,
        segment: str,
        month: int = 10,
        day_of_week: int = 3
    ) -> Dict[str, Any]:
        """
        Interactive simulation: predicts demand (quantity) for a specific product configuration.
        """
        if not self.is_trained:
            return {"predicted_quantity": 1, "predicted_revenue": unit_price}

        # Build feature vector matching self.feature_columns
        row = {col: 0 for col in self.feature_columns}
        row["Unit Price"] = unit_price
        row["Discount"] = discount
        row["Month"] = month
        row["DayOfWeek"] = day_of_week

        # Set one-hot columns
        cat_col = f"Category_{category}"
        if cat_col in row:
            row[cat_col] = 1

        reg_col = f"Region_{region}"
        if reg_col in row:
            row[reg_col] = 1

        seg_col = f"Customer Segment_{segment}"
        if seg_col in row:
            row[seg_col] = 1

        input_df = pd.DataFrame([row])
        pred_qty = float(self.model.predict(input_df)[0])
        pred_qty_rounded = max(1, int(round(pred_qty)))
        predicted_rev = round(pred_qty_rounded * unit_price * (1 - discount), 2)

        return {
            "predicted_quantity": pred_qty_rounded,
            "predicted_quantity_raw": round(pred_qty, 2),
            "predicted_revenue": predicted_rev,
            "discount_applied": f"{int(discount * 100)}%"
        }
