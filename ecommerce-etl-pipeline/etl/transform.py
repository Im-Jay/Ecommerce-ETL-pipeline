"""
Transform Module — E-Commerce ETL Pipeline

Handles the transformation phase of the ETL process:
    - Removes duplicate records
    - Handles missing / sentinel null values
    - Standardizes category names to a canonical form
    - Converts date columns from mixed formats to datetime
    - Removes invalid records (negative quantities, orphan FKs)
    - Creates calculated fields (revenue, order_month, order_year)
    - Generates a detailed transformation report
    - Saves cleaned data to data/cleaned/

Usage:
    from etl.transform import transform_all
    cleaned = transform_all(raw_data)
"""

import logging
import pandas as pd
import numpy as np
from config import CLEANED_DATA_DIR

# Module-level logger
logger = logging.getLogger("etl.transform")

# ── Sentinel values treated as NULL ────────────────────────
SENTINEL_NULLS = ["", "N/A", "null", "None", "none", "NA", "n/a", "nan"]

# ── Category standardization mapping ──────────────────────
# Maps every known variant (lowercase key) → canonical name
CATEGORY_MAP = {
    "electronics": "Electronics", "electronicss": "Electronics",
    "electronic": "Electronics",
    "clothing": "Clothing", "clothings": "Clothing", "apparel": "Clothing",
    "home & kitchen": "Home & Kitchen", "home&kitchen": "Home & Kitchen",
    "home and kitchen": "Home & Kitchen",
    "books": "Books", "book": "Books",
    "sports & outdoors": "Sports & Outdoors", "sports": "Sports & Outdoors",
    "outdoors": "Sports & Outdoors",
    "beauty & health": "Beauty & Health", "beauty": "Beauty & Health",
    "health & beauty": "Beauty & Health",
    "toys & games": "Toys & Games", "toys": "Toys & Games",
    "games": "Toys & Games",
    "automotive": "Automotive", "auto": "Automotive",
    "grocery": "Grocery", "groceries": "Grocery",
    "office supplies": "Office Supplies", "office": "Office Supplies",
    "stationery": "Office Supplies",
}


def _replace_sentinels(df: pd.DataFrame) -> pd.DataFrame:
    """Replace known sentinel null strings with np.nan."""
    return df.replace(SENTINEL_NULLS, np.nan)


def parse_mixed_dates(series: pd.Series) -> pd.Series:
    """
    Parse a Series of dates in mixed formats into proper datetime.

    Tries multiple explicit date formats sequentially, then falls
    back to pandas' infer_datetime_format. Unparseable values → NaT.

    Args:
        series: Series containing date strings in varied formats

    Returns:
        Series with parsed datetime values (NaT for failures)
    """
    formats = [
        "%Y-%m-%d",       # 2024-01-15 (standard)
        "%d/%m/%Y",       # 15/01/2024
        "%m-%d-%Y",       # 01-15-2024
        "%d-%m-%Y",       # 15-01-2024
        "%Y/%m/%d",       # 2024/01/15
        "%B %d, %Y",     # January 15, 2024
    ]

    result = pd.Series([pd.NaT] * len(series), index=series.index)
    remaining_mask = series.notna()

    for fmt in formats:
        if not remaining_mask.any():
            break

        parsed = pd.to_datetime(
            series[remaining_mask], format=fmt, errors="coerce"
        )
        newly_parsed = parsed.notna()

        # Update results for successfully parsed entries
        result[remaining_mask] = result[remaining_mask].where(
            ~newly_parsed, parsed[newly_parsed]
        )

        # Remove successfully parsed from remaining
        remaining_mask = remaining_mask & result.isna()

    # Final fallback: let pandas guess
    if remaining_mask.any():
        fallback = pd.to_datetime(
            series[remaining_mask], errors="coerce", dayfirst=True
        )
        result[remaining_mask] = fallback

    return result


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and validate the customers DataFrame.

    Cleaning steps:
        1. Replace sentinel null values ('', 'N/A', 'null', etc.)
        2. Remove duplicate records by customer_id
        3. Drop rows with missing customer_id
        4. Fill missing names/emails with defaults
        5. Parse registration_date from mixed formats

    Args:
        df: Raw customers DataFrame (all string columns)

    Returns:
        Cleaned customers DataFrame with proper types
    """
    logger.info("Cleaning customers data...")
    initial_count = len(df)

    # Step 1: Sentinel nulls → NaN
    df = _replace_sentinels(df)
    nulls_found = int(df.isna().sum().sum())
    logger.info(f"  → Found {nulls_found} null/sentinel values")

    # Step 2: Deduplicate by customer_id
    dupes = int(df.duplicated(subset=["customer_id"], keep="first").sum())
    df = df.drop_duplicates(subset=["customer_id"], keep="first")
    logger.info(f"  → Removed {dupes} duplicate customer records")

    # Step 3: Drop missing IDs (essential field)
    missing_id = int(df["customer_id"].isna().sum())
    df = df.dropna(subset=["customer_id"])
    if missing_id:
        logger.warning(f"  → Dropped {missing_id} rows with missing customer_id")

    # Step 4: Fill remaining missing values with defaults
    df["customer_name"] = df["customer_name"].fillna("Unknown")
    df["email"] = df["email"].fillna("unknown@example.com")
    df["city"] = df["city"].fillna("Unknown")
    df["state"] = df["state"].fillna("Unknown")

    # Step 5: Parse dates
    df["registration_date"] = parse_mixed_dates(df["registration_date"])
    invalid_dates = int(df["registration_date"].isna().sum())
    if invalid_dates:
        logger.warning(f"  → {invalid_dates} unparseable dates → defaulting to 2023-01-01")
        df["registration_date"] = df["registration_date"].fillna(
            pd.Timestamp("2023-01-01")
        )

    logger.info(f"  → Customers: {initial_count:,} → {len(df):,} records")
    return df.reset_index(drop=True)


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and validate the products DataFrame.

    Cleaning steps:
        1. Replace sentinel null values
        2. Remove duplicate records by product_id
        3. Drop rows with missing product_id
        4. Standardize category names using CATEGORY_MAP
        5. Validate and fix prices (must be positive numeric)

    Args:
        df: Raw products DataFrame (all string columns)

    Returns:
        Cleaned products DataFrame with proper types
    """
    logger.info("Cleaning products data...")
    initial_count = len(df)

    # Step 1: Sentinel nulls
    df = _replace_sentinels(df)

    # Step 2: Deduplicate
    dupes = int(df.duplicated(subset=["product_id"], keep="first").sum())
    df = df.drop_duplicates(subset=["product_id"], keep="first")
    logger.info(f"  → Removed {dupes} duplicate product records")

    # Step 3: Drop missing IDs
    missing_id = int(df["product_id"].isna().sum())
    df = df.dropna(subset=["product_id"])
    if missing_id:
        logger.warning(f"  → Dropped {missing_id} rows with missing product_id")

    # Step 4: Standardize categories
    df["category"] = df["category"].fillna("Uncategorized")
    category_fixes = 0

    def _standardize(cat):
        """Map variant category names to their canonical form."""
        nonlocal category_fixes
        key = str(cat).strip().lower()
        if key in CATEGORY_MAP:
            canonical = CATEGORY_MAP[key]
            if cat != canonical:
                category_fixes += 1
            return canonical
        return cat

    df["category"] = df["category"].apply(_standardize)
    logger.info(f"  → Standardized {category_fixes} inconsistent category names")

    # Step 5: Validate prices
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    median_price = df["price"].median()

    invalid_mask = df["price"].isna() | (df["price"] <= 0)
    invalid_prices = int(invalid_mask.sum())

    if invalid_prices:
        df.loc[invalid_mask, "price"] = median_price
        logger.warning(
            f"  → Fixed {invalid_prices} invalid prices (set to median: ₹{median_price:.2f})"
        )

    df["price"] = df["price"].round(2)

    logger.info(f"  → Products: {initial_count:,} → {len(df):,} records")
    return df.reset_index(drop=True)


def clean_orders(
    df: pd.DataFrame,
    valid_customer_ids: set,
    valid_product_ids: set,
) -> pd.DataFrame:
    """
    Clean and validate the orders DataFrame.

    Cleaning steps:
        1. Replace sentinel null values
        2. Remove duplicate records by order_id
        3. Drop rows with missing order_id
        4. Convert quantity to numeric, remove negatives/zeros
        5. Parse order_date from mixed formats
        6. Remove orders with invalid (orphan) foreign keys
        7. Fill missing payment methods

    Args:
        df: Raw orders DataFrame (all string columns)
        valid_customer_ids: Set of IDs from cleaned customers
        valid_product_ids: Set of IDs from cleaned products

    Returns:
        Cleaned orders DataFrame with proper types
    """
    logger.info("Cleaning orders data...")
    initial_count = len(df)

    # Step 1: Sentinel nulls
    df = _replace_sentinels(df)

    # Step 2: Deduplicate
    dupes = int(df.duplicated(subset=["order_id"], keep="first").sum())
    df = df.drop_duplicates(subset=["order_id"], keep="first")
    logger.info(f"  → Removed {dupes} duplicate order records")

    # Step 3: Drop missing IDs
    missing_id = int(df["order_id"].isna().sum())
    df = df.dropna(subset=["order_id"])
    if missing_id:
        logger.warning(f"  → Dropped {missing_id} rows with missing order_id")

    # Step 4: Validate quantities
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    negative_qty = int((df["quantity"] < 0).sum())
    null_qty = int(df["quantity"].isna().sum())

    # Remove invalid quantities (negative, zero, or null)
    df = df[(df["quantity"] > 0) & df["quantity"].notna()]
    df["quantity"] = df["quantity"].astype(int)
    logger.info(
        f"  → Removed {negative_qty} negative + {null_qty} null quantities"
    )

    # Step 5: Parse dates
    df["order_date"] = parse_mixed_dates(df["order_date"])
    invalid_dates = int(df["order_date"].isna().sum())
    df = df.dropna(subset=["order_date"])
    if invalid_dates:
        logger.warning(f"  → Removed {invalid_dates} orders with unparseable dates")

    # Step 6: Validate foreign keys
    orphan_cust = ~df["customer_id"].isin(valid_customer_ids)
    orphan_prod = ~df["product_id"].isin(valid_product_ids)
    orphan_count = int((orphan_cust | orphan_prod).sum())
    df = df[~orphan_cust & ~orphan_prod]
    if orphan_count:
        logger.warning(f"  → Removed {orphan_count} orders with invalid foreign keys")

    # Step 7: Fill missing payment methods
    df["payment_method"] = df["payment_method"].fillna("Unknown")

    logger.info(f"  → Orders: {initial_count:,} → {len(df):,} records")
    return df.reset_index(drop=True)


def enrich_orders(orders_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich orders with calculated fields.

    Adds:
        - revenue: quantity × price (joined from products table)
        - order_month: month number (1-12) from order_date
        - order_year: four-digit year from order_date

    Args:
        orders_df: Cleaned orders DataFrame
        products_df: Cleaned products DataFrame (for price lookup)

    Returns:
        Enriched orders DataFrame with new calculated columns
    """
    logger.info("Enriching orders with calculated fields...")

    # Merge to get product price
    df = orders_df.merge(
        products_df[["product_id", "price"]],
        on="product_id",
        how="left",
    )

    # Calculate revenue
    df["revenue"] = (df["quantity"] * df["price"]).round(2)

    # Extract temporal fields
    df["order_month"] = df["order_date"].dt.month
    df["order_year"] = df["order_date"].dt.year

    logger.info(f"  → Added: revenue, order_month, order_year")
    logger.info(f"  → Total revenue: ₹{df['revenue'].sum():,.2f}")
    logger.info(f"  → Average order value: ₹{df['revenue'].mean():,.2f}")

    return df


def generate_report(raw_data: dict, cleaned_data: dict) -> str:
    """
    Generate a detailed transformation report.

    Compares raw vs. cleaned row counts for each dataset and
    prints enrichment summary statistics.

    Args:
        raw_data: Dict of raw DataFrames (before cleaning)
        cleaned_data: Dict of cleaned DataFrames (after cleaning)

    Returns:
        Multi-line report string (also logged at INFO level)
    """
    lines = [
        "",
        "=" * 60,
        "  TRANSFORMATION REPORT",
        "=" * 60,
        "",
    ]

    total_raw = 0
    total_clean = 0

    for name in raw_data:
        raw_count = len(raw_data[name])
        clean_count = len(cleaned_data[name])
        removed = raw_count - clean_count
        pct = (removed / raw_count * 100) if raw_count > 0 else 0

        total_raw += raw_count
        total_clean += clean_count

        lines.extend([
            f"  {name.upper()}:",
            f"    Raw records:     {raw_count:>8,}",
            f"    Cleaned records: {clean_count:>8,}",
            f"    Removed:         {removed:>8,} ({pct:.1f}%)",
            "",
        ])

    # Enrichment summary
    if "orders" in cleaned_data and "revenue" in cleaned_data["orders"].columns:
        orders = cleaned_data["orders"]
        lines.extend([
            "  ENRICHMENT SUMMARY:",
            f"    Total orders:      {len(orders):>8,}",
            f"    Total revenue:     ₹{orders['revenue'].sum():>12,.2f}",
            f"    Avg order value:   ₹{orders['revenue'].mean():>12,.2f}",
            f"    Date range:        {orders['order_date'].min().date()} → "
            f"{orders['order_date'].max().date()}",
            "",
        ])

    total_removed = total_raw - total_clean
    total_pct = (total_removed / total_raw * 100) if total_raw > 0 else 0
    lines.extend([
        f"  TOTAL: {total_raw:,} → {total_clean:,} ({total_removed:,} removed, {total_pct:.1f}%)",
        "=" * 60,
    ])

    report = "\n".join(lines)
    logger.info(report)
    return report


def save_cleaned_data(data: dict) -> None:
    """
    Save cleaned DataFrames as CSV files in data/cleaned/.

    Args:
        data: Dict mapping dataset names to cleaned DataFrames
    """
    CLEANED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for name, df in data.items():
        filepath = CLEANED_DATA_DIR / f"{name}_cleaned.csv"
        df.to_csv(filepath, index=False)
        logger.info(f"  → Saved {name} ({len(df):,} rows) to: {filepath}")


def transform_all(raw_data: dict) -> dict:
    """
    Execute the full transformation pipeline.

    Orchestrates cleaning, validation, enrichment, reporting,
    and saving of all datasets.

    Args:
        raw_data: Dictionary of raw DataFrames from the extract phase

    Returns:
        Dictionary of cleaned and enriched DataFrames:
        {
            'customers': DataFrame,
            'products':  DataFrame,
            'orders':    DataFrame (with revenue, month, year),
        }
    """
    logger.info("=" * 60)
    logger.info("TRANSFORM PHASE — Starting data transformation")
    logger.info("=" * 60)

    # Clean individual datasets
    customers = clean_customers(raw_data["customers"].copy())
    products = clean_products(raw_data["products"].copy())

    # Build valid ID sets for foreign key validation
    valid_customer_ids = set(customers["customer_id"].unique())
    valid_product_ids = set(products["product_id"].unique())

    orders = clean_orders(
        raw_data["orders"].copy(),
        valid_customer_ids,
        valid_product_ids,
    )

    # Enrich orders with calculated fields
    orders = enrich_orders(orders, products)

    cleaned_data = {
        "customers": customers,
        "products": products,
        "orders": orders,
    }

    # Generate transformation report
    generate_report(raw_data, cleaned_data)

    # Save cleaned data to CSV
    save_cleaned_data(cleaned_data)

    logger.info("Transform phase completed successfully")
    return cleaned_data
