from fastapi import APIRouter
from sqlalchemy import create_engine, text
import os

router = APIRouter(prefix="/api/etl", tags=["etl"])

REPORTING_DB_URL = os.getenv("REPORTING_DATABASE_URL", "postgresql://ecommerce_user:password@localhost/ecommerce_reporting")
rep_engine = create_engine(REPORTING_DB_URL)

@router.get("/status")
def etl_status():
    with rep_engine.connect() as conn:
        # Last ETL run
        result = conn.execute(text("SELECT * FROM etl_log ORDER BY run_id DESC LIMIT 1"))
        last_run = dict(result.mappings().first()) if result.rowcount > 0 else None
        
        # Total sales
        result = conn.execute(text("SELECT COUNT(*) FROM fact_sales"))
        total_sales = result.scalar()
        
        # Total revenue
        result = conn.execute(text("SELECT COALESCE(SUM(revenue), 0) FROM fact_sales"))
        revenue = float(result.scalar())
    
    return {
        "last_etl_run": last_run,
        "total_sales_records": total_sales,
        "total_revenue": revenue,
        "status": "ETL pipeline active"
    }