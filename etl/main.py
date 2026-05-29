"""ETL orchestrator — runs the full pipeline."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from extract import get_last_etl_run, extract_new_orders, extract_all_products
from transform import transform_sales, transform_products, generate_date_range, transform_customers
from load import ensure_schema, load_products, load_dates, load_sales, load_customers, log_etl_run
from datetime import datetime


def run_etl():
    print("=" * 50)
    print("KAWAII ATELIER — ETL Pipeline")
    print("=" * 50)

    #  Ensure schema exists
    print("[1/6] Ensuring reporting schema...")
    ensure_schema()

    #  Get last run timestamp
    print("[2/6] Checking last ETL run...")
    last_run = get_last_etl_run()
    if last_run:
        print(f"      Last run: {last_run}")
    else:
        print("      No previous run found — full load")

    #  Extract
    print("[3/6] Extracting data from main DB...")
    raw_orders = extract_new_orders(last_run)
    print(f"      Found {len(raw_orders)} order items")

    if not raw_orders:
        print("      No new data. ETL complete.")
        log_etl_run(0, last_run or datetime.now(), "no_new_data")
        return

    raw_products = extract_all_products()
    print(f"      Found {len(raw_products)} products")

    #  Transform
    print("[4/6] Transforming data...")
    sales_facts = transform_sales(raw_orders)
    product_dims = transform_products(raw_products)
    customer_dims = transform_customers(raw_orders)

    # Generate dates
    all_dates = set()
    for s in sales_facts:
        all_dates.add(s["created_at"].date())
    if all_dates:
        min_date = min(all_dates)
        max_date = max(all_dates)
        date_dims = generate_date_range(min_date, max_date)
    else:
        date_dims = []

    print(f"      Sales facts: {len(sales_facts)}")
    print(f"      Date dimensions: {len(date_dims)}")
    print(f"      Customer dimensions: {len(customer_dims)}")

    # Load
    print("[5/6] Loading into reporting DB...")
    load_products(product_dims)
    load_dates(date_dims)
    load_sales(sales_facts)
    load_customers(customer_dims)
    print("      Load complete")

    # Log
    print("[6/6] Logging ETL run...")
    last_order_time = max(s["created_at"] for s in sales_facts)
    log_etl_run(len(sales_facts), last_order_time, "success")
    print(f"      Logged. Last order time: {last_order_time}")

    print("=" * 50)
    print("ETL COMPLETE ✦")
    print("=" * 50)


if __name__ == "__main__":
    run_etl()
