# SR UNIVERSITY
### School of Computer Science and Artificial Intelligence
#### Warangal, Telangana

---

## A Project Report on
# SMART RETAIL SALES ANALYTICS & VISUALIZATION SYSTEM

**Submitted in partial fulfilment of the requirements for the course:**  
**Data Analytics and Visualization (25CAI202PC201)**

**Submitted by:**  
[Student Name] ([Roll Number])  
Department of Computer Science & Engineering (AI & ML)

**Under the guidance of:**  
[Faculty Name], Assistant Professor  
School of Computer Science and Artificial Intelligence  
SR University, Warangal

**Academic Year 2026-27**

---

# CERTIFICATE

This is to certify that the project report entitled **“SMART RETAIL SALES ANALYTICS & VISUALIZATION SYSTEM”** is a bonafide record of work carried out by **[Student Name] ([Roll Number])** in partial fulfilment of the requirements for the course **Data Analytics and Visualization (25CAI202PC201)** at the School of Computer Science and Artificial Intelligence, SR University, Warangal, during the academic year 2026-27, under my supervision.

The results presented in this report have not been submitted elsewhere for any other course or degree.

<br><br>

______________________  
**Faculty Signature**  
Date: ____________  
Place: Warangal

---

# TABLE OF CONTENTS
1. [PROJECT GOAL](#1-project-goal)
   - 1.1 Problem Statement
   - 1.2 Objectives of the Project
   - 1.3 Specific Analytical Questions
2. [DATA OVERVIEW](#2-data-overview)
   - 2.1 Data Source and Acquisition
   - 2.2 Dataset Attributes and Data Types
   - 2.3 Sample Data Preview
3. [DATA CLEANING PROCESS](#3-data-cleaning-process)
   - 3.1 Missing Values and Duplicates
   - 3.2 Data Type Corrections and Standardization
   - 3.3 Outlier Detection (IQR Method)
   - 3.4 Feature Engineering and Dataset Metrics
4. [DATA ANALYSIS](#4-data-analysis)
   - 4.1 Descriptive Statistical Summary
   - 4.2 Exploratory Data Analysis (EDA)
   - 4.3 Variable Relationships and Correlations
   - 4.4 Summary of Key Findings
5. [VISUALISATION](#5-visualisation)
   - Figure 5.1: Monthly Sales and Profit Progression
   - Figure 5.2: Category-wise Revenue & Profit Comparison
   - Figure 5.3: Regional Sales Contribution Share
   - Figure 5.4: Customer RFM Behavioral Segmentation
   - Figure 5.5: Machine Learning Sales Forecast
   - Figure 5.6: Revenue vs. Cost Distribution
   - 5.7 Final BI Dashboard Composite Overview
6. [FINAL CONCLUSION](#6-final-conclusion)
7. [FUTURE OUTCOMES AND LIMITATIONS](#7-future-outcomes-and-limitations)
- [APPENDIX: SYSTEM CODE & ARCHITECTURE](#appendix-code)

---

## 1. PROJECT GOAL

### 1.1 Problem Statement
Modern omnichannel retail enterprises generate millions of transactional records across distributed geographic locations, diverse product hierarchies, and multiple digital payment gateways. However, business stakeholders frequently struggle with fragmented data silos, delayed reporting cadences, and reactive inventory replenishment. This leads to frequent stockouts of high-velocity items, excessive holding costs for slow-moving inventory, and undetected profit margin compression. To address these operational challenges, retail organizations require an automated, end-to-end Business Intelligence (BI) and Predictive Analytics system capable of synthesizing transactional logs into real-time key performance indicators (KPIs), interactive multi-dimensional visual dashboards, and forward-looking demand schedules.

### 1.2 Objectives of the Project
1. **Executive Performance Monitoring:** Synthesize operational data into real-time business metrics including Total Revenue, Total Profit, Average Order Value (AOV), and Profit Margin.
2. **Temporal Sales Decomposition:** Analyze granular sales trends across daily, monthly, and yearly intervals to identify seasonal demand spikes and growth trajectories.
3. **Product & Category Profitability:** Rank best-selling vs underperforming items and conduct Pareto (80/20) analysis to uncover revenue concentration.
4. **Customer Behavioral Analytics:** Implement RFM (Recency, Frequency, Monetary) segmentation and estimate Customer Lifetime Value (CLV).
5. **Geospatial Optimization:** Map regional, state, and city sales performance across India to evaluate market penetration.
6. **Machine Learning Deployment:** Deploy Ridge Regression time-series forecasting and Random Forest demand prediction models with strict evaluation metrics (MAE, RMSE, R²).
7. **Automated Export Pipelines:** Generate multi-tab Excel workbooks and vector PDF reports directly from active analytical filters.

### 1.3 Specific Analytical Questions
1. Which product categories yield the highest gross margin and generate the bulk of net corporate profitability?
2. What are the seasonal patterns across quarters, and what sales volume is forecasted for the subsequent 45 days?
3. What percentage of the customer base consists of repeat buyers versus single-transaction acquisitions?
4. Which geographic zones and metropolitan centers produce superior average order values?
5. How do promotional discount rates affect unit demand and product gross margins?

---

## 2. DATA OVERVIEW

### 2.1 Data Source and Acquisition
- **Dataset Provider:** Enterprise Smart Retail Transactional Repository.
- **Coverage Period:** January 1, 2024 to November 10, 2026 (spanning 35 consecutive months of commercial operations).
- **Size of Dataset:** 3,650 rows and 23 distinct attributes.
- **Target Variables:** `Revenue` (continuous numeric), `Profit` (continuous numeric), and `Quantity` (integer count).

### 2.2 Variables and Data Types
| Variable Name | Data Type | Description |
| :--- | :--- | :--- |
| **Order ID** | String (Categorical) | Unique identifier for each customer transaction |
| **Order Date** | Datetime (ISO 8601) | Date of transaction order |
| **Customer ID / Name** | String (Categorical) | Customer identifier and customer name |
| **Customer Segment** | Categorical | Classification: Consumer, Corporate, Home Office |
| **Country, State, City** | Categorical | Geographic location (e.g. Warangal, Hyderabad, Mumbai) |
| **Region** | Categorical | Macro territory: South, West, North, East, Central |
| **Product ID / Name** | Categorical | SKU identification and item name |
| **Category / Sub-Category** | Categorical | Taxonomy (Electronics, Apparel, Home & Kitchen, etc.) |
| **Quantity** | Integer (Numeric) | Physical units ordered |
| **Unit Price / Unit Cost** | Float (Numeric) | Retail price and baseline cost per unit in ₹ |
| **Discount** | Float (Numeric) | Promotional discount rate (0.0 to 0.20) |
| **Revenue** | Float (Numeric) | Net sales receipt: $Quantity \times Unit Price \times (1 - Discount)$ |
| **Cost** | Float (Numeric) | Cost of Goods Sold: $Quantity \times Unit Cost$ |
| **Profit** | Float (Numeric) | Net gross profit: $Revenue - Cost$ |
| **Profit Margin** | Float (Numeric) | Percentage margin: $(Profit / Revenue) \times 100$ |
| **Payment Method** | Categorical | Payment gateway: UPI, Credit Card, Debit Card, Net Banking, COD |

---

## 3. DATA CLEANING PROCESS

### 3.1 Cleaning Pipeline Overview
1. **Column Canonicalization:** Implemented alias lookup matching user-uploaded column variants (e.g. `turnover`, `sales` $\to$ `Revenue`).
2. **Duplicate Removal:** Exact duplicated records and primary key duplicates on `Order ID` were identified and removed.
3. **Data Type Coercion:** Dates were parsed into standard timestamps; numeric fields had currency symbols (`₹`, `$`), commas, and whitespace removed prior to float conversion.
4. **Missing Value Imputation:** Numerical features with nulls were imputed using median values; categorical features were imputed using mode or categorized as `'Unknown'`.
5. **Mathematical Integrity Verification:** Programmatically checked and recalculated derivative financial variables ($Revenue$, $Cost$, $Profit$, and $Profit Margin$).
6. **Outlier Detection:** Detected anomalies using the Interquartile Range (IQR) method:
   $$\text{IQR} = Q_3 - Q_1$$
   $$\text{Upper Bound} = Q_3 + 1.5 \times \text{IQR}, \quad \text{Lower Bound} = \max(0, Q_1 - 1.5 \times \text{IQR})$$
7. **Database Audit Logging:** Every cleaning operation was logged into SQLite database table `processing_logs`.

---

## 4. DATA ANALYSIS

### 4.1 Descriptive Statistical Summary
- **Total Gross Enterprise Revenue:** ₹10,48,25,940.00
- **Total Enterprise Gross Profit:** ₹2,66,12,380.00
- **Overall Operating Profit Margin:** 25.39%
- **Total Customer Transactions:** 3,650 orders
- **Total Unique Customers:** 450 customers
- **Average Order Value (AOV):** ₹28,719.44
- **Total Physical Products Sold:** 8,245 units

### 4.2 Key Findings
1. **High Profit Margin Resilience:** The business sustains a gross margin of ~25.4%, driven by strong margins in Electronics and Apparel.
2. **Q4 Holiday Seasonality:** Sales surge significantly (35-42% increase) from October to December.
3. **Pareto Distribution:** Top 20% of products generate over 78% of cumulative revenues.
4. **Regional Dominance:** The South Region (Hyderabad, Warangal, Bengaluru) contributes 38% of revenue.
5. **Digital Payment Adoption:** UPI and Credit Cards account for >68% of transaction volume.

---

## 5. VISUALISATION

### Figure 5.1: Monthly Sales and Profit Progression (2024 - 2026)
- **Axes:** X-Axis: Timeline (Year-Month); Y-Axis: Amount (₹ in Thousands).
- **Caption:** Multi-year chronological trend of gross revenue and profit progression.
- **Conclusion:** Demonstrates strong revenue expansion across 35 months, with recurring festive peaks in October and November.

### Figure 5.2: Category-wise Revenue and Profit Comparison
- **Axes:** X-Axis: Product Category; Y-Axis: Amount (₹ in Thousands).
- **Caption:** Side-by-side grouped bar chart comparing gross revenue and net profit across all product verticals.
- **Conclusion:** Electronics and Fashion represent the largest revenue drivers, while Health & Personal Care yields high profit margins per unit.

### Figure 5.3: Regional Sales Contribution Share
- **Axes:** Percentage distribution across geographic territories.
- **Caption:** Donut chart illustrating regional sales contribution shares across India.
- **Conclusion:** South zone leads with 38% market share, followed by West (25%) and North (22%).

### Figure 5.4: Customer RFM Behavioral Segmentation
- **Axes:** X-Axis: Customer Count; Y-Axis: Customer Behavioral Segment.
- **Caption:** Horizontal bar chart classifying customer volume into RFM behavioral tiers.
- **Conclusion:** A high-value cohort of 'Champions' and 'Loyal' customers accounts for 58% of repeat sales.

### Figure 5.5: Machine Learning Sales Forecast: Historical vs. Predicted
- **Axes:** X-Axis: Calendar Date; Y-Axis: Sales Volume (₹ in Thousands).
- **Caption:** Time-series forecast combining 90-day actuals with a 45-day Ridge Regression prediction interval.
- **Conclusion:** Captures weekly seasonality and recurring cyclical fluctuations, providing inventory procurement schedules with an 80% confidence interval.

### Figure 5.6: Revenue vs. Cost Distribution
- **Axes:** X-Axis: Order Cost (₹); Y-Axis: Order Revenue (₹).
- **Caption:** Scatter plot displaying order revenue vs cost with breakeven threshold.
- **Conclusion:** Confirms healthy pricing discipline with positive margin spreads across all transactions.

---

## 6. FINAL CONCLUSION
1. **Direct Answers to Objectives:**
   - Real-time KPI monitoring provides automated tracking of enterprise revenue, profit, and order volumes.
   - RFM customer segmentation identifies high-value accounts and informs retention workflows.
   - Machine learning algorithms generate actionable forward-looking demand schedules.
2. **Practical Business Applications:**
   - Inventory Managers optimize distribution center stocking based on regional demand.
   - Marketing Teams launch tailored promotional campaigns for specific customer segments.
   - Finance Teams monitor category-level profit margins to prevent margin erosion.

---

## 7. FUTURE OUTCOMES AND LIMITATIONS
1. **Limitations:**
   - Transaction logs model digital/ERP sales and do not track physical in-store footfall traffic.
   - Competitive price intelligence and external macroeconomic indicators were not incorporated.
2. **Future Scope:**
   - Real-time streaming integration with Apache Kafka for sub-second dashboard telemetry.
   - Deep learning models (Temporal Fusion Transformers) for multi-horizon demand forecasting.
   - Cloud containerization via Docker with PostgreSQL backend storage.

---

## APPENDIX: CODE & REPOSITORY

- **Technology Stack:** Python 3.14, Streamlit, Pandas, NumPy, Plotly, Scikit-learn, SQLite3, OpenPyXL, Python-Docx
- **Main Entrypoint:** `streamlit run app.py`

| Submitted by: [Student Name] | Faculty Signature: __________________ |
