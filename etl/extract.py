"""Extract raw data from the main transactional database."""
from sqlalchemy import create_engine, text
from config import MAIN_DB_URL, MAIN_ORDERS_TABLE, MAIN_ORDER_ITEMS_TABLE, MAIN_PRODUCTS_TABLE

engine = create_engine(MAIN_DB_URL)


def get_last_etl_run():
    """Get the timestamp of the last successful ETL run from reporting DB."""
    from sqlalchemy import create_engine
    from config import REPORTING_DB_URL, REPORTING_ETL_LOG

    rep_engine = create_engine(REPORTING_DB_URL)
    with rep_engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT MAX(last_order_time) FROM {REPORTING_ETL_LOG}
        """))
        row = result.fetchone()
        return row[0] if row and row[0] else None


def extract_new_orders(since_timestamp=None):
    """Pull orders and items created after the last ETL run."""
    with engine.connect() as conn:
        if since_timestamp:
            query = text(f"""
                SELECT 
                    o.id as order_id,
                    o.customer_name,
                    o.customer_email,
                    o.customer_phone,
                    o.shipping_address,
                    o.payment_method,
                    o.total_amount,
                    o.status,
                    o.created_at,
                    oi.id as item_id,
                    oi.product_id,
                    oi.quantity,
                    oi.unit_price
                FROM {MAIN_ORDERS_TABLE} o
                JOIN {MAIN_ORDER_ITEMS_TABLE} oi ON o.id = oi.order_id
                WHERE o.created_at > :since
                ORDER BY o.created_at
            """)
            result = conn.execute(query, {"since": since_timestamp})
        else:
            query = text(f"""
                SELECT 
                    o.id as order_id,
                    o.customer_name,
                    o.customer_email,
                    o.customer_phone,
                    o.shipping_address,
                    o.payment_method,
                    o.total_amount,
                    o.status,
                    o.created_at,
                    oi.id as item_id,
                    oi.product_id,
                    oi.quantity,
                    oi.unit_price
                FROM {MAIN_ORDERS_TABLE} o
                JOIN {MAIN_ORDER_ITEMS_TABLE} oi ON o.id = oi.order_id
                ORDER BY o.created_at
            """)
            result = conn.execute(query)

        rows = result.mappings().all()
        return [dict(row) for row in rows]


def extract_all_products():
    """Pull all products for dimension table."""
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT * FROM {MAIN_PRODUCTS_TABLE}"))
        rows = result.mappings().all()
        return [dict(row) for row in rows]
