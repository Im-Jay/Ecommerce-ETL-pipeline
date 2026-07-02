"""
ETL Pipeline Runner — E-Commerce Data Analytics

Main entry point that orchestrates the full ETL pipeline:
    1. EXTRACT  — Read raw CSV files from data/raw/
    2. TRANSFORM — Clean, validate, and enrich the data
    3. LOAD     — Insert into PostgreSQL database

Produces timestamped log output to both console and logs/pipeline.log.

Usage:
    python run_pipeline.py
"""

import sys
import time
import logging
from datetime import datetime

from config import LOG_FILE, LOG_FORMAT, LOG_DATE_FORMAT, LOG_DIR
from etl.extract import extract_all
from etl.transform import transform_all
from etl.load import load_all


def setup_logging() -> logging.Logger:
    """
    Configure logging for the entire pipeline.

    Sets up dual handlers:
        - FileHandler  → logs/pipeline.log (append mode)
        - StreamHandler → stdout (console)

    Returns:
        Root logger instance
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Prevent duplicate handlers on re-runs
    if root_logger.handlers:
        root_logger.handlers.clear()

    # File handler
    file_handler = logging.FileHandler(
        LOG_FILE, mode="a", encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
    )

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return root_logger


def print_banner(text: str) -> None:
    """Print a prominent section banner to the console."""
    width = 60
    print("\n" + "=" * width)
    print(f"  {text}")
    print("=" * width)


def main():
    """
    Run the complete ETL pipeline: Extract → Transform → Load.

    Logs progress, measures execution time for each phase,
    and prints a summary on success or failure.
    """
    logger = setup_logging()
    pipeline_start = time.time()

    print_banner("E-COMMERCE DATA ANALYTICS ETL PIPELINE")
    print(f"  Started at : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Log file   : {LOG_FILE}")
    print()

    logger.info("=" * 60)
    logger.info("PIPELINE EXECUTION STARTED")
    logger.info("=" * 60)

    try:
        # ── Phase 1: Extract ───────────────────────────────
        print_banner("PHASE 1: EXTRACT")
        extract_start = time.time()
        raw_data = extract_all()
        extract_time = time.time() - extract_start
        print(f"\n  ✓ Extract completed in {extract_time:.2f}s")

        # ── Phase 2: Transform ─────────────────────────────
        print_banner("PHASE 2: TRANSFORM")
        transform_start = time.time()
        cleaned_data = transform_all(raw_data)
        transform_time = time.time() - transform_start
        print(f"\n  ✓ Transform completed in {transform_time:.2f}s")

        # ── Phase 3: Load ─────────────────────────────────
        print_banner("PHASE 3: LOAD")
        load_start = time.time()
        load_results = load_all(cleaned_data)
        load_time = time.time() - load_start
        print(f"\n  ✓ Load completed in {load_time:.2f}s")

        # ── Execution Summary ─────────────────────────────
        total_time = time.time() - pipeline_start

        print_banner("EXECUTION SUMMARY")
        print(f"  Extract time   : {extract_time:.2f}s")
        print(f"  Transform time : {transform_time:.2f}s")
        print(f"  Load time      : {load_time:.2f}s")
        print(f"  Total time     : {total_time:.2f}s")
        print()
        print(f"  Rows loaded:")
        for table, count in load_results.items():
            print(f"    → {table:12s}: {count:>8,}")
        print(f"    → {'TOTAL':12s}: {sum(load_results.values()):>8,}")
        print()
        print(f"  Status: ✓ PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 60)

        logger.info(f"Pipeline completed successfully in {total_time:.2f}s")

    except Exception as e:
        total_time = time.time() - pipeline_start
        logger.error(f"Pipeline FAILED after {total_time:.2f}s: {e}", exc_info=True)

        print_banner("PIPELINE FAILED")
        print(f"  Error    : {e}")
        print(f"  Duration : {total_time:.2f}s")
        print(f"  Logs     : {LOG_FILE}")
        print("=" * 60)

        sys.exit(1)


if __name__ == "__main__":
    main()
