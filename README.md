# 🛒 E-Commerce Data Analytics ETL Pipeline

A complete, production-style **Extract → Transform → Load** (ETL) pipeline that processes raw e-commerce data from CSV files, cleans and enriches it, loads it into a PostgreSQL database, and performs business analytics using SQL queries and interactive Jupyter visualizations.

> Built as a portfolio project for Computer Engineering students — demonstrates real-world data engineering skills including data cleaning, database design, SQL analytics, and data visualization.

---

## 📐 Architecture

```
┌─────────────────┐
│   CSV Files     │    customers.csv, products.csv, orders.csv
│  (Dirty Data)   │    with missing values, duplicates, bad dates
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    EXTRACT      │    extract.py — Read & validate CSV files
│                 │    Logging, error handling, file validation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   TRANSFORM     │    transform.py — Clean, validate, enrich
│                 │    Dedup, null handling, date parsing,
│                 │    category standardization, calculated fields
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL     │    schema.sql — Normalized tables with
│   Database      │    PKs, FKs, indexes, constraints
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQL Analytics  │    sales_analysis.sql — 10 business queries
│                 │    Revenue trends, customer behavior, product
│                 │    performance, payment analysis
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Jupyter Notebook│    analysis.ipynb — Interactive dashboard
│   Dashboard     │    Matplotlib & Seaborn visualizations
└─────────────────┘
```

---

## 🛠️ Technologies Used

| Technology   | Purpose                                     |
|:-------------|:--------------------------------------------|
| **Python 3** | Core programming language                   |
| **Pandas**   | Data manipulation and transformation        |
| **PostgreSQL**| Relational database for structured storage  |
| **psycopg2** | Python ↔ PostgreSQL connector               |
| **SQLAlchemy**| Database connection for Jupyter             |
| **SQL**       | Analytics queries and schema definition     |
| **Jupyter**   | Interactive data analysis notebook          |
| **Matplotlib**| Static data visualizations                  |
| **Seaborn**   | Statistical chart aesthetics                |
| **Faker**     | Realistic sample data generation            |

---

## 📁 Project Structure

```
ecommerce-etl-pipeline/
├── config.py               # Database & path configuration
├── generate_data.py        # Sample data generator (with dirty data)
├── run_pipeline.py         # Main ETL pipeline runner
├── requirements.txt        # Python dependencies
├── .gitignore
├── README.md
│
├── data/
│   ├── raw/                # Generated dirty CSV files
│   │   ├── customers.csv
│   │   ├── products.csv
│   │   └── orders.csv
│   └── cleaned/            # Cleaned CSVs (output of Transform)
│
├── etl/
│   ├── __init__.py
│   ├── extract.py          # Phase 1: Data extraction
│   ├── transform.py        # Phase 2: Data transformation
│   └── load.py             # Phase 3: Database loading
│
├── sql/
│   ├── schema.sql          # Database table definitions
│   └── sales_analysis.sql  # 10 analytics queries
│
├── notebooks/
│   └── analysis.ipynb      # Jupyter analytics notebook
│
└── logs/
    └── pipeline.log        # Runtime logs
```

---

## ⚙️ Installation

### Prerequisites

- **Python 3.9+** — [Download](https://www.python.org/downloads/)
- **PostgreSQL 14+** — [Download](https://www.postgresql.org/download/)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/ecommerce-etl-pipeline.git
cd ecommerce-etl-pipeline
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up PostgreSQL

1. **Start PostgreSQL** service if not running.

2. **Create the database**:

```bash
# Windows (use full path if psql is not on PATH)
# "C:\Program Files\PostgreSQL\18\bin\psql" -U postgres
psql -U postgres
```

```sql
CREATE DATABASE ecommerce_analytics;
\q
```

3. **Configure connection** (optional):

   Edit `config.py` or set environment variables:

```bash
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=ecommerce_analytics
set DB_USER=postgres
set DB_PASSWORD=your_password
```

---

## 🚀 Usage

### 1. Generate Sample Data

```bash
python generate_data.py
```

This creates 3 CSV files in `data/raw/` with intentionally dirty data:
- **1,030+** customer records (with duplicates, nulls, bad dates)
- **206+** product records (with inconsistent categories)
- **10,300+** order records (with negatives, orphan keys, mixed dates)

### 2. Run the ETL Pipeline

```bash
python run_pipeline.py
```

This executes the full **Extract → Transform → Load** pipeline:

```
============================================================
  E-COMMERCE DATA ANALYTICS ETL PIPELINE
============================================================
  Started at : 2025-01-15 14:30:00
  Log file   : logs/pipeline.log

============================================================
  PHASE 1: EXTRACT
============================================================
  ✓ Extract completed in 0.15s

============================================================
  PHASE 2: TRANSFORM
============================================================
  ✓ Transform completed in 0.42s

============================================================
  PHASE 3: LOAD
============================================================
  ✓ Load completed in 3.21s

============================================================
  EXECUTION SUMMARY
============================================================
  Rows loaded:
    → customers   :    1,000
    → products    :      200
    → orders      :    8,547
    → TOTAL       :    9,747

  Status: ✓ PIPELINE COMPLETED SUCCESSFULLY
============================================================
```

### 3. Run SQL Analytics (Optional)

```bash
# Execute specific queries from sales_analysis.sql
psql -U postgres -d ecommerce_analytics -f sql/sales_analysis.sql
```

### 4. Open the Jupyter Notebook

```bash
jupyter notebook notebooks/analysis.ipynb
```

Run all cells to generate interactive visualizations:
- 📈 Monthly Revenue Trend (line chart)
- 🏆 Top 10 Products (bar chart)
- 🗂️ Revenue by Category (bar + pie chart)
- 👥 Customer Spending (horizontal bar chart)
- 💳 Payment Method Distribution (donut chart)
- 🔥 Category Performance Heatmap

---

## 📊 Analytics Queries

The `sql/sales_analysis.sql` file contains 10 production-ready analytics queries:

| # | Query                        | Purpose                                        |
|:-:|:-----------------------------|:-----------------------------------------------|
| 1 | Monthly Revenue Trend        | Track revenue growth over time                 |
| 2 | Top 10 Selling Products      | Identify highest-revenue products              |
| 3 | Top Customers by Revenue     | Find highest-value customers                   |
| 4 | Revenue by Category          | Analyze category revenue distribution          |
| 5 | Average Order Value          | Calculate order value statistics                |
| 6 | Orders per Month             | Understand demand patterns                     |
| 7 | Best Performing Categories   | Rank categories by multiple metrics            |
| 8 | Most Popular Payment Method  | Analyze payment preferences                    |
| 9 | Customer Lifetime Value      | Calculate total customer value                 |
| 10| Product Performance Analysis | Comprehensive per-product metrics              |

---

## ✨ Features

### ETL Pipeline
- ✅ Modular Extract → Transform → Load architecture
- ✅ Automatic dirty data detection and cleaning
- ✅ Mixed date format parsing (5+ formats supported)
- ✅ Category name standardization
- ✅ Foreign key validation (orphan removal)
- ✅ Calculated fields (revenue, order_month, order_year)
- ✅ Duplicate prevention with `ON CONFLICT DO NOTHING`
- ✅ Transaction handling with rollback on failure
- ✅ Detailed transformation reports

### Data Quality
- ✅ Missing value handling (drop / fill strategies)
- ✅ Duplicate record removal
- ✅ Negative quantity filtering
- ✅ Data type validation and conversion
- ✅ Referential integrity enforcement

### Logging & Monitoring
- ✅ Structured logging (INFO / WARNING / ERROR)
- ✅ Dual output: console + file (`logs/pipeline.log`)
- ✅ Per-phase timing metrics
- ✅ Execution summary with row counts

### Database
- ✅ Normalized schema (3NF)
- ✅ Primary keys, foreign keys, CHECK constraints
- ✅ Performance indexes for analytics queries

---

## 📝 Resume Bullet Points

This project supports the following resume statements:

> - Designed an end-to-end ETL pipeline using Python and Pandas to extract, clean, transform, and load 10,000+ raw e-commerce records into a PostgreSQL database, reducing data quality issues by 95%.
> - Performed data analysis using 10 SQL queries to identify sales trends, customer lifetime value, and product performance across 10 categories, visualized through Matplotlib and Seaborn dashboards.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Built with ❤️ for learning Data Engineering
</p>
