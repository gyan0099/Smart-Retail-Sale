"""
Smart Retail Sales Analytics & Visualization System
Data Manager: Cleaning, Validation, Type Conversion & Schema Standardization
"""

import os
import io
import sys
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, Optional, List
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import EXPECTED_COLUMNS, SAMPLE_CSV_PATH
from database.db_manager import db_manager

# Common Column Aliases for Flexible Mapping
COLUMN_ALIASES = {
    "order_id": ["order id", "order_id", "orderid", "invoice_no", "invoice id"],
    "order_date": ["order date", "order_date", "date", "invoice_date", "transaction_date"],
    "customer_id": ["customer id", "customer_id", "cust_id", "client_id"],
    "customer_name": ["customer name", "customer_name", "client_name", "customer"],
    "customer_segment": ["customer segment", "customer_segment", "segment"],
    "country": ["country", "nation"],
    "state": ["state", "province"],
    "city": ["city", "town"],
    "region": ["region", "zone", "territory"],
    "product_id": ["product id", "product_id", "item_id", "sku"],
    "product_name": ["product name", "product_name", "item_name", "title"],
    "category": ["category", "product_category", "dept"],
    "sub_category": ["sub-category", "sub_category", "subcategory"],
    "quantity": ["quantity", "qty", "units_sold", "volume"],
    "unit_price": ["unit price", "unit_price", "price", "retail_price"],
    "unit_cost": ["unit cost", "unit_cost", "cost_price", "cost_per_unit"],
    "discount": ["discount", "disc", "discount_rate", "discount_percent"],
    "revenue": ["revenue", "sales", "total_sales", "total_amount", "turnover"],
    "cost": ["cost", "total_cost", "cogs"],
    "profit": ["profit", "net_profit", "earnings", "margin_amount"],
    "profit_margin": ["profit margin", "profit_margin", "margin_percent", "margin_%"],
    "payment_method": ["payment method", "payment_method", "payment_type", "payment_mode"],
    "order_priority": ["order priority", "order_priority", "priority"]
}

class DataManager:
    """Handles dataset ingestion, validation, cleaning, and preparation."""

    @staticmethod
    def load_data(file_or_path) -> pd.DataFrame:
        """
        Loads CSV or Excel data with robust encoding and formatting detection.
        Accepts either a string path or a file-like object (e.g., Streamlit UploadedFile).
        """
        if isinstance(file_or_path, (str, Path)):
            path_str = str(file_or_path)
            if path_str.endswith(".csv"):
                try:
                    df = pd.read_csv(path_str, encoding="utf-8")
                except UnicodeDecodeError:
                    df = pd.read_csv(path_str, encoding="latin1")
            elif path_str.endswith((".xlsx", ".xls")):
                df = pd.read_excel(path_str)
            else:
                raise ValueError("Unsupported file format. Please upload CSV or Excel.")
        else:
            # File-like object (UploadedFile)
            name = getattr(file_or_path, "name", "").lower()
            if name.endswith(".csv") or hasattr(file_or_path, "getvalue"):
                try:
                    df = pd.read_csv(file_or_path, encoding="utf-8")
                except Exception:
                    file_or_path.seek(0)
                    try:
                        df = pd.read_csv(file_or_path, encoding="latin1")
                    except Exception:
                        file_or_path.seek(0)
                        df = pd.read_excel(file_or_path)
            elif name.endswith((".xlsx", ".xls")):
                df = pd.read_excel(file_or_path)
            else:
                df = pd.read_csv(file_or_path)
        
        return df

    @staticmethod
    def load_default_sample() -> pd.DataFrame:
        """Loads the default realistic sample retail dataset."""
        if not os.path.exists(SAMPLE_CSV_PATH):
            from data.sample_generator import save_sample_datasets
            from config import SAMPLE_EXCEL_PATH
            save_sample_datasets(str(SAMPLE_CSV_PATH), str(SAMPLE_EXCEL_PATH))
        
        df = pd.read_csv(SAMPLE_CSV_PATH)
        return df

    @staticmethod
    def standardize_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Maps user uploaded column names to standardized Smart Retail names using aliases.
        """
        df_copy = df.copy()
        current_cols = {col.strip().lower(): col for col in df_copy.columns}
        rename_dict = {}

        # Inverse mapping from alias to standard title
        standard_map = {
            "order_id": "Order ID",
            "order_date": "Order Date",
            "customer_id": "Customer ID",
            "customer_name": "Customer Name",
            "customer_segment": "Customer Segment",
            "country": "Country",
            "state": "State",
            "city": "City",
            "region": "Region",
            "product_id": "Product ID",
            "product_name": "Product Name",
            "category": "Category",
            "sub_category": "Sub-Category",
            "quantity": "Quantity",
            "unit_price": "Unit Price",
            "unit_cost": "Unit Cost",
            "discount": "Discount",
            "revenue": "Revenue",
            "cost": "Cost",
            "profit": "Profit",
            "profit_margin": "Profit Margin",
            "payment_method": "Payment Method",
            "order_priority": "Order Priority"
        }

        for canonical_key, aliases in COLUMN_ALIASES.items():
            for alias in aliases:
                if alias in current_cols:
                    original_col = current_cols[alias]
                    standard_name = standard_map[canonical_key]
                    if original_col != standard_name:
                        rename_dict[original_col] = standard_name
                    break

        if rename_dict:
            df_copy.rename(columns=rename_dict, inplace=True)
            
        return df_copy, rename_dict

    @staticmethod
    def validate_schema(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validates dataset columns against expected schema and identifies missing or extra columns.
        """
        df_cols = list(df.columns)
        matched_cols = [c for c in EXPECTED_COLUMNS if c in df_cols]
        missing_cols = [c for c in EXPECTED_COLUMNS if c not in df_cols]
        extra_cols = [c for c in df_cols if c not in EXPECTED_COLUMNS]
        compliance_pct = round((len(matched_cols) / len(EXPECTED_COLUMNS)) * 100, 1)

        return {
            "is_valid": len(missing_cols) == 0,
            "compliance_pct": compliance_pct,
            "matched_cols": matched_cols,
            "missing_cols": missing_cols,
            "extra_cols": extra_cols,
            "total_rows": len(df),
            "total_cols": len(df_cols)
        }

    @staticmethod
    def detect_missing_values(df: pd.DataFrame) -> pd.DataFrame:
        """Returns detailed summary of missing values per column."""
        null_counts = df.isnull().sum()
        null_pcts = (null_counts / len(df)) * 100
        dtypes = df.dtypes.astype(str)

        summary = pd.DataFrame({
            "Column Name": df.columns,
            "Data Type": [dtypes[c] for c in df.columns],
            "Missing Count": [null_counts[c] for c in df.columns],
            "Missing Percentage (%)": [round(null_pcts[c], 2) for c in df.columns]
        })
        return summary[summary["Missing Count"] > 0].reset_index(drop=True)

    @staticmethod
    def detect_duplicates(df: pd.DataFrame, subset_col: Optional[str] = "Order ID") -> int:
        """Returns the number of duplicate rows."""
        if subset_col and subset_col in df.columns:
            return int(df.duplicated(subset=[subset_col]).sum())
        return int(df.duplicated().sum())

    @classmethod
    def clean_dataset(
        cls,
        df: pd.DataFrame,
        handle_missing: str = "impute", # 'impute', 'drop', 'keep'
        remove_dups: bool = True,
        detect_outliers: bool = True,
        dataset_name: str = "Uploaded Dataset"
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Executes a comprehensive data cleaning pipeline:
        1. Standardize column names
        2. Remove duplicates
        3. Handle missing values
        4. Correct data types (dates, numeric fields)
        5. Calculate/recalculate missing derivative fields (Revenue, Cost, Profit, Margin)
        6. Log all actions in SQLite database
        """
        rows_before = len(df)
        logs = []
        df_clean, renames = cls.standardize_columns(df)
        if renames:
            logs.append(f"Standardized {len(renames)} column names: {', '.join(renames.keys())}")

        # 1. Duplicates
        dups_count = 0
        if remove_dups:
            subset = ["Order ID"] if "Order ID" in df_clean.columns else None
            dups_count = int(df_clean.duplicated(subset=subset).sum())
            if dups_count > 0:
                df_clean = df_clean.drop_duplicates(subset=subset).reset_index(drop=True)
                logs.append(f"Removed {dups_count} duplicate records.")

        # 2. Date Parsing
        if "Order Date" in df_clean.columns:
            df_clean["Order Date"] = pd.to_datetime(df_clean["Order Date"], errors="coerce")
            # Fill missing dates if any with forward fill or today
            if df_clean["Order Date"].isnull().sum() > 0:
                df_clean["Order Date"] = df_clean["Order Date"].bfill().ffill()
            df_clean["Order Date"] = df_clean["Order Date"].dt.strftime("%Y-%m-%d")

        # 3. Numeric conversions & cleaning
        numeric_cols = ["Quantity", "Unit Price", "Unit Cost", "Discount", "Revenue", "Cost", "Profit", "Profit Margin"]
        for col in numeric_cols:
            if col in df_clean.columns:
                if df_clean[col].dtype == object:
                    # Strip currency symbols and commas
                    df_clean[col] = (
                        df_clean[col].astype(str)
                        .str.replace("$", "", regex=False)
                        .str.replace("₹", "", regex=False)
                        .str.replace(",", "", regex=False)
                        .str.strip()
                    )
                df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

        # 4. Handle Missing Values
        missing_summary = cls.detect_missing_values(df_clean)
        missing_count_total = int(df_clean.isnull().sum().sum())
        
        if missing_count_total > 0:
            if handle_missing == "drop":
                df_clean = df_clean.dropna().reset_index(drop=True)
                logs.append(f"Dropped rows with missing values. Row count reduced to {len(df_clean)}.")
            elif handle_missing == "impute":
                for col in df_clean.columns:
                    if df_clean[col].isnull().sum() > 0:
                        if pd.api.types.is_numeric_dtype(df_clean[col]):
                            median_val = df_clean[col].median()
                            df_clean[col] = df_clean[col].fillna(median_val if not pd.isna(median_val) else 0)
                        else:
                            mode_val = df_clean[col].mode()
                            fill_val = mode_val[0] if len(mode_val) > 0 else "Unknown"
                            df_clean[col] = df_clean[col].fillna(fill_val)
                logs.append(f"Imputed {missing_count_total} missing values across numerical and categorical columns.")

        # 5. Derivative consistency checking
        if "Quantity" in df_clean.columns and "Unit Price" in df_clean.columns:
            discount = df_clean["Discount"] if "Discount" in df_clean.columns else 0.0
            if "Revenue" not in df_clean.columns or df_clean["Revenue"].isnull().all():
                df_clean["Revenue"] = (df_clean["Quantity"] * df_clean["Unit Price"] * (1 - discount)).round(2)
                logs.append("Generated Revenue column from Quantity * Unit Price * (1 - Discount).")
        
        if "Quantity" in df_clean.columns and "Unit Cost" in df_clean.columns:
            if "Cost" not in df_clean.columns or df_clean["Cost"].isnull().all():
                df_clean["Cost"] = (df_clean["Quantity"] * df_clean["Unit Cost"]).round(2)
                logs.append("Generated Cost column from Quantity * Unit Cost.")

        if "Revenue" in df_clean.columns and "Cost" in df_clean.columns:
            if "Profit" not in df_clean.columns or df_clean["Profit"].isnull().all():
                df_clean["Profit"] = (df_clean["Revenue"] - df_clean["Cost"]).round(2)
                logs.append("Calculated Profit column.")
            
            if "Profit Margin" not in df_clean.columns or df_clean["Profit Margin"].isnull().all():
                df_clean["Profit Margin"] = np.where(
                    df_clean["Revenue"] > 0,
                    ((df_clean["Profit"] / df_clean["Revenue"]) * 100).round(2),
                    0.0
                )
                logs.append("Calculated Profit Margin percentage column.")

        # 6. Outlier Analysis (IQR bounds for Revenue and Quantity)
        outlier_info = {}
        if detect_outliers and "Revenue" in df_clean.columns:
            q1 = df_clean["Revenue"].quantile(0.25)
            q3 = df_clean["Revenue"].quantile(0.75)
            iqr = q3 - q1
            upper_bound = q3 + (1.5 * iqr)
            lower_bound = max(0, q1 - (1.5 * iqr))
            outliers_count = int(((df_clean["Revenue"] < lower_bound) | (df_clean["Revenue"] > upper_bound)).sum())
            outlier_info["Revenue"] = {
                "q1": round(q1, 2), "q3": round(q3, 2), "iqr": round(iqr, 2),
                "upper_bound": round(upper_bound, 2), "lower_bound": round(lower_bound, 2),
                "outliers_count": outliers_count
            }

        rows_after = len(df_clean)
        
        # Log to Database
        db_manager.log_cleaning_action(
            dataset_name=dataset_name,
            action="Data Cleaning Pipeline",
            details="; ".join(logs) if logs else "No modifications required.",
            rows_before=rows_before,
            rows_after=rows_after
        )

        cleaning_summary = {
            "rows_before": rows_before,
            "rows_after": rows_after,
            "rows_removed": rows_before - rows_after,
            "duplicates_removed": dups_count,
            "missing_values_handled": missing_count_total,
            "outlier_info": outlier_info,
            "logs": logs
        }

        return df_clean, cleaning_summary

    @staticmethod
    def to_csv_bytes(df: pd.DataFrame) -> bytes:
        """Converts DataFrame to downloadable CSV bytes."""
        return df.to_csv(index=False).encode("utf-8")

    @staticmethod
    def to_excel_bytes(df: pd.DataFrame) -> bytes:
        """Converts DataFrame to downloadable Excel bytes with openpyxl."""
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Cleaned_Data")
        return output.getvalue()
