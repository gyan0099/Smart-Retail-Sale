"""
Smart Retail Sales Analytics & Visualization System
Realistic Multi-Store Retail Sales Dataset Generator
Includes Indian Retail Network, Store IDs, Shop Names, Coordinates, Categories & Margins.
"""

import os
import sys
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import INDIAN_STORES_INFO, SAMPLE_CSV_PATH, SAMPLE_EXCEL_PATH

# Fix random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_retail_dataset(n_records: int = 3650) -> pd.DataFrame:
    """
    Generates a realistic retail sales dataset representing a chain of shops across India.
    Includes Store IDs, Store Names, Store Types, geographic coordinates, and accurate financial metrics.
    """
    categories_data = {
        "Electronics": {
            "Smartphones": [("Apple iPhone 15", 79900, 62000), ("Samsung Galaxy S24", 74999, 58000), 
                            ("OnePlus 12", 64999, 49000), ("Redmi Note 13 Pro", 24999, 18500)],
            "Laptops": [("MacBook Air M2", 99900, 78000), ("Dell XPS 13", 115000, 89000), 
                        ("Lenovo ThinkPad E14", 58000, 44000), ("HP Pavilion 15", 62000, 47000)],
            "Audio & Accessories": [("Sony WH-1000XM5 Headphones", 29990, 21000), ("Apple AirPods Pro 2", 24900, 18000),
                                    ("JBL Flip 6 Speaker", 9999, 6800), ("Boat Airdopes 441", 1999, 1100)],
            "Wearables": [("Apple Watch Series 9", 41900, 31000), ("Samsung Galaxy Watch 6", 29999, 21000),
                          ("Noise ColorFit Pro", 2999, 1700), ("Fire-Boltt Phoenix", 1799, 950)]
        },
        "Fashion & Apparel": {
            "Men's Clothing": [("Levi's 511 Slim Jeans", 3599, 1900), ("Van Heusen Formal Shirt", 2499, 1200),
                               ("Nike Dry-Fit T-Shirt", 1995, 950), ("Puma Track Pants", 2299, 1100)],
            "Women's Clothing": [("Biba Anarkali Kurta Set", 4999, 2300), ("Zara Floral Midi Dress", 3990, 1950),
                                 ("Fabindia Silk Saree", 6500, 3100), ("Only Denim Jacket", 2999, 1400)],
            "Footwear": [("Nike Air Zoom Pegasus", 10295, 5800), ("Adidas Ultraboost Light", 13999, 7900),
                         ("Puma Smash v2 Sneakers", 3499, 1700), ("Clarks Leather Loafers", 5999, 3100)]
        },
        "Home & Kitchen": {
            "Kitchen Appliances": [("Philips Air Fryer XL", 8999, 5700), ("Prestige Induction Cooktop", 3295, 2000),
                                  ("Bajaj Mixer Grinder 750W", 3999, 2400), ("Morphy Richards Microwave", 7499, 4900)],
            "Home Decor": [("D'Decor Blackout Curtains", 2199, 1100), ("Solimo Luxury Bed Sheet Set", 1599, 850),
                           ("Philips Smart LED Ceiling Light", 2499, 1400), ("Wakefit Orthopedic Pillow", 1299, 650)],
            "Cookware": [("Hawkins Stainless Steel Pressure Cooker", 2850, 1750), ("Prestige Non-Stick Kadai", 1890, 1050),
                         ("Milton Insulated Casserole Set", 1450, 800)]
        },
        "Health & Personal Care": {
            "Skincare": [("The Ordinary Niacinamide 10%", 750, 420), ("Minimalist Salicylic Acid Serum", 599, 310),
                         ("Cetaphil Gentle Skin Cleanser", 625, 380), ("Neutrogena Hydro Boost Water Gel", 1150, 690)],
            "Personal Grooming": [("Philips Series 5000 Trimmer", 2195, 1300), ("Dyson Supersonic Hair Dryer", 34900, 24500),
                                  ("Oral-B Pro Electric Toothbrush", 1799, 1050)],
            "Wellness & Supplements": [("MuscleBlaze Whey Protein 1kg", 2499, 1600), ("Optimum Nutrition Gold Standard", 3899, 2600),
                                      ("Himalaya Ashwagandha Capsules", 250, 130)]
        },
        "Sports & Fitness": {
            "Fitness Equipment": [("Cockatoo Motorized Treadmill", 24999, 16500), ("Decathlon Hex Dumbbell Pair (10kg)", 3499, 2100),
                                  ("Boldfit Yoga Mat 10mm", 1199, 550), ("Kobo Resistance Bands Set", 899, 420)],
            "Outdoor Sports": [("Yonex Astrox 77 Badminton Racket", 8990, 5200), ("Cosco Premier Football", 1250, 680),
                               ("SG Cricket Bat English Willow", 6499, 3600)]
        },
        "Office & Stationery": {
            "Office Furniture": [("Green Soul Ergonomic Gaming Chair", 14990, 9200), ("Wakefit Height Adjustable Desk", 18999, 12000)],
            "Stationery & Writing": [("Parker Urban Fountain Pen", 1850, 950), ("Classmate Premium Spiral Notebook (Pack of 4)", 480, 250)]
        }
    }

    # City list with weighted population and store presence
    city_keys = list(INDIAN_STORES_INFO.keys())
    city_weights = [
        0.10, # Warangal
        0.18, # Hyderabad
        0.14, # Bengaluru
        0.08, # Chennai
        0.04, # Kochi
        0.05, # Visakhapatnam
        0.04, # Vijayawada
        0.12, # Mumbai
        0.07, # Pune
        0.05, # Ahmedabad
        0.08, # Delhi
        0.03, # Jaipur
        0.03, # Lucknow
        0.02, # Chandigarh
        0.05, # Kolkata
        0.02  # Bhopal
    ]

    customer_segments = ["Consumer", "Corporate", "Home Office"]
    payment_methods = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash on Delivery"]
    order_priorities = ["High", "Medium", "Low", "Critical"]

    # Generate 500 distinct customer personas
    first_names = ["Aarav", "Aditi", "Rohan", "Ananya", "Vikram", "Pooja", "Rahul", "Sneha", "Kiran", "Divya",
                   "Arjun", "Neha", "Sanjay", "Priya", "Manish", "Meera", "Varun", "Swati", "Abhishek", "Ritu",
                   "Deepak", "Kavita", "Suresh", "Lakshmi", "Rajesh", "Sunita", "Harish", "Bhavna", "Pradeep", "Anita"]
    last_names = ["Sharma", "Reddy", "Verma", "Rao", "Patel", "Singh", "Nair", "Gupta", "Iyer", "Kumar",
                  "Deshmukh", "Choudhury", "Bhatt", "Menon", "Joshi", "Mishra", "Mehta", "Chatterjee", "Prasad", "Naidu"]

    customers = []
    for i in range(1, 501):
        c_id = f"CUST-{i:04d}"
        c_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        c_segment = random.choices(customer_segments, weights=[0.60, 0.28, 0.12])[0]
        customers.append((c_id, c_name, c_segment))

    # Product list
    products = []
    prod_counter = 1
    for category, subcats in categories_data.items():
        for subcat, item_list in subcats.items():
            for name, price, cost in item_list:
                p_id = f"PRD-{prod_counter:04d}"
                products.append({
                    "Product ID": p_id,
                    "Product Name": name,
                    "Category": category,
                    "Sub-Category": subcat,
                    "Unit Price": price,
                    "Unit Cost": cost
                })
                prod_counter += 1

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2026, 11, 10)
    total_days = (end_date - start_date).days

    records = []
    for order_idx in range(1, n_records + 1):
        order_id = f"ORD-{order_idx:05d}"
        
        # Date with seasonal Q4 multiplier
        rand_days = random.randint(0, total_days)
        order_date = start_date + timedelta(days=rand_days)

        # Select Store / City
        city = random.choices(city_keys, weights=city_weights)[0]
        store_meta = INDIAN_STORES_INFO[city]

        # Customer selection
        cust_idx = int(np.random.pareto(a=1.5) * 50) % len(customers)
        cust_id, cust_name, cust_segment = customers[cust_idx]

        # Product selection
        prod = random.choice(products)

        # Quantity
        if cust_segment == "Corporate":
            quantity = random.choices([1, 2, 3, 4, 5, 8, 10], weights=[0.20, 0.25, 0.20, 0.15, 0.10, 0.05, 0.05])[0]
        else:
            quantity = random.choices([1, 2, 3, 4, 5], weights=[0.55, 0.25, 0.12, 0.05, 0.03])[0]

        discount_rate = random.choices([0.0, 0.05, 0.10, 0.15, 0.20], weights=[0.45, 0.25, 0.15, 0.10, 0.05])[0]

        unit_price = prod["Unit Price"]
        unit_cost = prod["Unit Cost"]

        raw_revenue = quantity * unit_price
        revenue = round(raw_revenue * (1 - discount_rate), 2)
        cost = round(quantity * unit_cost, 2)
        profit = round(revenue - cost, 2)
        profit_margin = round((profit / revenue) * 100, 2) if revenue > 0 else 0.0

        payment = random.choices(payment_methods, weights=[0.42, 0.28, 0.14, 0.10, 0.06])[0]
        priority = random.choices(order_priorities, weights=[0.25, 0.50, 0.18, 0.07])[0]

        records.append({
            "Order ID": order_id,
            "Order Date": order_date.strftime("%Y-%m-%d"),
            "Store ID": store_meta["store_id"],
            "Store Name": store_meta["store_name"],
            "Store Type": store_meta["store_type"],
            "Customer ID": cust_id,
            "Customer Name": cust_name,
            "Customer Segment": cust_segment,
            "Country": "India",
            "State": store_meta["state"],
            "City": city,
            "Region": store_meta["region"],
            "Latitude": store_meta["lat"],
            "Longitude": store_meta["lon"],
            "Product ID": prod["Product ID"],
            "Product Name": prod["Product Name"],
            "Category": prod["Category"],
            "Sub-Category": prod["Sub-Category"],
            "Quantity": quantity,
            "Unit Price": unit_price,
            "Unit Cost": unit_cost,
            "Discount": discount_rate,
            "Revenue": revenue,
            "Cost": cost,
            "Profit": profit,
            "Profit Margin": profit_margin,
            "Payment Method": payment,
            "Order Priority": priority
        })

    df = pd.DataFrame(records)
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df = df.sort_values(by="Order Date").reset_index(drop=True)
    df["Order Date"] = df["Order Date"].dt.strftime("%Y-%m-%d")
    return df

def save_sample_datasets(output_csv_path: str, output_excel_path: str, n_records: int = 3650):
    """Generates and saves datasets."""
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df = generate_retail_dataset(n_records=n_records)
    df.to_csv(output_csv_path, index=False)
    with pd.ExcelWriter(output_excel_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Retail_Sales_Data", index=False)
    print(f"Generated clean dataset: {output_csv_path} (Shape: {df.shape})")

if __name__ == "__main__":
    save_sample_datasets(str(SAMPLE_CSV_PATH), str(SAMPLE_EXCEL_PATH))
