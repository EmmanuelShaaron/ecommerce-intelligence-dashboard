"""
Ecommerce Intelligence Dashboard
=================================
Single-file Streamlit analytics dashboard.
Data source: data/global_ecommerce_sales.csv (2,001 orders, Jan 2023 – Dec 2025)

Run:
    streamlit run ecommerce_intelligence_dashboard.py
"""

import pathlib

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CSV_PATH = pathlib.Path(__file__).parent / "data" / "global_ecommerce_sales.csv"

PAGE_NAMES = [
    "📊 Executive Overview",
    "📈 Sales & Trend Analysis",
    "🛒 Product & Category Intelligence",
    "👥 Customer & Segment Analysis",
    "🌍 Geographic Intelligence",
    "⚠️ Risk & Opportunity",
    "💡 Management Recommendations",
]

PLOTLY_TEMPLATE = "plotly_white"

# ---------------------------------------------------------------------------
# Sub-Task 1 — Data Layer
# ---------------------------------------------------------------------------


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and prepare the CSV. Called once; result is cached by Streamlit."""
    df = pd.read_csv(CSV_PATH, parse_dates=["Order_Date"])

    # --- Validate expected columns ---
    required_cols = {
        "Order_ID", "Order_Date", "Customer_Name", "Customer_Segment",
        "Country", "Region", "Product_Category", "Product_Name",
        "Quantity", "Unit_Price", "Discount_Percent", "Total_Sales",
        "Shipping_Cost", "Profit", "Payment_Method",
    }
    missing = required_cols - set(df.columns)
    if missing:
        st.error(f"Dataset is missing expected columns: {missing}")
        st.stop()

    # --- Derived columns for grouping ---
    df["Year"] = df["Order_Date"].dt.year
    df["Month"] = df["Order_Date"].dt.month
    df["Quarter"] = df["Order_Date"].dt.quarter
    # YearMonth as Period string for readable axis labels
    df["YearMonth"] = df["Order_Date"].dt.to_period("M").astype(str)

    # --- Derived metric: Profit Margin % ---
    # Guard division by zero: where Total_Sales == 0, result is NaN
    df["Profit_Margin_%"] = np.where(
        df["Total_Sales"] != 0,
        (df["Profit"] / df["Total_Sales"]) * 100,
        np.nan,
    )

    return df


def filter_data(df: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame:
    """Return rows whose Order_Date falls within [start_date, end_date]."""
    mask = (df["Order_Date"] >= start_date) & (df["Order_Date"] <= end_date)
    return df.loc[mask].copy()


def is_empty(df: pd.DataFrame) -> bool:
    """Return True if the DataFrame has no rows."""
    return df.empty


def safe_pct(numerator: float, denominator: float) -> float:
    """Return numerator/denominator * 100, or 0.0 if denominator is zero."""
    return (numerator / denominator * 100) if denominator != 0 else 0.0


def fmt_currency(value: float) -> str:
    """Format a float as a dollar currency string with commas."""
    return f"${value:,.2f}"


def fmt_pct(value: float) -> str:
    """Format a float as a percentage string."""
    return f"{value:.2f}%"


# ---------------------------------------------------------------------------
# Sub-Task 3 — Page 1: Executive Overview
# ---------------------------------------------------------------------------


def page_executive_overview(df: pd.DataFrame) -> None:
    st.header("📊 Executive Overview")
    st.markdown("High-level KPIs and top-line revenue breakdowns for the selected period.")

    if is_empty(df):
        st.warning("No data available for the selected date range. Please adjust the filters.")
        return

    # --- KPI calculations ---
    total_revenue = df["Total_Sales"].sum()
    total_profit = df["Profit"].sum()
    profit_margin = safe_pct(total_profit, total_revenue)
    total_orders = len(df)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0

    # --- KPI Cards ---
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Revenue", fmt_currency(total_revenue))
    c2.metric("Total Profit", fmt_currency(total_profit))
    c3.metric("Profit Margin %", fmt_pct(profit_margin))
    c4.metric("Total Orders", f"{total_orders:,}")
    c5.metric("Avg Order Value", fmt_currency(avg_order_value))

    st.divider()

    # --- Revenue by Year ---
    st.subheader("Revenue by Year")
    rev_year = (
        df.groupby("Year", as_index=False)["Total_Sales"]
        .sum()
        .rename(columns={"Total_Sales": "Revenue"})
    )
    fig_year = px.bar(
        rev_year, x="Year", y="Revenue",
        text_auto=".2s",
        labels={"Revenue": "Revenue ($)", "Year": "Year"},
        template=PLOTLY_TEMPLATE,
        color="Year",
        color_continuous_scale="Blues",
    )
    fig_year.update_traces(textposition="outside")
    fig_year.update_layout(showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig_year, use_container_width=True)

    col_left, col_right = st.columns(2)

    # --- Revenue by Category ---
    with col_left:
        st.subheader("Revenue by Category")
        rev_cat = (
            df.groupby("Product_Category", as_index=False)["Total_Sales"]
            .sum()
            .rename(columns={"Total_Sales": "Revenue"})
            .sort_values("Revenue", ascending=False)
        )
        fig_cat = px.bar(
            rev_cat, x="Product_Category", y="Revenue",
            text_auto=".2s",
            labels={"Revenue": "Revenue ($)", "Product_Category": "Category"},
            template=PLOTLY_TEMPLATE,
            color="Product_Category",
        )
        fig_cat.update_traces(textposition="outside")
        fig_cat.update_layout(showlegend=False)
        st.plotly_chart(fig_cat, use_container_width=True)

    # --- Revenue by Region ---
    with col_right:
        st.subheader("Revenue by Region")
        rev_region = (
            df.groupby("Region", as_index=False)["Total_Sales"]
            .sum()
            .rename(columns={"Total_Sales": "Revenue"})
            .sort_values("Revenue", ascending=False)
        )
        fig_region = px.bar(
            rev_region, x="Region", y="Revenue",
            text_auto=".2s",
            labels={"Revenue": "Revenue ($)", "Region": "Region"},
            template=PLOTLY_TEMPLATE,
            color="Region",
        )
        fig_region.update_traces(textposition="outside")
        fig_region.update_layout(showlegend=False)
        st.plotly_chart(fig_region, use_container_width=True)

    # --- Top 10 Products by Revenue ---
    st.subheader("Top 10 Products by Revenue")
    top_products = (
        df.groupby("Product_Name", as_index=False)["Total_Sales"]
        .sum()
        .rename(columns={"Total_Sales": "Revenue"})
        .sort_values("Revenue", ascending=False)
        .head(10)
    )
    fig_top = px.bar(
        top_products, x="Revenue", y="Product_Name",
        orientation="h",
        text_auto=".2s",
        labels={"Revenue": "Revenue ($)", "Product_Name": "Product"},
        template=PLOTLY_TEMPLATE,
        color="Revenue",
        color_continuous_scale="Blues",
    )
    fig_top.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
    st.plotly_chart(fig_top, use_container_width=True)


# ---------------------------------------------------------------------------
# Sub-Task 4 — Page 2: Sales & Trend Analysis
# ---------------------------------------------------------------------------


def page_sales_trends(df: pd.DataFrame) -> None:
    st.header("📈 Sales & Trend Analysis")
    st.markdown("Monthly trends, year-over-year comparisons, quarterly breakdowns, and seasonal patterns.")

    if is_empty(df):
        st.warning("No data available for the selected date range. Please adjust the filters.")
        return

    # --- Monthly Revenue & Profit trends ---
    monthly = (
        df.groupby("YearMonth", as_index=False)
        .agg(Revenue=("Total_Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order_ID", "count"))
        .sort_values("YearMonth")
    )

    st.subheader("Monthly Revenue Trend")
    fig_rev = px.line(
        monthly, x="YearMonth", y="Revenue",
        markers=True,
        labels={"Revenue": "Revenue ($)", "YearMonth": "Month"},
        template=PLOTLY_TEMPLATE,
    )
    fig_rev.update_xaxes(tickangle=45)
    st.plotly_chart(fig_rev, use_container_width=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Monthly Profit Trend")
        fig_profit = px.line(
            monthly, x="YearMonth", y="Profit",
            markers=True,
            labels={"Profit": "Profit ($)", "YearMonth": "Month"},
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=["#EF553B"],
        )
        fig_profit.update_xaxes(tickangle=45)
        st.plotly_chart(fig_profit, use_container_width=True)

    with col_right:
        st.subheader("Monthly Order Count Trend")
        fig_orders = px.bar(
            monthly, x="YearMonth", y="Orders",
            labels={"Orders": "Number of Orders", "YearMonth": "Month"},
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=["#00CC96"],
        )
        fig_orders.update_xaxes(tickangle=45)
        st.plotly_chart(fig_orders, use_container_width=True)

    st.divider()

    # --- Year-over-Year monthly revenue comparison (separate lines per year) ---
    st.subheader("Year-over-Year Monthly Revenue Comparison")
    yoy = (
        df.groupby(["Year", "Month"], as_index=False)["Total_Sales"]
        .sum()
        .rename(columns={"Total_Sales": "Revenue"})
    )
    # Map month numbers to abbreviated names for readability
    month_names = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
                   7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
    yoy["Month_Name"] = yoy["Month"].map(month_names)
    yoy["Year"] = yoy["Year"].astype(str)
    fig_yoy = px.line(
        yoy, x="Month", y="Revenue",
        color="Year",
        markers=True,
        labels={"Revenue": "Revenue ($)", "Month": "Month"},
        template=PLOTLY_TEMPLATE,
    )
    fig_yoy.update_xaxes(
        tickmode="array",
        tickvals=list(month_names.keys()),
        ticktext=list(month_names.values()),
    )
    st.plotly_chart(fig_yoy, use_container_width=True)

    st.divider()

    # --- Quarterly Revenue by Category ---
    st.subheader("Quarterly Revenue by Category")
    quarterly = (
        df.groupby(["Year", "Quarter", "Product_Category"], as_index=False)["Total_Sales"]
        .sum()
        .rename(columns={"Total_Sales": "Revenue"})
    )
    quarterly["Quarter_Label"] = "Q" + quarterly["Quarter"].astype(str) + " " + quarterly["Year"].astype(str)
    fig_q = px.bar(
        quarterly, x="Quarter_Label", y="Revenue",
        color="Product_Category",
        barmode="group",
        labels={"Revenue": "Revenue ($)", "Quarter_Label": "Quarter", "Product_Category": "Category"},
        template=PLOTLY_TEMPLATE,
    )
    fig_q.update_xaxes(tickangle=45)
    st.plotly_chart(fig_q, use_container_width=True)

    st.divider()

    # --- Seasonal Monthly Analysis (average revenue per calendar month across all years) ---
    st.subheader("Seasonal Monthly Revenue Profile")
    seasonal = (
        df.groupby("Month", as_index=False)["Total_Sales"]
        .mean()
        .rename(columns={"Total_Sales": "Avg_Revenue"})
    )
    seasonal["Month_Name"] = seasonal["Month"].map(month_names)
    fig_season = px.bar(
        seasonal, x="Month_Name", y="Avg_Revenue",
        labels={"Avg_Revenue": "Avg Revenue ($)", "Month_Name": "Month"},
        template=PLOTLY_TEMPLATE,
        color="Avg_Revenue",
        color_continuous_scale="Blues",
    )
    fig_season.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_season, use_container_width=True)


# ---------------------------------------------------------------------------
# Sub-Task 5 — Page 3: Product & Category Intelligence
# ---------------------------------------------------------------------------


def page_product_intelligence(df: pd.DataFrame) -> None:
    st.header("🛒 Product & Category Intelligence")
    st.markdown("Category and product-level revenue, profit, discounting behaviour, and shipping cost analysis.")

    if is_empty(df):
        st.warning("No data available for the selected date range. Please adjust the filters.")
        return

    # --- Revenue and Profit by Category ---
    st.subheader("Revenue and Profit by Category")
    cat_summary = (
        df.groupby("Product_Category", as_index=False)
        .agg(Revenue=("Total_Sales", "sum"), Profit=("Profit", "sum"))
        .sort_values("Revenue", ascending=False)
    )
    fig_cat = go.Figure()
    fig_cat.add_trace(go.Bar(name="Revenue", x=cat_summary["Product_Category"], y=cat_summary["Revenue"]))
    fig_cat.add_trace(go.Bar(name="Profit", x=cat_summary["Product_Category"], y=cat_summary["Profit"]))
    fig_cat.update_layout(
        barmode="group",
        xaxis_title="Category",
        yaxis_title="Amount ($)",
        template=PLOTLY_TEMPLATE,
    )
    st.plotly_chart(fig_cat, use_container_width=True)

    col_left, col_right = st.columns(2)

    # --- Top 10 Products by Revenue ---
    with col_left:
        st.subheader("Top 10 Products by Revenue")
        top_rev = (
            df.groupby("Product_Name", as_index=False)["Total_Sales"]
            .sum()
            .rename(columns={"Total_Sales": "Revenue"})
            .sort_values("Revenue", ascending=False)
            .head(10)
        )
        fig_tr = px.bar(
            top_rev, x="Revenue", y="Product_Name",
            orientation="h", text_auto=".2s",
            labels={"Revenue": "Revenue ($)", "Product_Name": "Product"},
            template=PLOTLY_TEMPLATE,
            color="Revenue",
            color_continuous_scale="Blues",
        )
        fig_tr.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        st.plotly_chart(fig_tr, use_container_width=True)

    # --- Top 10 Products by Profit ---
    with col_right:
        st.subheader("Top 10 Products by Profit")
        top_profit = (
            df.groupby("Product_Name", as_index=False)["Profit"]
            .sum()
            .sort_values("Profit", ascending=False)
            .head(10)
        )
        fig_tp = px.bar(
            top_profit, x="Profit", y="Product_Name",
            orientation="h", text_auto=".2s",
            labels={"Profit": "Profit ($)", "Product_Name": "Product"},
            template=PLOTLY_TEMPLATE,
            color="Profit",
            color_continuous_scale="Greens",
        )
        fig_tp.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        st.plotly_chart(fig_tp, use_container_width=True)

    st.divider()

    # --- Discount vs Profit Margin scatter ---
    st.subheader("Discount % vs Profit Margin % (by Order)")
    # Drop rows where Profit_Margin_% is NaN (Total_Sales == 0 edge case)
    scatter_df = df.dropna(subset=["Profit_Margin_%"])
    fig_scatter = px.scatter(
        scatter_df,
        x="Discount_Percent",
        y="Profit_Margin_%",
        color="Product_Category",
        opacity=0.6,
        hover_data=["Product_Name", "Total_Sales", "Profit"],
        labels={
            "Discount_Percent": "Discount (%)",
            "Profit_Margin_%": "Profit Margin (%)",
            "Product_Category": "Category",
        },
        template=PLOTLY_TEMPLATE,
    )
    # Add zero-margin reference line
    fig_scatter.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Break-even")
    st.plotly_chart(fig_scatter, use_container_width=True)

    col_left2, col_right2 = st.columns(2)

    # --- Average Discount by Category ---
    with col_left2:
        st.subheader("Average Discount % by Category")
        avg_disc = (
            df.groupby("Product_Category", as_index=False)["Discount_Percent"]
            .mean()
            .rename(columns={"Discount_Percent": "Avg_Discount"})
            .sort_values("Avg_Discount", ascending=False)
        )
        fig_disc = px.bar(
            avg_disc, x="Product_Category", y="Avg_Discount",
            text_auto=".1f",
            labels={"Avg_Discount": "Avg Discount (%)", "Product_Category": "Category"},
            template=PLOTLY_TEMPLATE,
            color="Product_Category",
        )
        fig_disc.update_traces(textposition="outside")
        fig_disc.update_layout(showlegend=False)
        st.plotly_chart(fig_disc, use_container_width=True)

    # --- Shipping Cost Ratio by Category ---
    with col_right2:
        st.subheader("Shipping Cost as % of Revenue by Category")
        ship_cat = df.groupby("Product_Category", as_index=False).agg(
            Revenue=("Total_Sales", "sum"),
            Ship_Cost=("Shipping_Cost", "sum"),
        )
        ship_cat["Ship_Ratio_%"] = np.where(
            ship_cat["Revenue"] != 0,
            ship_cat["Ship_Cost"] / ship_cat["Revenue"] * 100,
            np.nan,
        )
        fig_ship = px.bar(
            ship_cat, x="Product_Category", y="Ship_Ratio_%",
            text_auto=".1f",
            labels={"Ship_Ratio_%": "Shipping / Revenue (%)", "Product_Category": "Category"},
            template=PLOTLY_TEMPLATE,
            color="Product_Category",
        )
        fig_ship.update_traces(textposition="outside")
        fig_ship.update_layout(showlegend=False)
        st.plotly_chart(fig_ship, use_container_width=True)


# ---------------------------------------------------------------------------
# Sub-Task 6 — Page 4: Customer & Segment Analysis
# ---------------------------------------------------------------------------


def page_customer_analysis(df: pd.DataFrame) -> None:
    st.header("👥 Customer & Segment Analysis")
    st.markdown("Revenue and profitability by customer segment, payment behaviour, and top customers.")

    if is_empty(df):
        st.warning("No data available for the selected date range. Please adjust the filters.")
        return

    # --- Segment KPIs ---
    st.subheader("Revenue, Profit and Average Order Value by Segment")
    seg = df.groupby("Customer_Segment", as_index=False).agg(
        Revenue=("Total_Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order_ID", "count"),
    )
    seg["AOV"] = np.where(seg["Orders"] != 0, seg["Revenue"] / seg["Orders"], 0.0)

    col_left, col_mid, col_right = st.columns(3)

    with col_left:
        fig_rev_seg = px.bar(
            seg, x="Customer_Segment", y="Revenue",
            text_auto=".2s",
            labels={"Revenue": "Revenue ($)", "Customer_Segment": "Segment"},
            template=PLOTLY_TEMPLATE,
            color="Customer_Segment",
            title="Revenue by Segment",
        )
        fig_rev_seg.update_traces(textposition="outside")
        fig_rev_seg.update_layout(showlegend=False)
        st.plotly_chart(fig_rev_seg, use_container_width=True)

    with col_mid:
        fig_profit_seg = px.bar(
            seg, x="Customer_Segment", y="Profit",
            text_auto=".2s",
            labels={"Profit": "Profit ($)", "Customer_Segment": "Segment"},
            template=PLOTLY_TEMPLATE,
            color="Customer_Segment",
            title="Profit by Segment",
        )
        fig_profit_seg.update_traces(textposition="outside")
        fig_profit_seg.update_layout(showlegend=False)
        st.plotly_chart(fig_profit_seg, use_container_width=True)

    with col_right:
        fig_aov_seg = px.bar(
            seg, x="Customer_Segment", y="AOV",
            text_auto=".2s",
            labels={"AOV": "Avg Order Value ($)", "Customer_Segment": "Segment"},
            template=PLOTLY_TEMPLATE,
            color="Customer_Segment",
            title="Avg Order Value by Segment",
        )
        fig_aov_seg.update_traces(textposition="outside")
        fig_aov_seg.update_layout(showlegend=False)
        st.plotly_chart(fig_aov_seg, use_container_width=True)

    st.divider()

    col_left2, col_right2 = st.columns(2)

    # --- Payment Method Distribution ---
    with col_left2:
        st.subheader("Payment Method Distribution")
        pay = (
            df.groupby("Payment_Method", as_index=False)["Order_ID"]
            .count()
            .rename(columns={"Order_ID": "Orders"})
        )
        fig_pay = px.pie(
            pay, names="Payment_Method", values="Orders",
            hole=0.4,
            template=PLOTLY_TEMPLATE,
        )
        fig_pay.update_traces(textinfo="percent+label")
        st.plotly_chart(fig_pay, use_container_width=True)

    # --- Top 10 Customers by Revenue ---
    with col_right2:
        st.subheader("Top 10 Customers by Revenue")
        top_cust = (
            df.groupby("Customer_Name", as_index=False)["Total_Sales"]
            .sum()
            .rename(columns={"Total_Sales": "Revenue"})
            .sort_values("Revenue", ascending=False)
            .head(10)
        )
        fig_tc = px.bar(
            top_cust, x="Revenue", y="Customer_Name",
            orientation="h", text_auto=".2s",
            labels={"Revenue": "Revenue ($)", "Customer_Name": "Customer"},
            template=PLOTLY_TEMPLATE,
            color="Revenue",
            color_continuous_scale="Blues",
        )
        fig_tc.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        st.plotly_chart(fig_tc, use_container_width=True)

    st.divider()

    # --- Customer Order Frequency ---
    st.subheader("Customer Order Frequency")
    order_freq = (
        df.groupby("Customer_Name", as_index=False)["Order_ID"]
        .count()
        .rename(columns={"Order_ID": "Order_Count"})
    )
    # value_counts() on a Series returns a Series; reset_index() gives two columns.
    # In pandas >= 1.1 the columns are [series_name, "count"]; force explicit names.
    freq_dist = order_freq["Order_Count"].value_counts().reset_index()
    freq_dist.columns = ["Orders_Per_Customer", "Customer_Count"]
    freq_dist = freq_dist.sort_values("Orders_Per_Customer")
    fig_freq = px.bar(
        freq_dist, x="Orders_Per_Customer", y="Customer_Count",
        labels={"Orders_Per_Customer": "Number of Orders Placed", "Customer_Count": "Number of Customers"},
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=["#636EFA"],
    )
    fig_freq.update_xaxes(tickmode="linear")
    st.plotly_chart(fig_freq, use_container_width=True)


# ---------------------------------------------------------------------------
# Sub-Task 7 — Page 5: Geographic Intelligence
# ---------------------------------------------------------------------------


def page_geographic_intelligence(df: pd.DataFrame) -> None:
    st.header("🌍 Geographic Intelligence")
    st.markdown("Revenue and profitability distribution by country and region.")

    if is_empty(df):
        st.warning("No data available for the selected date range. Please adjust the filters.")
        return

    # --- Revenue by Country (top 20, horizontal bar — offline safe) ---
    st.subheader("Top 20 Countries by Revenue")
    rev_country = (
        df.groupby("Country", as_index=False)["Total_Sales"]
        .sum()
        .rename(columns={"Total_Sales": "Revenue"})
        .sort_values("Revenue", ascending=False)
        .head(20)
    )
    fig_country = px.bar(
        rev_country, x="Revenue", y="Country",
        orientation="h", text_auto=".2s",
        labels={"Revenue": "Revenue ($)", "Country": "Country"},
        template=PLOTLY_TEMPLATE,
        color="Revenue",
        color_continuous_scale="Blues",
    )
    fig_country.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
    st.plotly_chart(fig_country, use_container_width=True)

    st.divider()

    col_left, col_right = st.columns(2)

    # --- Revenue and Profit by Region ---
    with col_left:
        st.subheader("Revenue and Profit by Region")
        reg = df.groupby("Region", as_index=False).agg(
            Revenue=("Total_Sales", "sum"),
            Profit=("Profit", "sum"),
        ).sort_values("Revenue", ascending=False)
        fig_reg = go.Figure()
        fig_reg.add_trace(go.Bar(name="Revenue", x=reg["Region"], y=reg["Revenue"]))
        fig_reg.add_trace(go.Bar(name="Profit", x=reg["Region"], y=reg["Profit"]))
        fig_reg.update_layout(
            barmode="group",
            xaxis_title="Region",
            yaxis_title="Amount ($)",
            template=PLOTLY_TEMPLATE,
        )
        st.plotly_chart(fig_reg, use_container_width=True)

    # --- Profit Margin % by Region ---
    with col_right:
        st.subheader("Profit Margin % by Region")
        reg_margin = df.groupby("Region", as_index=False).agg(
            Revenue=("Total_Sales", "sum"),
            Profit=("Profit", "sum"),
        )
        reg_margin["Margin_%"] = np.where(
            reg_margin["Revenue"] != 0,
            reg_margin["Profit"] / reg_margin["Revenue"] * 100,
            np.nan,
        )
        fig_margin = px.bar(
            reg_margin.sort_values("Margin_%", ascending=False),
            x="Region", y="Margin_%",
            text_auto=".1f",
            labels={"Margin_%": "Profit Margin (%)", "Region": "Region"},
            template=PLOTLY_TEMPLATE,
            color="Margin_%",
            color_continuous_scale="RdYlGn",
        )
        fig_margin.update_traces(textposition="outside")
        fig_margin.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_margin, use_container_width=True)

    st.divider()

    # --- Country-level KPI Table ---
    st.subheader("Country-Level KPI Table")
    country_kpi = df.groupby("Country", as_index=False).agg(
        Revenue=("Total_Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order_ID", "count"),
    )
    country_kpi["Margin_%"] = np.where(
        country_kpi["Revenue"] != 0,
        country_kpi["Profit"] / country_kpi["Revenue"] * 100,
        np.nan,
    )
    country_kpi = country_kpi.sort_values("Revenue", ascending=False)
    country_kpi["Revenue"] = country_kpi["Revenue"].round(2)
    country_kpi["Profit"] = country_kpi["Profit"].round(2)
    country_kpi["Margin_%"] = country_kpi["Margin_%"].round(2)
    st.dataframe(
        country_kpi.rename(columns={
            "Revenue": "Revenue ($)",
            "Profit": "Profit ($)",
            "Margin_%": "Margin (%)",
        }),
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------------------------
# Sub-Task 8 — Page 6: Risk & Opportunity
# ---------------------------------------------------------------------------


def page_risk_opportunity(df: pd.DataFrame) -> None:
    st.header("⚠️ Risk & Opportunity")
    st.markdown("Loss-making orders, high-discount risk, shipping cost drains, and high-margin opportunities.")

    if is_empty(df):
        st.warning("No data available for the selected date range. Please adjust the filters.")
        return

    # --- Loss-making order KPIs ---
    loss_df = df[df["Profit"] < 0]
    loss_count = len(loss_df)
    total_orders = len(df)
    loss_pct = safe_pct(loss_count, total_orders)

    st.subheader("Loss-Making Orders")
    c1, c2, c3 = st.columns(3)
    c1.metric("Loss-Making Orders", f"{loss_count:,}")
    c2.metric("% of All Orders", fmt_pct(loss_pct))
    c3.metric("Total Loss Amount", fmt_currency(loss_df["Profit"].sum()))

    st.divider()

    col_left, col_right = st.columns(2)

    # --- Products with negative average profit ---
    with col_left:
        st.subheader("Products with Negative Average Profit")
        neg_prod = (
            df.groupby("Product_Name", as_index=False)["Profit"]
            .mean()
            .rename(columns={"Profit": "Avg_Profit"})
        )
        neg_prod = neg_prod[neg_prod["Avg_Profit"] < 0].sort_values("Avg_Profit")
        if neg_prod.empty:
            st.info("No products have a negative average profit in this period.")
        else:
            neg_prod["Avg_Profit"] = neg_prod["Avg_Profit"].round(2)
            st.dataframe(
                neg_prod.rename(columns={"Avg_Profit": "Avg Profit ($)"}),
                use_container_width=True,
                hide_index=True,
            )

    # --- High-discount loss-making orders ---
    with col_right:
        st.subheader("High-Discount (≥ 20%) Loss-Making Orders")
        high_disc_loss = df[(df["Discount_Percent"] >= 20) & (df["Profit"] < 0)]
        if high_disc_loss.empty:
            st.info("No high-discount loss-making orders in this period.")
        else:
            summary = (
                high_disc_loss.groupby("Product_Name", as_index=False)
                .agg(
                    Orders=("Order_ID", "count"),
                    Total_Loss=("Profit", "sum"),
                    Avg_Discount=("Discount_Percent", "mean"),
                )
                .sort_values("Total_Loss")
            )
            summary["Total_Loss"] = summary["Total_Loss"].round(2)
            summary["Avg_Discount"] = summary["Avg_Discount"].round(1)
            st.dataframe(
                summary.rename(columns={
                    "Total_Loss": "Total Loss ($)",
                    "Avg_Discount": "Avg Discount (%)",
                }),
                use_container_width=True,
                hide_index=True,
            )

    st.divider()

    col_left2, col_right2 = st.columns(2)

    # --- High-margin opportunity products (top 10 by avg profit margin %) ---
    with col_left2:
        st.subheader("Top 10 High-Margin Products (Opportunity)")
        high_margin = (
            df.dropna(subset=["Profit_Margin_%"])
            .groupby("Product_Name", as_index=False)["Profit_Margin_%"]
            .mean()
            .rename(columns={"Profit_Margin_%": "Avg_Margin_%"})
            .sort_values("Avg_Margin_%", ascending=False)
            .head(10)
        )
        if high_margin.empty:
            st.info("No margin data available.")
        else:
            fig_hm = px.bar(
                high_margin, x="Avg_Margin_%", y="Product_Name",
                orientation="h", text_auto=".1f",
                labels={"Avg_Margin_%": "Avg Profit Margin (%)", "Product_Name": "Product"},
                template=PLOTLY_TEMPLATE,
                color="Avg_Margin_%",
                color_continuous_scale="Greens",
            )
            fig_hm.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
            st.plotly_chart(fig_hm, use_container_width=True)

    # --- Shipping cost drain by category ---
    with col_right2:
        st.subheader("Shipping Cost Drain by Category (Total)")
        ship_drain = (
            df.groupby("Product_Category", as_index=False)["Shipping_Cost"]
            .sum()
            .rename(columns={"Shipping_Cost": "Total_Shipping_Cost"})
            .sort_values("Total_Shipping_Cost", ascending=False)
        )
        fig_drain = px.bar(
            ship_drain, x="Product_Category", y="Total_Shipping_Cost",
            text_auto=".2s",
            labels={
                "Total_Shipping_Cost": "Total Shipping Cost ($)",
                "Product_Category": "Category",
            },
            template=PLOTLY_TEMPLATE,
            color="Product_Category",
        )
        fig_drain.update_traces(textposition="outside")
        fig_drain.update_layout(showlegend=False)
        st.plotly_chart(fig_drain, use_container_width=True)


# ---------------------------------------------------------------------------
# Sub-Task 9 — Page 7: Management Recommendations
# ---------------------------------------------------------------------------


def page_recommendations(df: pd.DataFrame) -> None:
    st.header("💡 Management Recommendations")
    st.markdown("Data-driven findings and recommended actions derived from the selected period.")

    if is_empty(df):
        st.warning("No data available. Please select a wider date range to generate recommendations.")
        return

    # --- Compute all supporting statistics ---
    total_revenue = df["Total_Sales"].sum()
    total_profit = df["Profit"].sum()
    overall_margin = safe_pct(total_profit, total_revenue)
    total_orders = len(df)

    # Loss-making orders
    loss_df = df[df["Profit"] < 0]
    loss_count = len(loss_df)
    loss_pct = safe_pct(loss_count, total_orders)

    # Category margins
    cat_margin = df.groupby("Product_Category").agg(
        Revenue=("Total_Sales", "sum"), Profit=("Profit", "sum")
    )
    cat_margin["Margin_%"] = np.where(
        cat_margin["Revenue"] != 0,
        cat_margin["Profit"] / cat_margin["Revenue"] * 100,
        np.nan,
    )
    best_cat = cat_margin["Margin_%"].idxmax() if not cat_margin["Margin_%"].isna().all() else "N/A"
    worst_cat = cat_margin["Margin_%"].idxmin() if not cat_margin["Margin_%"].isna().all() else "N/A"
    best_cat_margin = cat_margin.loc[best_cat, "Margin_%"] if best_cat != "N/A" else 0.0
    worst_cat_margin = cat_margin.loc[worst_cat, "Margin_%"] if worst_cat != "N/A" else 0.0

    # Highest-discount category
    avg_disc_cat = df.groupby("Product_Category")["Discount_Percent"].mean()
    high_disc_cat = avg_disc_cat.idxmax() if not avg_disc_cat.empty else "N/A"
    high_disc_val = avg_disc_cat.max() if not avg_disc_cat.empty else 0.0

    # Top region by revenue
    reg_rev = df.groupby("Region")["Total_Sales"].sum()
    top_region = reg_rev.idxmax() if not reg_rev.empty else "N/A"
    top_region_rev = reg_rev.max() if not reg_rev.empty else 0.0
    top_region_pct = safe_pct(top_region_rev, total_revenue)

    # Top customer segment
    seg_rev = df.groupby("Customer_Segment")["Total_Sales"].sum()
    top_segment = seg_rev.idxmax() if not seg_rev.empty else "N/A"
    top_segment_pct = safe_pct(seg_rev.max() if not seg_rev.empty else 0, total_revenue)

    # Shipping cost ratio overall
    total_shipping = df["Shipping_Cost"].sum()
    ship_ratio = safe_pct(total_shipping, total_revenue)

    # High-discount loss orders
    high_disc_loss = df[(df["Discount_Percent"] >= 20) & (df["Profit"] < 0)]
    high_disc_loss_count = len(high_disc_loss)

    # ---  Observed Findings ---
    st.subheader("📋 Observed Findings")
    st.markdown("The following findings are computed directly from the data in the selected date range.")

    findings = [
        f"**Overall profitability:** The business achieved a total revenue of "
        f"**{fmt_currency(total_revenue)}** with a net profit of **{fmt_currency(total_profit)}**, "
        f"yielding an overall profit margin of **{fmt_pct(overall_margin)}**.",

        f"**Loss-making orders:** Out of **{total_orders:,}** total orders, "
        f"**{loss_count:,}** ({fmt_pct(loss_pct)}) generated a negative profit. "
        f"These orders represent a structural cost risk to the business.",

        f"**Best-performing category (margin):** **{best_cat}** achieves the highest average "
        f"profit margin at **{fmt_pct(best_cat_margin)}**, indicating strong pricing power.",

        f"**Weakest-performing category (margin):** **{worst_cat}** has the lowest average "
        f"profit margin at **{fmt_pct(worst_cat_margin)}**, which warrants pricing or cost review.",

        f"**Discount risk:** **{high_disc_cat}** carries the highest average discount at "
        f"**{fmt_pct(high_disc_val)}** per order. "
        f"**{high_disc_loss_count:,}** orders with a discount ≥ 20% also generated a loss.",

        f"**Geographic concentration:** **{top_region}** accounts for "
        f"**{fmt_pct(top_region_pct)}** of total revenue ({fmt_currency(top_region_rev)}), "
        f"representing both a strength and a geographic dependency risk.",

        f"**Dominant customer segment:** The **{top_segment}** segment drives "
        f"**{fmt_pct(top_segment_pct)}** of total revenue, making it the primary commercial audience.",

        f"**Shipping cost burden:** Shipping costs represent "
        f"**{fmt_pct(ship_ratio)}** of total revenue ({fmt_currency(total_shipping)}), "
        f"which directly compresses net margins.",
    ]

    for i, finding in enumerate(findings, 1):
        st.markdown(f"{i}. {finding}")

    st.divider()

    # --- Recommended Actions ---
    st.subheader("✅ Recommended Actions")
    st.markdown("Each action is directly tied to the findings above.")

    actions = [
        f"**[Profitability]** Prioritise strategies to maintain or improve the "
        f"{fmt_pct(overall_margin)} margin baseline. Track margin monthly to detect early deterioration.",

        f"**[Loss Orders]** Investigate the **{loss_count:,}** loss-making orders "
        f"({fmt_pct(loss_pct)} of total). Identify common products, segments, or regions and introduce "
        f"floor-price controls or discount caps.",

        f"**[Category Investment]** Increase marketing and inventory investment in **{best_cat}**, "
        f"which delivers {fmt_pct(best_cat_margin)} margins. Expand product lines within this category.",

        f"**[Category Review]** Conduct a cost-structure and pricing review for **{worst_cat}** "
        f"(current margin: {fmt_pct(worst_cat_margin)}). Either re-price, renegotiate supplier costs, "
        f"or reduce discount depth.",

        f"**[Discount Policy]** Introduce a discount approval threshold of ≥ 20% for **{high_disc_cat}** "
        f"where {high_disc_loss_count:,} high-discount orders are already loss-making. "
        f"Test 10–15% as a ceiling for standard promotions.",

        f"**[Geographic Diversification]** Reduce dependency on **{top_region}** "
        f"({fmt_pct(top_region_pct)} of revenue). Develop go-to-market strategies for under-represented regions.",

        f"**[Segment Strategy]** Deepen engagement with the **{top_segment}** segment through loyalty "
        f"programmes and volume contracts. Develop targeted campaigns to grow the smaller segments.",

        f"**[Shipping Optimisation]** At {fmt_pct(ship_ratio)} of revenue, shipping costs are a "
        f"significant margin drain ({fmt_currency(total_shipping)} total). Negotiate bulk carrier rates, "
        f"introduce free-shipping order-value thresholds, or use regional fulfilment centres.",
    ]

    for i, action in enumerate(actions, 1):
        st.markdown(f"{i}. {action}")

    st.caption(
        "Note: All figures above are computed from the filtered dataset. "
        "Recommendations reflect patterns in the data and should be validated against operational context."
    )


# ---------------------------------------------------------------------------
# Sub-Task 2 — Sidebar & Navigation Shell + main()
# ---------------------------------------------------------------------------


def main() -> None:
    st.set_page_config(
        page_title="Ecommerce Intelligence Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # --- Load data ---
    df_full = load_data()

    # --- Sidebar ---
    st.sidebar.title("📊 Dashboard Controls")
    st.sidebar.markdown("---")

    # Date range filter
    min_date = df_full["Order_Date"].min().date()
    max_date = df_full["Order_Date"].max().date()

    st.sidebar.subheader("📅 Date Range Filter")
    start_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

    # Guard: start must not be after end
    if start_date > end_date:
        st.sidebar.error("⚠️ Start Date must be on or before End Date.")
        st.error("Please correct the date range in the sidebar.")
        return

    # Filter data for the selected range
    df = filter_data(df_full, pd.Timestamp(start_date), pd.Timestamp(end_date))

    # Show active row count
    st.sidebar.markdown(f"**Orders in range:** {len(df):,}")
    st.sidebar.markdown("---")

    # Page selector
    st.sidebar.subheader("📂 Navigation")
    selected_page = st.sidebar.radio("Select Page", PAGE_NAMES, label_visibility="collapsed")

    st.sidebar.markdown("---")
    st.sidebar.caption(
        f"Data: global_ecommerce_sales.csv  \n"
        f"Period: {min_date} → {max_date}  \n"
        f"Total Records: {len(df_full):,}"
    )

    # --- Route to selected page ---
    if selected_page == PAGE_NAMES[0]:
        page_executive_overview(df)
    elif selected_page == PAGE_NAMES[1]:
        page_sales_trends(df)
    elif selected_page == PAGE_NAMES[2]:
        page_product_intelligence(df)
    elif selected_page == PAGE_NAMES[3]:
        page_customer_analysis(df)
    elif selected_page == PAGE_NAMES[4]:
        page_geographic_intelligence(df)
    elif selected_page == PAGE_NAMES[5]:
        page_risk_opportunity(df)
    elif selected_page == PAGE_NAMES[6]:
        page_recommendations(df)


if __name__ == "__main__":
    main()
