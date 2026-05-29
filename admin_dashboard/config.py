"""Admin Dashboard configuration."""
import os
from dotenv import load_dotenv

load_dotenv()

MAIN_DB_URL = os.getenv(
    "MAIN_DATABASE_URL",
    "postgresql://postgres@localhost/ecommerce_main"
)

REPORTING_DB_URL = os.getenv(
    "REPORTING_DATABASE_URL",
    "postgresql://postgres@localhost/ecommerce_reporting"
)