"""ETL configuration — database connections and table names."""
import os
from dotenv import load_dotenv

load_dotenv()

# Main transactional database
MAIN_DB_URL = os.getenv(
    "MAIN_DATABASE_URL",
    "postgresql://ecommerce_user:password@localhost/ecommerce_main"
)

# Reporting/analytics database
REPORTING_DB_URL = os.getenv(
    "REPORTING_DATABASE_URL",
    "postgresql://ecommerce_user:password@localhost/ecommerce_reporting"
)

# Tables
MAIN_ORDERS_TABLE = "orders"
MAIN_ORDER_ITEMS_TABLE = "order_items"
MAIN_PRODUCTS_TABLE = "products"

REPORTING_FACT_SALES = "fact_sales"
REPORTING_DIM_PRODUCTS = "dim_products"
REPORTING_DIM_DATE = "dim_date"
REPORTING_DIM_CUSTOMERS = "dim_customers"
REPORTING_ETL_LOG = "etl_log"
