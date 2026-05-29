"""Kawaii Atelier — Analytics Dashboard (Streamlit)."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from queries import (
    get_total_revenue,
    get_total_orders,
    get_total_products_sold,
    get_total_customers,
    get_sales_by_month,
    get_top_products,
    get_sales_by_product_type,
    get_customer_stats,
    get_repeat_customers,
    get_recent_sales,
)

st.set_page_config(
    page_title="Kawaii Atelier Analytics",
    page_icon="★",
    layout="wide",
)

# ─── HEADER ───
st.markdown("""
    <div style="text-align:center; padding: 1rem 0;">
        <h1 style="font-family: 'Fredoka One', cursive; color: #ff4d8f;">
            KAWAII ATELIER ★ Analytics
        </h1>
        <p style="color: #8b6f4e; font-family: 'DM Mono', monospace; font-size: 0.9rem;">
            Sales · Revenue · Products · Customers
        </p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# ─── KPI CARDS ───
col1, col2, col3, col4 = st.columns(4)

with col1:
    revenue = get_total_revenue()
    st.metric(
        label="💰 Total Revenue",
        value=f"₱{float(revenue):,.2f}" if revenue else "₱0.00",
    )

with col2:
    orders = get_total_orders()
    st.metric(
        label="📦 Total Orders",
        value=f"{orders}",
    )

with col3:
    products = get_total_products_sold()
    st.metric(
        label="🎨 Products Sold",
        value=f"{products}",
    )

with col4:
    customers = get_total_customers()
    st.metric(
        label="👥 Unique Customers",
        value=f"{customers}",
    )

st.divider()

# ─── CHARTS ───
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("📈 Sales Trend (Monthly)")
    sales_data = get_sales_by_month()
    if sales_data:
        df = pd.DataFrame(sales_data)
        df["period"] = df["month_name"] + " " + df["year"].astype(str)
        fig = px.line(
            df, x="period", y="revenue",
            markers=True,
            labels={"revenue": "Revenue (₱)", "period": "Month"},
            color_discrete_sequence=["#ff4d8f"],
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Nunito, sans-serif"),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No sales data yet. Run the ETL pipeline first.")

with right_col:
    st.subheader("🥧 Sales by Product Type")
    type_data = get_sales_by_product_type()
    if type_data:
        df = pd.DataFrame(type_data)
        fig = px.pie(
            df, values="revenue", names="type",
            color_discrete_sequence=["#ff4d8f", "#00c4a7", "#c9a84c", "#b84c2f"],
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Nunito, sans-serif"),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No sales data yet.")

st.divider()

# ─── TOP PRODUCTS ───
st.subheader("🏆 Top Products by Quantity Sold")
top_products = get_top_products(5)
if top_products:
    df = pd.DataFrame(top_products)
    fig = px.bar(
        df, x="name", y="total_qty",
        color="type",
        labels={"name": "Product", "total_qty": "Units Sold", "type": "Category"},
        color_discrete_sequence=["#ff4d8f", "#00c4a7", "#c9a84c", "#b84c2f"],
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Nunito, sans-serif"),
        xaxis_tickangle=-45,
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No product sales data yet.")

st.divider()

# ─── CUSTOMER STATS ───
st.subheader("👥 Customer Statistics")
customer_stats = get_customer_stats()
if customer_stats and customer_stats["total_customers"]:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Customers", f"{customer_stats['total_customers']}")
    with c2:
        avg = customer_stats['avg_orders'] or 0
        st.metric("Avg Orders / Customer", f"{avg:.1f}")
    with c3:
        spent = customer_stats['avg_spent'] or 0
        st.metric("Avg Spend / Customer", f"₱{float(spent):,.2f}")

    repeat = get_repeat_customers()
    if repeat:
        st.markdown("**Repeat Customers:**")
        df = pd.DataFrame(repeat)
        st.dataframe(df, use_container_width=True)
else:
    st.info("No customer data yet.")

st.divider()

# ─── RECENT SALES ───
st.subheader("🛒 Recent Sales")
recent = get_recent_sales(10)
if recent:
    df = pd.DataFrame(recent)
    df["revenue"] = df["revenue"].apply(lambda x: f"₱{float(x):,.2f}")
    st.dataframe(df, use_container_width=True)
else:
    st.info("No recent sales data.")

# ─── FOOTER ───
st.divider()
st.markdown("""
    <div style="text-align:center; color: #8b6f4e; font-size: 0.8rem; padding: 1rem 0;">
        Kawaii Atelier Analytics Dashboard · Powered by Streamlit · Data refreshed via ETL
    </div>
""", unsafe_allow_html=True)
