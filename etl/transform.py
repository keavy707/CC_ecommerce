"""Transform raw data into star schema format."""
from datetime import datetime, date, timedelta
from decimal import Decimal


def transform_sales(raw_rows):
    """Convert raw order items into fact_sales rows."""
    facts = []
    for row in raw_rows:
        created_at = row["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

        # Handle both datetime and date objects
        if isinstance(created_at, datetime):
            date_key = int(created_at.strftime("%Y%m%d"))
            created_dt = created_at
        else:
            date_key = int(created_at.strftime("%Y%m%d"))
            created_dt = datetime.combine(created_at, datetime.min.time())

        facts.append({
            "order_id": row["order_id"],
            "product_id": row["product_id"],
            "date_key": date_key,
            "quantity": row["quantity"],
            "revenue": Decimal(str(row["unit_price"])) * row["quantity"],
            "customer_email": row["customer_email"],
            "created_at": created_dt,
        })
    return facts


def transform_products(raw_products):
    """Convert raw products into dim_products rows."""
    dims = []
    for p in raw_products:
        dims.append({
            "product_id": p["id"],
            "code": p["code"],
            "name": p["name"],
            "type": p["type"],
            "price": Decimal(str(p["price"])),
        })
    return dims


def generate_date_range(start_date, end_date):
    """Generate dim_date rows for a date range."""
    import calendar

    # Ensure both are date objects
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()

    dates = []
    current = start_date
    while current <= end_date:
        dates.append({
            "date_key": int(current.strftime("%Y%m%d")),
            "full_date": current,
            "year": current.year,
            "month": current.month,
            "month_name": calendar.month_name[current.month],
            "day": current.day,
            "weekday": calendar.day_name[current.weekday()],
        })
        current += timedelta(days=1)
    return dates


def transform_customers(raw_rows):
    """Aggregate customer stats from orders."""
    customers = {}
    for row in raw_rows:
        email = row["customer_email"]
        created_at = row["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

        if email not in customers:
            customers[email] = {
                "customer_email": email,
                "customer_name": row["customer_name"],
                "total_orders": 0,
                "total_spent": Decimal("0"),
                "first_order": created_at,
                "last_order": created_at,
            }
        customers[email]["total_orders"] += 1
        customers[email]["total_spent"] += Decimal(str(row["total_amount"]))
        if created_at > customers[email]["last_order"]:
            customers[email]["last_order"] = created_at
    return list(customers.values())