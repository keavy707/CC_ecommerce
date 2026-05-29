"""SQL queries for the analytics dashboard."""
from sqlalchemy import create_engine, text
from config import REPORTING_DB_URL

engine = create_engine(REPORTING_DB_URL)


def get_total_revenue():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COALESCE(SUM(revenue), 0) FROM fact_sales"))
        return result.scalar()


def get_total_orders():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(DISTINCT order_id) FROM fact_sales"))
        return result.scalar()


def get_total_products_sold():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COALESCE(SUM(quantity), 0) FROM fact_sales"))
        return result.scalar()


def get_total_customers():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(DISTINCT customer_email) FROM fact_sales"))
        return result.scalar()


def get_sales_by_month():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT d.year, d.month, d.month_name, SUM(f.revenue) as revenue, SUM(f.quantity) as qty
            FROM fact_sales f
            JOIN dim_date d ON f.date_key = d.date_key
            GROUP BY d.year, d.month, d.month_name
            ORDER BY d.year, d.month
        """))
        return [dict(row) for row in result.mappings()]


def get_top_products(limit=5):
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT p.name, p.type, SUM(f.quantity) as total_qty, SUM(f.revenue) as total_revenue
            FROM fact_sales f
            JOIN dim_products p ON f.product_id = p.product_id
            GROUP BY p.product_id, p.name, p.type
            ORDER BY total_qty DESC
            LIMIT :limit
        """), {"limit": limit})
        return [dict(row) for row in result.mappings()]


def get_sales_by_product_type():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT p.type, SUM(f.quantity) as qty, SUM(f.revenue) as revenue
            FROM fact_sales f
            JOIN dim_products p ON f.product_id = p.product_id
            GROUP BY p.type
            ORDER BY revenue DESC
        """))
        return [dict(row) for row in result.mappings()]


def get_customer_stats():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_customers,
                AVG(total_orders) as avg_orders,
                AVG(total_spent) as avg_spent,
                MAX(total_spent) as top_spent
            FROM dim_customers
        """))
        return dict(result.mappings().first())


def get_repeat_customers():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT customer_name, customer_email, total_orders, total_spent
            FROM dim_customers
            WHERE total_orders > 1
            ORDER BY total_orders DESC
        """))
        return [dict(row) for row in result.mappings()]


def get_recent_sales(limit=10):
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT f.order_id, p.name, f.quantity, f.revenue, d.full_date
            FROM fact_sales f
            JOIN dim_products p ON f.product_id = p.product_id
            JOIN dim_date d ON f.date_key = d.date_key
            ORDER BY f.sale_id DESC
            LIMIT :limit
        """), {"limit": limit})
        return [dict(row) for row in result.mappings()]
