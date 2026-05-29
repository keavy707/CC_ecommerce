"""Load transformed data into the reporting database."""
from sqlalchemy import create_engine, text
from config import (
    REPORTING_DB_URL,
    REPORTING_FACT_SALES,
    REPORTING_DIM_PRODUCTS,
    REPORTING_DIM_DATE,
    REPORTING_DIM_CUSTOMERS,
    REPORTING_ETL_LOG,
)

engine = create_engine(REPORTING_DB_URL)


def ensure_schema():
    """Create reporting tables if they don't exist."""
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))  # Close any open transaction

        # dim_products
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {REPORTING_DIM_PRODUCTS} (
                product_id VARCHAR PRIMARY KEY,
                code VARCHAR,
                name VARCHAR,
                type VARCHAR,
                price NUMERIC(10,2)
            )
        """))

        # dim_date
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {REPORTING_DIM_DATE} (
                date_key INTEGER PRIMARY KEY,
                full_date DATE,
                year INTEGER,
                month INTEGER,
                month_name VARCHAR,
                day INTEGER,
                weekday VARCHAR
            )
        """))

        # dim_customers
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {REPORTING_DIM_CUSTOMERS} (
                customer_email VARCHAR PRIMARY KEY,
                customer_name VARCHAR,
                total_orders INTEGER,
                total_spent NUMERIC(10,2),
                first_order TIMESTAMP,
                last_order TIMESTAMP
            )
        """))

        # fact_sales
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {REPORTING_FACT_SALES} (
                sale_id SERIAL PRIMARY KEY,
                order_id INTEGER,
                product_id VARCHAR,
                date_key INTEGER,
                quantity INTEGER,
                revenue NUMERIC(10,2),
                customer_email VARCHAR
            )
        """))

        # etl_log
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {REPORTING_ETL_LOG} (
                run_id SERIAL PRIMARY KEY,
                run_time TIMESTAMP DEFAULT NOW(),
                rows_processed INTEGER,
                last_order_time TIMESTAMP,
                status VARCHAR
            )
        """))

        conn.commit()


def load_products(products):
    """Upsert products into dim_products."""
    with engine.connect() as conn:
        for p in products:
            conn.execute(text(f"""
                INSERT INTO {REPORTING_DIM_PRODUCTS} (product_id, code, name, type, price)
                VALUES (:product_id, :code, :name, :type, :price)
                ON CONFLICT (product_id) DO UPDATE SET
                    code = EXCLUDED.code,
                    name = EXCLUDED.name,
                    type = EXCLUDED.type,
                    price = EXCLUDED.price
            """), p)
        conn.commit()


def load_dates(dates):
    """Upsert dates into dim_date."""
    with engine.connect() as conn:
        for d in dates:
            conn.execute(text(f"""
                INSERT INTO {REPORTING_DIM_DATE} (date_key, full_date, year, month, month_name, day, weekday)
                VALUES (:date_key, :full_date, :year, :month, :month_name, :day, :weekday)
                ON CONFLICT (date_key) DO NOTHING
            """), d)
        conn.commit()


def load_sales(sales):
    """Insert sales into fact_sales."""
    with engine.connect() as conn:
        for s in sales:
            conn.execute(text(f"""
                INSERT INTO {REPORTING_FACT_SALES} (order_id, product_id, date_key, quantity, revenue, customer_email)
                VALUES (:order_id, :product_id, :date_key, :quantity, :revenue, :customer_email)
            """), s)
        conn.commit()


def load_customers(customers):
    """Upsert customers into dim_customers."""
    with engine.connect() as conn:
        for c in customers:
            conn.execute(text(f"""
                INSERT INTO {REPORTING_DIM_CUSTOMERS} 
                (customer_email, customer_name, total_orders, total_spent, first_order, last_order)
                VALUES (:customer_email, :customer_name, :total_orders, :total_spent, :first_order, :last_order)
                ON CONFLICT (customer_email) DO UPDATE SET
                    customer_name = EXCLUDED.customer_name,
                    total_orders = EXCLUDED.total_orders,
                    total_spent = EXCLUDED.total_spent,
                    last_order = EXCLUDED.last_order
            """), c)
        conn.commit()


def log_etl_run(rows_processed, last_order_time, status="success"):
    """Record ETL run in log table."""
    with engine.connect() as conn:
        conn.execute(text(f"""
            INSERT INTO {REPORTING_ETL_LOG} (run_time, rows_processed, last_order_time, status)
            VALUES (NOW(), :rows_processed, :last_order_time, :status)
        """), {
            "rows_processed": rows_processed,
            "last_order_time": last_order_time,
            "status": status,
        })
        conn.commit()
