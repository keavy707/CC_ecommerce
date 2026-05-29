"""Kawaii Atelier — Admin Dashboard (Streamlit).
Combines product management + analytics dashboard.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
from config import REPORTING_DB_URL, MAIN_DB_URL

# ─── DATABASE ENGINES ───
main_engine = create_engine(MAIN_DB_URL)
rep_engine = create_engine(REPORTING_DB_URL)

st.set_page_config(
    page_title="Kawaii Atelier Admin",
    page_icon="★",
    layout="wide",
)

# ─── SIDEBAR NAVIGATION ───
st.sidebar.title("KAWAII ATELIER ★")
st.sidebar.markdown("*Admin Panel*")

page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "📦 Products", "🛒 Orders"],
)

# ═══════════════════════════════════════════
# PAGE 1: DASHBOARD (Analytics)
# ═══════════════════════════════════════════
if page == "Dashboard":
    st.markdown("""
        <div style="text-align:center; padding: 1rem 0;">
            <h1 style="font-family: 'Fredoka One', cursive; color: #ff4d8f;">
                KAWAII ATELIER ★ Analytics
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        with rep_engine.connect() as conn:
            result = conn.execute(text("SELECT COALESCE(SUM(revenue), 0) FROM fact_sales"))
            revenue = result.scalar()
        st.metric("Total Revenue", f"₱{float(revenue):,.2f}")
    
    with col2:
        with rep_engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(DISTINCT order_id) FROM fact_sales"))
            orders = result.scalar()
        st.metric("Total Orders", f"{orders}")
    
    with col3:
        with rep_engine.connect() as conn:
            result = conn.execute(text("SELECT COALESCE(SUM(quantity), 0) FROM fact_sales"))
            products = result.scalar()
        st.metric("Products Sold", f"{products}")
    
    with col4:
        with rep_engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(DISTINCT customer_email) FROM fact_sales"))
            customers = result.scalar()
        st.metric("👥 Unique Customers", f"{customers}")
    
    st.divider()
    
    # Charts
    left_col, right_col = st.columns(2)
    
    with left_col:
        st.subheader("Sales Trend (Monthly)")
        with rep_engine.connect() as conn:
            result = conn.execute(text("""
                SELECT d.year, d.month, d.month_name, SUM(f.revenue) as revenue
                FROM fact_sales f
                JOIN dim_date d ON f.date_key = d.date_key
                GROUP BY d.year, d.month, d.month_name
                ORDER BY d.year, d.month
            """))
            sales_data = [dict(row) for row in result.mappings()]
        
        if sales_data:
            df = pd.DataFrame(sales_data)
            df["period"] = df["month_name"] + " " + df["year"].astype(str)
            fig = px.line(df, x="period", y="revenue", markers=True,
                        labels={"revenue": "Revenue (₱)", "period": "Month"},
                        color_discrete_sequence=["#ff4d8f"])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sales data yet.")
    
    with right_col:
        st.subheader("Sales by Product Type")
        with rep_engine.connect() as conn:
            result = conn.execute(text("""
                SELECT p.type, SUM(f.revenue) as revenue
                FROM fact_sales f
                JOIN dim_products p ON f.product_id = p.product_id
                GROUP BY p.type
                ORDER BY revenue DESC
            """))
            type_data = [dict(row) for row in result.mappings()]
        
        if type_data:
            df = pd.DataFrame(type_data)
            fig = px.pie(df, values="revenue", names="type",
                        color_discrete_sequence=["#ff4d8f", "#00c4a7", "#c9a84c", "#b84c2f"])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sales data yet.")
    
    st.divider()
    
    # Top Products
    st.subheader("Top Products")
    with rep_engine.connect() as conn:
        result = conn.execute(text("""
            SELECT p.name, p.type, SUM(f.quantity) as qty, SUM(f.revenue) as revenue
            FROM fact_sales f
            JOIN dim_products p ON f.product_id = p.product_id
            GROUP BY p.product_id, p.name, p.type
            ORDER BY qty DESC
            LIMIT 10
        """))
        top = [dict(row) for row in result.mappings()]
    
    if top:
        df = pd.DataFrame(top)
        fig = px.bar(df, x="name", y="qty", color="type",
                    labels={"name": "Product", "qty": "Units Sold"},
                    color_discrete_sequence=["#ff4d8f", "#00c4a7", "#c9a84c", "#b84c2f"])
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent Sales Table
    st.subheader("🛒 Recent Sales")
    with rep_engine.connect() as conn:
        result = conn.execute(text("""
            SELECT f.order_id, p.name, f.quantity, f.revenue, d.full_date
            FROM fact_sales f
            JOIN dim_products p ON f.product_id = p.product_id
            JOIN dim_date d ON f.date_key = d.date_key
            ORDER BY f.sale_id DESC
            LIMIT 20
        """))
        recent = [dict(row) for row in result.mappings()]
    
    if recent:
        df = pd.DataFrame(recent)
        df["revenue"] = df["revenue"].apply(lambda x: f"₱{float(x):,.2f}")
        st.dataframe(df, use_container_width=True)

# ═══════════════════════════════════════════
# PAGE 2: PRODUCT MANAGEMENT
# ═══════════════════════════════════════════
elif page == "📦 Products":
    st.markdown("""
        <div style="text-align:center; padding: 1rem 0;">
            <h1 style="font-family: 'Fredoka One', cursive; color: #ff4d8f;">
                📦 Product Management
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Load all products
    with main_engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM products ORDER BY id"))
        products = [dict(row) for row in result.mappings()]
    
    # Display products in a table
    if products:
        df = pd.DataFrame(products)
        df["price"] = df["price"].apply(lambda x: f"₱{float(x):,.2f}")
        st.dataframe(df[["id", "code", "name", "type", "price", "stock"]], use_container_width=True)
    
    st.divider()
    
    # Edit Product
    st.subheader("Edit Product")
    product_ids = [p["id"] for p in products]
    selected_id = st.selectbox("Select Product", product_ids)
    
    selected_product = next((p for p in products if p["id"] == selected_id), None)
    
    if selected_product:
        with st.form("edit_product"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name", selected_product["name"])
                price = st.number_input("Price", min_value=0.0, value=float(selected_product["price"]), step=10.0)
                stock = st.number_input("Stock", min_value=0, value=int(selected_product["stock"]), step=1)
            with col2:
                code = st.text_input("Code", selected_product["code"])
                type_ = st.selectbox("Type", ["tshirt", "pin", "sticker", "artcard"], index=["tshirt", "pin", "sticker", "artcard"].index(selected_product["type"]))
                description = st.text_area("Description", selected_product.get("description", ""))
            
            submitted = st.form_submit_button("Save Changes")
            if submitted:
                with main_engine.connect() as conn:
                    conn.execute(text("""
                        UPDATE products 
                        SET name = :name, code = :code, type = :type, price = :price, 
                            stock = :stock, description = :description
                        WHERE id = :id
                    """), {
                        "name": name, "code": code, "type": type_, "price": price,
                        "stock": stock, "description": description, "id": selected_id
                    })
                    conn.commit()
                st.success(f"✅ Updated {name}")
                st.rerun()
    
    st.divider()
    
    # Add New Product
    st.subheader("➕ Add New Product")
    with st.form("add_product"):
        col1, col2 = st.columns(2)
        with col1:
            new_id = st.text_input("Product ID (e.g., ts-005)")
            new_name = st.text_input("Name")
            new_price = st.number_input("Price", min_value=0.0, step=10.0)
            new_stock = st.number_input("Stock", min_value=0, step=1)
        with col2:
            new_code = st.text_input("Code (e.g., MO-009)")
            new_type = st.selectbox("Type", ["tshirt", "pin", "sticker", "artcard"])
            new_emoji = st.text_input("Emoji (e.g., 🌟)", "🌟")
            new_image = st.text_input("Image filename (e.g., ts-new.jpg)")
        
        add_submitted = st.form_submit_button("➕ Add Product")
        if add_submitted:
            with main_engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO products (id, code, name, type, price, stock, emoji, image, description)
                    VALUES (:id, :code, :name, :type, :price, :stock, :emoji, :image, :description)
                """), {
                    "id": new_id, "code": new_code, "name": new_name, "type": new_type,
                    "price": new_price, "stock": new_stock, "emoji": new_emoji,
                    "image": new_image, "description": ""
                })
                conn.commit()
            st.success(f"✅ Added {new_name}")
            st.rerun()

# ═══════════════════════════════════════════
# PAGE 3: ORDERS
# ═══════════════════════════════════════════
elif page == "🛒 Orders":
    st.markdown("""
        <div style="text-align:center; padding: 1rem 0;">
            <h1 style="font-family: 'Fredoka One', cursive; color: #ff4d8f;">
                Order Management
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Load all orders
    with main_engine.connect() as conn:
        result = conn.execute(text("""
            SELECT o.*, COUNT(oi.id) as item_count
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            GROUP BY o.id
            ORDER BY o.created_at DESC
        """))
        orders = [dict(row) for row in result.mappings()]
    
    if orders:
        df = pd.DataFrame(orders)
        df["total_amount"] = df["total_amount"].apply(lambda x: f"₱{float(x):,.2f}")
        df["created_at"] = df["created_at"].astype(str)
        st.dataframe(df[["id", "customer_name", "customer_email", "total_amount", "status", "payment_method", "created_at"]], use_container_width=True)
    
    st.divider()
    
    # Update Order Status
    st.subheader("🔄 Update Order Status")
    order_ids = [str(o["id"]) for o in orders]
    selected_order = st.selectbox("Select Order", order_ids)
    new_status = st.selectbox("New Status", ["pending", "paid", "shipped", "delivered", "cancelled"])
    
    if st.button("Update Status"):
        with main_engine.connect() as conn:
            conn.execute(text("UPDATE orders SET status = :status WHERE id = :id"),
                        {"status": new_status, "id": int(selected_order)})
            conn.commit()
        st.success(f"✅ Order #{selected_order} updated to {new_status}")
        st.rerun()
    
    st.divider()
    
    # Order Details
    st.subheader("Order Details")
    if selected_order:
        with main_engine.connect() as conn:
            # Order info
            result = conn.execute(text("SELECT * FROM orders WHERE id = :id"), {"id": int(selected_order)})
            order = dict(result.mappings().first()) if result.rowcount > 0 else None
            
            # Items
            result = conn.execute(text("""
                SELECT oi.*, p.name, p.type
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = :id
            """), {"id": int(selected_order)})
            items = [dict(row) for row in result.mappings()]
        
        if order:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Customer:** {order['customer_name']}")
                st.write(f"**Email:** {order['customer_email']}")
                st.write(f"**Phone:** {order.get('customer_phone', 'N/A')}")
            with col2:
                st.write(f"**Total:** ₱{float(order['total_amount']):,.2f}")
                st.write(f"**Status:** {order['status']}")
                st.write(f"**Payment:** {order['payment_method']}")
            
            st.write(f"**Address:** {order.get('shipping_address', 'N/A')}")
            
            if items:
                st.write("**Items:**")
                for item in items:
                    st.write(f"- {item['name']} ({item['type']}) × {item['quantity']} @ ₱{float(item['unit_price']):,.2f}")