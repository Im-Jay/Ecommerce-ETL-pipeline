"""
Extract Module — E-Commerce ETL Pipeline

Handles the extraction phase of the ETL process:
    - Reads raw CSV files from the data/raw/ directory
    - Validates file existence and integrity
    - Logs extraction status (row counts, columns, errors)
    - Returns DataFrames for downstream transformation

Usage:
    from etl.extract import extract_all
    raw_data = extract_all()  # returns dict of DataFrames
"""

import logging
import pandas as pd
from pathlib import Path
from config import CSV_FILES

# Module-level logger
logger = logging.getLogger("etl.extract")


def extract_csv(name: str, filepath: Path) -> pd.DataFrame:
    """
    Extract data from a single CSV file with validation.

    Reads the entire file as string dtype to preserve raw data
    exactly as it appears, deferring type conversion to the
    transform phase.

    Args:
        name: Logical name of the dataset (e.g., 'customers')
        filepath: Absolute path to the CSV file

    Returns:
        DataFrame containing the raw data

    Raises:
        FileNotFoundError: If the CSV file does not exist
        pd.errors.EmptyDataError: If the CSV file has no data
        Exception: For any other read errors
    """
    logger.info(f"Extracting '{name}' from: {filepath}")

    # Validate file existence
    if not filepath.exists():
        logger.error(f"File not found: {filepath}")
        raise FileNotFoundError(f"CSV file not found: {filepath}")

    # Validate file is not empty
    if filepath.stat().st_size == 0:
        logger.error(f"File is empty: {filepath}")
        raise pd.errors.EmptyDataError(f"CSV file is empty: {filepath}")

    # Read CSV — all columns as string to preserve raw state
    try:
        df = pd.read_csv(filepath, dtype=str)
    except pd.errors.ParserError as e:
        logger.error(f"Failed to parse '{name}': {e}")
        raise

    # Log extraction metrics
    logger.info(f"  → Extracted {len(df):,} rows × {len(df.columns)} columns")
    logger.info(f"  → Columns: {list(df.columns)}")

    # Warn about potential issues
    null_count = df.isna().sum().sum()
    if null_count > 0:
        logger.warning(f"  → Found {null_count} native null values in '{name}'")

    return df


def extract_all() -> dict:
    """
    Extract all configured CSV datasets.

    Iterates through all files defined in config.CSV_FILES,
    extracts each one, and collects results. Continues past
    individual file failures to extract as much data as possible.

    Returns:
        Dictionary mapping dataset names to their raw DataFrames:
        {
            'customers': DataFrame,
            'products':  DataFrame,
            'orders':    DataFrame,
        }

    Raises:
        RuntimeError: If no datasets could be extracted
    """
    logger.info("=" * 60)
    logger.info("EXTRACT PHASE — Starting data extraction")
    logger.info("=" * 60)

    extracted_data = {}
    errors = []

    for name, filepath in CSV_FILES.items():
        try:
            extracted_data[name] = extract_csv(name, filepath)
        except FileNotFoundError as e:
            errors.append(f"{name}: {e}")
            logger.error(f"Skipping '{name}': file not found")
        except pd.errors.EmptyDataError as e:
            errors.append(f"{name}: {e}")
            logger.error(f"Skipping '{name}': file is empty")
        except Exception as e:
            errors.append(f"{name}: {e}")
            logger.error(f"Unexpected error extracting '{name}': {e}")

    # Summary
    if errors:
        logger.warning(f"Extraction completed with {len(errors)} error(s):")
        for err in errors:
            logger.warning(f"  - {err}")

    if not extracted_data:
        msg = "No datasets could be extracted. Cannot proceed."
        logger.error(msg)
        raise RuntimeError(msg)

    logger.info(
        f"Extraction complete: {len(extracted_data)} dataset(s) extracted "
        f"({', '.join(extracted_data.keys())})"
    )

    return extracted_data
