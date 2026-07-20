import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Supply Chain Analytics Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #2e75b6);
        border-radius: 12px;
        padding: 20px 24px;
        color: white;
        margin-bottom: 8px;
    }
    .metric-label { font-size: 13px; opacity: 0.8; margin-bottom: 4px; }
    .metric-value { font-size: 28px; font-weight: 700; }
    .metric-delta { font-size: 12px; margin-top: 4px; }
    .insight-box {
        background: #1a1a2e;
        border-left: 4px solid #2e75b6;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 6px 0;
        font-size: 14px;
    }
    .section-title {
        font-size: 20px;
        font-weight: 600;
        margin: 24px 0 12px 0;
        color: #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)


# ── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    np.random.seed(42)
    n = 200

    locations     = ["Kolkata", "Mumbai", "Chennai", "Bangalore", "Delhi", "Hyderabad", "Pune"]
    product_types = ["Haircare", "Skincare", "Cosmetics", "Wellness"]
    carriers      = ["MAERSK", "CMA CGM", "OOCL", "MSC", "HAPAG"]
    statuses      = ["Delivered", "In Transit", "Delayed", "Processing"]

    dates = pd.date_range(start="2023-01-01", end="2024-12-31", periods=n)

    df = pd.DataFrame({
        "Date":                 dates,
        "SKU":                  [f"SKU{i}" for i in range(n)],
        "Product type":         np.random.choice(product_types, n, p=[0.35, 0.30, 0.20, 0.15]),
        "Location":             np.random.choice(locations, n, p=[0.22, 0.20, 0.18, 0.16, 0.13, 0.06, 0.05]),
        "Carrier":              np.random.choice(carriers, n),
        "Price":                np.round(np.random.uniform(5, 100, n), 2),
        "Availability":         np.random.randint(10, 100, n),
        "Number of products sold": np.random.randint(10, 900, n),
        "Revenue generated":    np.round(np.random.uniform(1000, 15000, n), 2),
        "Shipping times":       np.random.randint(1, 15, n),
        "Lead time":            np.random.randint(3, 20, n),
        "Defect rates":         np.round(np.random.uniform(0, 0.05, n), 4),
        "Order status":         np.random.choice(statuses, n, p=[0.65, 0.20, 0.10, 0.05]),
        "Manufacturing costs":  np.round(np.random.uniform(500, 8000, n), 2),
    })
    df["Month"]       = df["Date"].dt.to_period("M").astype(str)
    df["Quarter"]     = "Q" + df["Date"].dt.quarter.astype(str) + " " + df["Date"].dt.year.astype(str)
    df["Profit"]      = df["Revenue generated"] - df["Manufacturing costs"]
    df["Profit Margin %"] = np.round((df["Profit"] / df["Revenue generated"]) * 100, 1)
    return df

df = load_data()

# ── SIDEBAR FILTERS ───────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/color/96/box.png", width=60)
st.sidebar.title("📦 Supply Chain Analytics")
st.sidebar.markdown("---")
st.sidebar.subheader("🔧 Filters")

product_filter = st.sidebar.multiselect(
    "Product Type",
    options=df["Product type"].unique(),
    default=df["Product type"].unique()
)

location_filter = st.sidebar.multiselect(
    "Location",
    options=df["Location"].unique(),
    default=df["Location"].unique()
)

carrier_filter = st.sidebar.multiselect(
    "Carrier",
    options=df["Carrier"].unique(),
    default=df["Carrier"].unique()
)

status_filter = st.sidebar.multiselect(
    "Order Status",
    options=df["Order status"].unique(),
    default=df["Order status"].unique()
)

date_min = df["Date"].min().date()
date_max = df["Date"].max().date()
date_range = st.sidebar.date_input(
    "Date Range",
    value=(date_min, date_max),
    min_value=date_min,
    max_value=date_max
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Project by Kavin Padmanaban**")
st.sidebar.markdown("[GitHub](https://github.com/Kavin9699/Kavin-project) | [Live App](https://supply-chain-dashboard-kavin.streamlit.app)")

# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
filtered = df[
    df["Product type"].isin(product_filter) &
    df["Location"].isin(location_filter) &
    df["Carrier"].isin(carrier_filter) &
    df["Order status"].isin(status_filter)
]
if len(date_range) == 2:
    filtered = filtered[
        (filtered["Date"].dt.date >= date_range[0]) &
        (filtered["Date"].dt.date <= date_range[1])
    ]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.title("📦 Supply Chain Analytics Dashboard")
st.markdown(f"Showing **{len(filtered):,}** of **{len(df):,}** records  |  Use sidebar filters to explore")
st.markdown("---")

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executive Overview",
    "🔍 Product & Location Analysis",
    "📈 Trend & Forecast",
    "⚙️ Operational Intelligence"
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — EXECUTIVE OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:

    # KPI CARDS
    total_rev     = filtered["Revenue generated"].sum()
    total_orders  = len(filtered)
    avg_shipping  = filtered["Shipping times"].mean()
    avg_margin    = filtered["Profit Margin %"].mean()
    total_units   = filtered["Number of products sold"].sum()
    delay_rate    = (filtered["Order status"] == "Delayed").mean() * 100

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">💰 Total Revenue</div>
            <div class="metric-value">${total_rev:,.0f}</div>
            <div class="metric-delta">Across {total_orders} orders</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">📦 Units Sold</div>
            <div class="metric-value">{total_units:,}</div>
            <div class="metric-delta">Avg {total_units/max(total_orders,1):.0f} per order</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">🚚 Avg Shipping Time</div>
            <div class="metric-value">{avg_shipping:.1f} days</div>
            <div class="metric-delta">Delay rate: {delay_rate:.1f}%</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">📈 Avg Profit Margin</div>
            <div class="metric-value">{avg_margin:.1f}%</div>
            <div class="metric-delta">Net profit focus</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ROW 2 — Revenue by Product + Order Status Donut
    col1, col2 = st.columns([3, 2])

    with col1:
        rev_prod = filtered.groupby("Product type")["Revenue generated"].sum().reset_index()
        fig = px.bar(
            rev_prod, x="Product type", y="Revenue generated",
            color="Product type",
            color_discrete_sequence=px.colors.qualitative.Bold,
            title="Revenue by Product Type",
            text_auto=".2s"
        )
        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)",
                          paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        status_counts = filtered["Order status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig2 = px.pie(
            status_counts, names="Status", values="Count",
            title="Order Status Breakdown",
            hole=0.55,
            color_discrete_sequence=["#2ecc71", "#3498db", "#e74c3c", "#f39c12"]
        )
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig2, use_container_width=True)

    # AUTOMATED INSIGHTS
    st.markdown('<div class="section-title">🧠 Auto-Generated Insights</div>', unsafe_allow_html=True)

    top_loc    = filtered.groupby("Location")["Revenue generated"].sum().idxmax()
    top_prod   = filtered.groupby("Product type")["Revenue generated"].sum().idxmax()
    top_carr   = filtered.groupby("Carrier")["Revenue generated"].sum().idxmax()
    worst_ship = filtered.groupby("Location")["Shipping times"].mean().idxmax()
    best_margin_prod = filtered.groupby("Product type")["Profit Margin %"].mean().idxmax()
    delayed_pct = delay_rate

    insights = [
        f"📍 <b>{top_loc}</b> is the highest revenue-generating location in the selected period.",
        f"🏆 <b>{top_prod}</b> leads all product types in total revenue generated.",
        f"🚢 <b>{top_carr}</b> is the top-performing carrier by revenue contribution.",
        f"⚠️ <b>{worst_ship}</b> has the longest average shipping time — a potential bottleneck to investigate.",
        f"💹 <b>{best_margin_prod}</b> delivers the strongest average profit margin across product types.",
        f"🔴 Current delay rate is <b>{delayed_pct:.1f}%</b> — {'within acceptable range.' if delayed_pct < 15 else 'above threshold — corrective action recommended.'}",
    ]
    for insight in insights:
        st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PRODUCT & LOCATION ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:

    col1, col2 = st.columns(2)

    with col1:
        # Orders by location — Plotly horizontal bar
        loc_data = filtered.groupby("Location").agg(
            Orders=("SKU", "count"),
            Revenue=("Revenue generated", "sum")
        ).reset_index().sort_values("Revenue", ascending=True)

        fig = px.bar(
            loc_data, y="Location", x="Revenue",
            orientation="h",
            title="Revenue by Location",
            color="Revenue",
            color_continuous_scale="Blues",
            text_auto=".2s"
        )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)",
                          paper_bgcolor="rgba(0,0,0,0)", font_color="white",
                          coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Defect rate by product type
        defect = filtered.groupby("Product type")["Defect rates"].mean().reset_index()
        defect["Defect rates"] = (defect["Defect rates"] * 100).round(2)
        fig2 = px.bar(
            defect, x="Product type", y="Defect rates",
            title="Avg Defect Rate by Product Type (%)",
            color="Defect rates",
            color_continuous_scale="Reds",
            text_auto=True
        )
        fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)",
                           paper_bgcolor="rgba(0,0,0,0)", font_color="white",
                           coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Heatmap — Revenue by Product × Location
    heatmap_data = filtered.pivot_table(
        index="Product type", columns="Location",
        values="Revenue generated", aggfunc="sum", fill_value=0
    )
    fig3 = px.imshow(
        heatmap_data,
        title="Revenue Heatmap — Product Type × Location",
        color_continuous_scale="Blues",
        text_auto=".2s",
        aspect="auto"
    )
    fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig3, use_container_width=True)

    # Scatter — Price vs Revenue coloured by Product
    fig4 = px.scatter(
        filtered, x="Price", y="Revenue generated",
        color="Product type", size="Number of products sold",
        hover_data=["SKU", "Location", "Carrier"],
        title="Price vs Revenue (bubble = units sold)",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig4.update_layout(plot_bgcolor="rgba(0,0,0,0)",
                       paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig4, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — TREND & FORECAST
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:

    st.markdown("### 📈 Monthly Revenue Trend with Moving Average & Forecast")

    monthly = filtered.groupby("Month")["Revenue generated"].sum().reset_index()
    monthly = monthly.sort_values("Month")
    monthly["MA_3"] = monthly["Revenue generated"].rolling(3, min_periods=1).mean()

    # Simple linear forecast for next 3 months
    x = np.arange(len(monthly))
    y = monthly["Revenue generated"].values
    if len(x) > 1:
        coeffs = np.polyfit(x, y, 1)
        future_x = np.arange(len(monthly), len(monthly) + 3)
        future_y = np.polyval(coeffs, future_x)

        # Generate future month labels
        last_period = pd.Period(monthly["Month"].iloc[-1], freq="M")
        future_months = [(last_period + i + 1).strftime("%Y-%m") for i in range(3)]
    else:
        future_months = []
        future_y = []

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly["Month"], y=monthly["Revenue generated"],
        name="Monthly Revenue", marker_color="#2e75b6", opacity=0.7
    ))
    fig.add_trace(go.Scatter(
        x=monthly["Month"], y=monthly["MA_3"],
        mode="lines", name="3-Month Moving Avg",
        line=dict(color="#f39c12", width=2.5)
    ))
    if len(future_months) > 0:
        fig.add_trace(go.Scatter(
            x=future_months, y=future_y,
            mode="lines+markers", name="Forecast (Linear)",
            line=dict(color="#2ecc71", width=2, dash="dash"),
            marker=dict(size=8, symbol="diamond")
        ))

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="white", legend=dict(bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Quarterly comparison
    col1, col2 = st.columns(2)
    with col1:
        qtr = filtered.groupby("Quarter")["Revenue generated"].sum().reset_index()
        fig2 = px.bar(qtr, x="Quarter", y="Revenue generated",
                      title="Quarterly Revenue Comparison",
                      color="Revenue generated",
                      color_continuous_scale="Blues", text_auto=".2s")
        fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)",
                           paper_bgcolor="rgba(0,0,0,0)", font_color="white",
                           coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        # Shipping time trend monthly
        ship_trend = filtered.groupby("Month")["Shipping times"].mean().reset_index()
        ship_trend = ship_trend.sort_values("Month")
        fig3 = px.line(ship_trend, x="Month", y="Shipping times",
                       title="Avg Shipping Time Trend (Monthly)",
                       markers=True,
                       color_discrete_sequence=["#e74c3c"])
        fig3.add_hline(y=ship_trend["Shipping times"].mean(),
                       line_dash="dash", line_color="gray",
                       annotation_text="Overall Avg")
        fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)",
                           paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig3, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — OPERATIONAL INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:

    st.markdown("### ⚙️ Carrier Performance & Operational Metrics")

    col1, col2 = st.columns(2)

    with col1:
        # Carrier performance — grouped bar
        carrier_perf = filtered.groupby("Carrier").agg(
            Avg_Shipping=("Shipping times", "mean"),
            Avg_Defect=("Defect rates", "mean"),
            Total_Revenue=("Revenue generated", "sum")
        ).reset_index()
        carrier_perf["Avg_Defect"] = carrier_perf["Avg_Defect"] * 100

        fig = px.bar(
            carrier_perf, x="Carrier", y="Avg_Shipping",
            title="Avg Shipping Time by Carrier (days)",
            color="Avg_Shipping", color_continuous_scale="RdYlGn_r",
            text_auto=".1f"
        )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)",
                          paper_bgcolor="rgba(0,0,0,0)", font_color="white",
                          coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Lead time vs Shipping time scatter by carrier
        fig2 = px.scatter(
            filtered, x="Lead time", y="Shipping times",
            color="Carrier", size="Revenue generated",
            title="Lead Time vs Shipping Time by Carrier",
            hover_data=["Product type", "Location"],
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)",
                           paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig2, use_container_width=True)

    # Profit margin by product × carrier heatmap
    margin_heat = filtered.pivot_table(
        index="Carrier", columns="Product type",
        values="Profit Margin %", aggfunc="mean"
    ).round(1)
    fig3 = px.imshow(
        margin_heat,
        title="Avg Profit Margin % — Carrier × Product Type",
        color_continuous_scale="RdYlGn",
        text_auto=True, aspect="auto"
    )
    fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig3, use_container_width=True)

    # Inventory availability distribution
    col1, col2 = st.columns(2)
    with col1:
        fig4 = px.box(
            filtered, x="Product type", y="Availability",
            color="Product type",
            title="Stock Availability Distribution by Product",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig4.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)",
                           paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig4, use_container_width=True)

    with col2:
        # Top 10 SKUs by revenue
        top_sku = filtered.nlargest(10, "Revenue generated")[
            ["SKU", "Product type", "Revenue generated", "Profit Margin %", "Location"]
        ].reset_index(drop=True)
        st.markdown("#### 🏅 Top 10 SKUs by Revenue")
        st.dataframe(
            top_sku.style.background_gradient(subset=["Revenue generated"], cmap="Blues")
                         .format({"Revenue generated": "${:,.0f}", "Profit Margin %": "{:.1f}%"}),
            use_container_width=True, height=360
        )

    # Raw data expander
    with st.expander("🗂️ View Filtered Dataset"):
        st.dataframe(filtered.reset_index(drop=True), use_container_width=True)
        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Filtered Data as CSV", csv,
                           "supply_chain_filtered.csv", "text/csv")
