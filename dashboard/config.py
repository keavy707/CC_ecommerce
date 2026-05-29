"""Dashboard configuration."""
import os
from dotenv import load_dotenv

load_dotenv()

REPORTING_DB_URL = os.getenv(
    "REPORTING_DATABASE_URL",
    "postgresql://ecommerce_user:password@localhost/ecommerce_reporting"
)
