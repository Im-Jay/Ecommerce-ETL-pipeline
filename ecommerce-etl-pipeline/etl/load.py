"""
Load Module — E-Commerce ETL Pipeline

Handles the load phase of the ETL process:
    - Connects to PostgreSQL database
    - Creates normalized tables using schema.sql
    - Loads cleaned DataFrames into the database
    - Prevents duplicate insertion (ON CONFLICT DO NOTHING)
    - Includes transaction handling with rollback on failure
    - Logs insertion counts and errors

Usage:
    from etl.load import load_all
    results = load_all(cleaned_data)
"""

import logging
import psycopg2
import pandas as pd
from config import DB_CONFIG, SQL_DIR

# Module-level logger
logger = logging.getLogger("etl.load")


def get_connection():
    """
    Establish a connection to the PostgreSQL database.

    Uses connection parameters from config.DB_CONFIG (host, port,
    database, user, password). Autocommit is disabled so that
    callers can manage transactions explicitly.

    Returns:
        psycopg2 connection object

    Raises:
        psycopg2.OperationalError: If the connection cannot be established
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        logger.info(
            f"Connected to PostgreSQL: "
            f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        )
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        logger.error(
            "Ensure PostgreSQL is running and the database "
            f"'{DB_CONFIG['database']}' exists."
        )
        raise


def create_tables(conn) -> None:
    """
    Create database tables using the schema.sql file.

    Drops existing tables and recreates them to ensure a clean
    schema on each pipeline run.

    Args:
        conn: Active psycopg2 connection

    Raises:
        FileNotFoundError: If schema.sql is missing
        Exception: If SQL execution fails (transaction is rolled back)
    """
    schema_path = SQL_DIR / "schema.sql"

    if not schema_path.exists():
        logger.error(f"Schema file not found: {schema_path}")
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    logger.info("Creating database tables from schema.sql...")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    cursor = conn.cursor()
    try:
        cursor.execute(schema_sql)
        conn.commit()
        logger.info("  → Database tables created successfully")
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to create tables: {e}")
        raise
    finally:
        cursor.close()


def load_customers(conn, df: pd.DataFrame) -> int:
    """
    Load cleaned customers data into the customers table.

    Uses INSERT ... ON CONFLICT DO NOTHING to safely handle
    any remaining duplicates.

    Args:
        conn: Active psycopg2 connection
        df: Cleaned customers DataFrame

    Returns:
        Number of rows successfully inserted
    """
    logger.info(f"Loading {len(df):,} customers into database...")

    insert_sql = """
        INSERT INTO customers (
            customer_id, customer_name, email, city, state, registration_date
        ) VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (customer_id) DO NOTHING;
    """

    cursor = conn.cursor()
    inserted = 0

    try:
        for _, row in df.iterrows():
            cursor.execute(insert_sql, (
                row["customer_id"],
                row["customer_name"],
                row["email"],
                row["city"],
                row["state"],
                row["registration_date"],
            ))
            inserted += cursor.rowcount

        conn.commit()
        logger.info(f"  → Inserted {inserted:,} customers")
        return inserted
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to load customers: {e}")
        raise
    finally:
        cursor.close()


def load_products(conn, df: pd.DataFrame) -> int:
    """
    Load cleaned products data into the products table.

    Args:
        conn: Active psycopg2 connection
        df: Cleaned products DataFrame

    Returns:
        Number of rows successfully inserted
    """
    logger.info(f"Loading {len(df):,} products into database...")

    insert_sql = """
        INSERT INTO products (
            product_id, product_name, category, price
        ) VALUES (%s, %s, %s, %s)
        ON CONFLICT (product_id) DO NOTHING;
    """

    cursor = conn.cursor()
    inserted = 0

    try:
        for _, row in df.iterrows():
            cursor.execute(insert_sql, (
                row["product_id"],
                row["product_name"],
                row["category"],
                float(row["price"]),
            ))
            inserted += cursor.rowcount

        conn.commit()
        logger.info(f"  → Inserted {inserted:,} products")
        return inserted
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to load products: {e}")
        raise
    finally:
        cursor.close()


def load_orders(conn, df: pd.DataFrame) -> int:
    """
    Load cleaned and enriched orders data into the orders table.

    Args:
        conn: Active psycopg2 connection
        df: Cleaned orders DataFrame (with revenue, order_month, order_year)

    Returns:
        Number of rows successfully inserted
    """
    logger.info(f"Loading {len(df):,} orders into database...")

    insert_sql = """
        INSERT INTO orders (
            order_id, customer_id, product_id, quantity,
            order_date, payment_method, revenue, order_month, order_year
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (order_id) DO NOTHING;
    """

    cursor = conn.cursor()
    inserted = 0

    try:
        for _, row in df.iterrows():
            cursor.execute(insert_sql, (
                row["order_id"],
                row["customer_id"],
                row["product_id"],
                int(row["quantity"]),
                row["order_date"],
                row["payment_method"],
                float(row["revenue"]),
                int(row["order_month"]),
                int(row["order_year"]),
            ))
            inserted += cursor.rowcount

        conn.commit()
        logger.info(f"  → Inserted {inserted:,} orders")
        return inserted
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to load orders: {e}")
        raise
    finally:
        cursor.close()


def load_all(cleaned_data: dict) -> dict:
    """
    Execute the full load phase.

    Connects to PostgreSQL, creates tables, and loads all cleaned
    datasets. Tables are created fresh on each run (DROP + CREATE).

    Args:
        cleaned_data: Dictionary of cleaned DataFrames:
            {
                'customers': DataFrame,
                'products':  DataFrame,
                'orders':    DataFrame,
            }

    Returns:
        Dictionary with insertion counts per table:
            {'customers': int, 'products': int, 'orders': int}

    Raises:
        Exception: If connection or loading fails (propagated after logging)
    """
    logger.info("=" * 60)
    logger.info("LOAD PHASE — Loading data into PostgreSQL")
    logger.info("=" * 60)

    conn = None
    results = {}

    try:
        conn = get_connection()
        create_tables(conn)

        # Load in dependency order: customers → products → orders
        results["customers"] = load_customers(conn, cleaned_data["customers"])
        results["products"] = load_products(conn, cleaned_data["products"])
        results["orders"] = load_orders(conn, cleaned_data["orders"])

        total = sum(results.values())
        logger.info(f"Load phase completed — {total:,} total rows loaded")

    except Exception as e:
        logger.error(f"Load phase failed: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")

    return results
