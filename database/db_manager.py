"""
Smart Retail Sales Analytics & Visualization System
SQLite Database Manager
Handles dataset registry, audit trails, cleaning logs, and analytical snapshots.
"""

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import DATABASE_PATH

class DatabaseManager:
    """Manages SQLite database connections and operations for Smart Retail System."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(DATABASE_PATH)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a connection to the SQLite database with row factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initializes tables if they do not exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Datasets tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS uploaded_datasets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    uploaded_at TEXT NOT NULL,
                    row_count INTEGER NOT NULL,
                    col_count INTEGER NOT NULL,
                    file_size_kb REAL NOT NULL,
                    status TEXT DEFAULT 'Active'
                );
            """)

            # Data processing & cleaning audit trail
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processing_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_name TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT NOT NULL,
                    rows_before INTEGER,
                    rows_after INTEGER,
                    timestamp TEXT NOT NULL
                );
            """)

            # Executive analytics snapshots
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS executive_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_name TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    total_revenue REAL NOT NULL,
                    total_profit REAL NOT NULL,
                    total_orders INTEGER NOT NULL,
                    total_customers INTEGER NOT NULL,
                    products_sold INTEGER NOT NULL,
                    avg_order_value REAL NOT NULL,
                    profit_margin REAL NOT NULL,
                    revenue_growth REAL
                );
            """)

            # Active sales table for direct SQL queries
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales_records (
                    order_id TEXT PRIMARY KEY,
                    order_date TEXT,
                    customer_id TEXT,
                    customer_name TEXT,
                    customer_segment TEXT,
                    country TEXT,
                    state TEXT,
                    city TEXT,
                    region TEXT,
                    product_id TEXT,
                    product_name TEXT,
                    category TEXT,
                    sub_category TEXT,
                    quantity INTEGER,
                    unit_price REAL,
                    unit_cost REAL,
                    discount REAL,
                    revenue REAL,
                    cost REAL,
                    profit REAL,
                    profit_margin REAL,
                    payment_method TEXT,
                    order_priority TEXT
                );
            """)

            conn.commit()

    def log_dataset_upload(self, filename: str, row_count: int, col_count: int, file_size_kb: float, status: str = "Active") -> int:
        """Records an uploaded dataset in the database."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO uploaded_datasets (filename, uploaded_at, row_count, col_count, file_size_kb, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (filename, now, row_count, col_count, file_size_kb, status))
            conn.commit()
            return cursor.lastrowid

    def log_cleaning_action(self, dataset_name: str, action: str, details: str, rows_before: int, rows_after: int):
        """Records a data cleaning operation into the audit log."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO processing_logs (dataset_name, action, details, rows_before, rows_after, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (dataset_name, action, details, rows_before, rows_after, now))
            conn.commit()

    def get_datasets(self) -> pd.DataFrame:
        """Retrieves list of uploaded datasets."""
        with self.get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM uploaded_datasets ORDER BY id DESC", conn)

    def get_logs(self) -> pd.DataFrame:
        """Retrieves data cleaning and processing audit logs."""
        with self.get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM processing_logs ORDER BY id DESC", conn)

    def save_sales_records(self, df: pd.DataFrame):
        """Persists or refreshes active sales records in SQLite."""
        with self.get_connection() as conn:
            # Map column names to database schema
            rename_map = {
                "Order ID": "order_id", "Order Date": "order_date", "Customer ID": "customer_id",
                "Customer Name": "customer_name", "Customer Segment": "customer_segment",
                "Country": "country", "State": "state", "City": "city", "Region": "region",
                "Product ID": "product_id", "Product Name": "product_name", "Category": "category",
                "Sub-Category": "sub_category", "Quantity": "quantity", "Unit Price": "unit_price",
                "Unit Cost": "unit_cost", "Discount": "discount", "Revenue": "revenue",
                "Cost": "cost", "Profit": "profit", "Profit Margin": "profit_margin",
                "Payment Method": "payment_method", "Order Priority": "order_priority"
            }
            db_df = df.rename(columns=rename_map)
            # Retain only recognized columns
            valid_cols = [c for c in rename_map.values() if c in db_df.columns]
            db_df[valid_cols].to_sql("sales_records", conn, if_exists="replace", index=False)

    def load_sales_records(self) -> pd.DataFrame:
        """Loads sales records from SQLite database."""
        with self.get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM sales_records", conn)
            # Revert column names back to Title Case display names
            reverse_map = {
                "order_id": "Order ID", "order_date": "Order Date", "customer_id": "Customer ID",
                "customer_name": "Customer Name", "customer_segment": "Customer Segment",
                "country": "Country", "state": "State", "city": "City", "region": "Region",
                "product_id": "Product ID", "product_name": "Product Name", "category": "Category",
                "sub_category": "Sub-Category", "quantity": "Quantity", "unit_price": "Unit Price",
                "unit_cost": "Unit Cost", "discount": "Discount", "revenue": "Revenue",
                "cost": "Cost", "profit": "Profit", "profit_margin": "Profit Margin",
                "payment_method": "Payment Method", "order_priority": "Order Priority"
            }
            return df.rename(columns=reverse_map)

    def save_snapshot(self, name: str, metrics: Dict[str, Any]):
        """Saves an executive KPI snapshot."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO executive_snapshots (
                    snapshot_name, timestamp, total_revenue, total_profit, 
                    total_orders, total_customers, products_sold, 
                    avg_order_value, profit_margin, revenue_growth
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, now, 
                metrics.get("total_revenue", 0.0),
                metrics.get("total_profit", 0.0),
                metrics.get("total_orders", 0),
                metrics.get("total_customers", 0),
                metrics.get("products_sold", 0),
                metrics.get("avg_order_value", 0.0),
                metrics.get("profit_margin", 0.0),
                metrics.get("revenue_growth", 0.0)
            ))
            conn.commit()

    def get_snapshots(self) -> pd.DataFrame:
        """Retrieves saved executive snapshots."""
        with self.get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM executive_snapshots ORDER BY id DESC", conn)

# Singleton instance
db_manager = DatabaseManager()
