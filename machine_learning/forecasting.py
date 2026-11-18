"""
Smart Retail Sales Analytics & Visualization System
Machine Learning: Future Sales Forecasting Engine
Uses Time-Feature Engineering, Ridge Regression, Confidence Intervals & Evaluation Metrics.
"""

import numpy as np
import pandas as pd
from datetime import timedelta
from typing import Dict, Any, Tuple
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

class SalesForecaster:
    """Trains regression models to forecast future daily/weekly retail sales."""

    @staticmethod
    def forecast_sales(
        df: pd.DataFrame, 
        days_ahead: int = 30,
        aggregation: str = "D" # 'D' for Daily, 'W' for Weekly
    ) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """
        Generates sales forecast with confidence intervals and model evaluation metrics.
        Returns:
            combined_df: DataFrame with Date, Revenue, Lower_Bound, Upper_Bound, and Data_Type ('Actual' vs 'Forecast (Predicted)')
            metrics: Dict containing MAE, RMSE, MAPE, R2
        """
        if "Order Date" not in df.columns or "Revenue" not in df.columns or len(df) < 20:
            return pd.DataFrame(), {}

        # 1. Aggregate historical time series
        ts_df = df.copy()
        ts_df["Order Date"] = pd.to_datetime(ts_df["Order Date"])
        daily = ts_df.groupby("Order Date")["Revenue"].sum().reset_index().sort_values("Order Date")
        
        # Resample to ensure consecutive dates
        daily = daily.set_index("Order Date").resample(aggregation).sum().reset_index()
        daily["Revenue"] = daily["Revenue"].fillna(0)

        # 2. Feature Engineering
        daily["Day"] = daily["Order Date"].dt.day
        daily["Month"] = daily["Order Date"].dt.month
        daily["DayOfWeek"] = daily["Order Date"].dt.dayofweek
        daily["DayOfYear"] = daily["Order Date"].dt.dayofyear
        daily["Year"] = daily["Order Date"].dt.year
        daily["Trend"] = np.arange(len(daily))
        
        # Lags and Rolling
        daily["Lag_1"] = daily["Revenue"].shift(1).bfill().ffill()
        daily["Lag_7"] = daily["Revenue"].shift(7).bfill().ffill()
        daily["Rolling_7"] = daily["Revenue"].rolling(7, min_periods=1).mean()

        feature_cols = ["Trend", "Day", "Month", "DayOfWeek", "DayOfYear", "Lag_1", "Lag_7", "Rolling_7"]
        X = daily[feature_cols].values
        y = daily["Revenue"].values

        # 3. Train-Test Split (80% Train, 20% Test)
        split_idx = int(len(daily) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        # Train Ridge Model
        model = Ridge(alpha=1.0)
        model.fit(X_train, y_train)

        # Evaluate on Test Set
        y_pred_test = model.predict(X_test)
        mae = float(mean_absolute_error(y_test, y_pred_test))
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_test)))
        r2 = float(r2_score(y_test, y_pred_test))
        mape = float(np.mean(np.abs((y_test - y_pred_test) / np.maximum(y_test, 1))) * 100)

        metrics = {
            "MAE": round(mae, 2),
            "RMSE": round(rmse, 2),
            "MAPE_%": round(mape, 2),
            "R2_Score": round(max(0.0, r2), 3)
        }

        # Refit on all data for future projection
        model.fit(X, y)
        residuals = y - model.predict(X)
        std_resid = np.std(residuals)

        # 4. Iterative Multi-Step Future Forecasting
        last_date = daily["Order Date"].max()
        future_rows = []
        
        current_trend = daily["Trend"].iloc[-1]
        last_lag1 = daily["Revenue"].iloc[-1]
        last_lag7 = daily["Revenue"].iloc[-7] if len(daily) >= 7 else last_lag1
        recent_values = list(daily["Revenue"].iloc[-7:].values)

        for step in range(1, days_ahead + 1):
            next_date = last_date + timedelta(days=step if aggregation == "D" else step * 7)
            trend_val = current_trend + step
            rolling_val = float(np.mean(recent_values[-7:]))
            
            features = np.array([[
                trend_val,
                next_date.day,
                next_date.month,
                next_date.dayofweek,
                next_date.dayofyear,
                last_lag1,
                last_lag7,
                rolling_val
            ]])

            pred_val = float(max(0, model.predict(features)[0]))
            
            # Confidence bounds (80% confidence interval approx 1.28 * std)
            lower_bound = max(0, pred_val - (1.28 * std_resid))
            upper_bound = pred_val + (1.28 * std_resid)

            future_rows.append({
                "Order Date": next_date,
                "Revenue": round(pred_val, 2),
                "Lower_Bound": round(lower_bound, 2),
                "Upper_Bound": round(upper_bound, 2),
                "Data_Type": "Forecast (Predicted)"
            })

            # Update lag values for recursive step
            last_lag7 = recent_values[0]
            last_lag1 = pred_val
            recent_values.pop(0)
            recent_values.append(pred_val)

        # Format historical data
        hist_df = daily[["Order Date", "Revenue"]].copy()
        hist_df["Lower_Bound"] = hist_df["Revenue"]
        hist_df["Upper_Bound"] = hist_df["Revenue"]
        hist_df["Data_Type"] = "Actual"

        future_df = pd.DataFrame(future_rows)
        combined_df = pd.concat([hist_df, future_df], ignore_index=True)
        combined_df["Order Date"] = pd.to_datetime(combined_df["Order Date"])

        return combined_df, metrics
