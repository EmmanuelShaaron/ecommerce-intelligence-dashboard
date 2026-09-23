# Ecommerce Intelligence Dashboard — Implementation Plan

## Top-Level Overview

Build a single-file Streamlit analytics dashboard (`ecommerce_intelligence_dashboard.py`) that reads
`data/global_ecommerce_sales.csv` (2,001 orders, Jan 2023–Dec 2025, 15 columns) and presents seven
themed analysis pages behind a sidebar date-range filter. All metrics are computed at runtime from
the raw data. No numbers are hard-coded. No ML, no external APIs, no internet required.

---

## Dataset Facts (from exploration)

| Fact | Value |
|------|-------|
| Rows (excl. header) | 2,001 |
| Date range | 2023-01-02 → 2025-12-31 |
| Date format | ISO `YYYY-MM-DD` |
| Numeric columns | Quantity, Unit_Price, Discount_Percent, Total_Sales, Shipping_Cost, Profit |
| Categorical columns | Customer_Segment, Country, Region, Product_Category, Payment_Method |
| Text columns | Order_ID, Customer_Name, Product_Name |
| Negative-profit rows | ~272 (~13.6 %) — must be kept |
| Profit_Margin_% | Derived: `(Profit / Total_Sales) * 100` (guard div-by-zero) |

---

## Sub-Task 1 — Project Bootstrap & Data Layer

**Intent:** Create the single application file, declare dependencies, load the CSV, parse dates,
derive computed columns, and expose a filtering function that all pages will call. Getting this
layer right protects every downstream page from bad data.

**Expected Outcomes:**
- File `ecommerce_intelligence_dashboard.py` exists in the project root.
- `load_data()` reads `data/global_ecommerce_sales.csv` relative to the script location.
- `Order_Date` is parsed as `datetime64`.
- `Profit_Margin_%` column added as `(Profit / Total_Sales) * 100` (NaN when Total_Sales == 0).
- `Year`, `Month`, `Quarter`, `YearMonth` helper columns added for grouping.
- `filter_data(df, start_date, end_date)` returns the date-filtered slice.
- All imports declared at the top: `streamlit`, `pandas`, `numpy`, `plotly.express`, `plotly.graph_objects`.
- App runs with `streamlit run ecommerce_intelligence_dashboard.py` from the project folder.

**Todo List:**
1. Create `ecommerce_intelligence_dashboard.py` at project root.
2. Add all imports.
3. Implement `load_data()` with `@st.cache_data`.
4. Add `Order_Date` datetime parse.
5. Derive `Profit_Margin_%`, `Year`, `Month`, `Quarter`, `YearMonth` columns.
6. Implement `filter_data(df, start_date, end_date)` returning filtered DataFrame.
7. Add empty-result guard helper `is_empty(df)`.

**Relevant Context:** CSV at `data/global_ecommerce_sales.csv`; path must be resolved relative to
`__file__` so it works regardless of working directory.

**Status:** [ ] pending

---

## Sub-Task 2 — Sidebar & Navigation Shell

**Intent:** Build the Streamlit shell: page title, sidebar with date-range filter and page selector,
and top-level routing logic that calls each page function. This is done before page content so that
every page immediately receives a filtered DataFrame.

**Expected Outcomes:**
- Sidebar shows a date-range slider/date inputs defaulting to full dataset range.
- Sidebar shows a page selector (radio or selectbox) for the seven pages.
- Filtered DataFrame is computed once and passed to the active page function.
- Sidebar shows the active row count after filtering.
- Empty-filter warning is shown in the main area if zero rows match.

**Todo List:**
1. Add `main()` entry point.
2. Set Streamlit page config (title, layout="wide", icon).
3. Load data, compute min/max dates for sidebar.
4. Add `st.sidebar` date inputs (start_date, end_date).
5. Add page selector to sidebar.
6. Call `filter_data()` and show row count.
7. Route to page functions based on selection (stubs at this point).

**Relevant Context:** Uses `load_data()` and `filter_data()` from Sub-Task 1.

**Status:** [ ] pending

---

## Sub-Task 3 — Page 1: Executive Overview

**Intent:** Give leadership a single-screen KPI snapshot plus four exploratory charts showing
where revenue comes from.

**Expected Outcomes:**
- KPI row: Total Revenue, Total Profit, Profit Margin %, Total Orders, Average Order Value.
- Bar chart: Revenue by Year.
- Bar chart: Revenue by Product_Category.
- Bar chart: Revenue by Region.
- Horizontal bar: Top 10 products by revenue.
- All values computed from filtered DataFrame.

**Todo List:**
1. Implement `page_executive_overview(df)`.
2. Compute five KPIs from `df`.
3. Render KPIs as `st.metric` cards in a 5-column layout.
4. Add Revenue by Year bar chart (Plotly Express).
5. Add Revenue by Category bar chart.
6. Add Revenue by Region bar chart.
7. Add Top 10 Products by Revenue horizontal bar.
8. Add section heading and chart titles.

**Relevant Context:** `Total_Sales` = revenue. `Profit` = profit. KPIs use the filtered slice.

**Status:** [ ] pending

---

## Sub-Task 4 — Page 2: Sales & Trend Analysis

**Intent:** Surface time-based patterns — monthly trends, year-over-year comparison, quarterly
breakdowns, and seasonal monthly profiles — so the user can spot growth and seasonality.

**Expected Outcomes:**
- Line chart: Monthly Revenue trend.
- Line chart: Monthly Profit trend.
- Bar chart: Monthly Order Count trend.
- Multi-line or grouped chart: Year-over-Year monthly revenue comparison.
- Heatmap or grouped bar: Quarterly Revenue by Category.
- Bar chart: Average Monthly Revenue by Month Number (seasonality).

**Todo List:**
1. Implement `page_sales_trends(df)`.
2. Group by `YearMonth` for three monthly trend charts.
3. Group by `Year` + `Month` for YoY comparison (pivot and plot).
4. Group by `Year` + `Quarter` + `Product_Category` for quarterly/category chart.
5. Group by `Month` (across years) for seasonal profile.
6. Add section headings and chart titles.

**Relevant Context:** `YearMonth`, `Year`, `Month`, `Quarter` columns from Sub-Task 1.

**Status:** [ ] pending

---

## Sub-Task 5 — Page 3: Product & Category Intelligence

**Intent:** Enable product-level decisions by showing which categories and SKUs drive revenue and
profit, how discounting correlates with margin, and where shipping costs eat profitability.

**Expected Outcomes:**
- Grouped bar chart: Revenue and Profit by Category.
- Horizontal bar: Top 10 products by Revenue.
- Horizontal bar: Top 10 products by Profit.
- Scatter plot: Discount_Percent vs Profit_Margin_% (coloured by Category).
- Bar chart: Average Discount_Percent by Category.
- Bar chart: Shipping cost as % of Total_Sales by Category.

**Todo List:**
1. Implement `page_product_intelligence(df)`.
2. Group by `Product_Category` for revenue/profit grouped bar.
3. Group by `Product_Name` for top-10 revenue and top-10 profit bars.
4. Build scatter data (one row per order) for discount vs margin.
5. Group by `Product_Category` for average discount bar.
6. Compute `Shipping_Ratio = Shipping_Cost / Total_Sales * 100`; group by category.
7. Add section headings and chart titles.

**Relevant Context:** `Discount_Percent` is integer 0–30. `Profit_Margin_%` from Sub-Task 1.

**Status:** [ ] pending

---

## Sub-Task 6 — Page 4: Customer & Segment Analysis

**Intent:** Help marketing understand which customer types and payment methods generate value and
which customers are highest-priority.

**Expected Outcomes:**
- Bar chart: Revenue by Customer_Segment.
- Bar chart: Profit by Customer_Segment.
- Bar chart: Average Order Value by Customer_Segment.
- Pie/donut chart: Payment Method distribution.
- Horizontal bar: Top 10 Customers by Revenue.
- Bar chart: Customer Order Frequency (orders per customer distribution or top customers).

**Todo List:**
1. Implement `page_customer_analysis(df)`.
2. Group by `Customer_Segment` for revenue, profit, and AOV.
3. Group by `Payment_Method` for pie chart.
4. Group by `Customer_Name` for top-10 revenue bar.
5. Compute order frequency (count of orders per customer) and show distribution or top-20 chart.
6. Add section headings and chart titles.

**Status:** [ ] pending

---

## Sub-Task 7 — Page 5: Geographic Intelligence

**Intent:** Show spatial distribution of revenue and profitability to guide market prioritisation.

**Expected Outcomes:**
- Horizontal bar chart: Revenue by Country (top 20).
- Grouped bar chart: Revenue and Profit by Region.
- Bar chart: Profit Margin % by Region.
- Table (st.dataframe): Country-level KPI table (Revenue, Profit, Margin %, Orders).

**Todo List:**
1. Implement `page_geographic_intelligence(df)`.
2. Group by `Country` for top-20 revenue bar.
3. Group by `Region` for revenue/profit grouped bar.
4. Group by `Region` for profit margin bar.
5. Group by `Country` for KPI table; format with 2 decimal places.
6. Add section headings and chart titles.

**Status:** [ ] pending

---

## Sub-Task 8 — Page 6: Risk & Opportunity

**Intent:** Surface actionable risk signals: loss-making orders, problem products, discount abuse,
shipping cost drains, and high-margin opportunities.

**Expected Outcomes:**
- KPI cards: count and % of loss-making orders.
- Table: Products with negative average profit (Negative-Profit Products).
- Table/chart: High-discount (>=20 %) loss-making orders summary.
- Horizontal bar: Top 10 products by Profit Margin % (opportunity).
- Bar chart: Top categories/products by Shipping_Cost drain (absolute total).

**Todo List:**
1. Implement `page_risk_opportunity(df)`.
2. Compute `loss_orders = df[df['Profit'] < 0]`; count and pct.
3. Group by `Product_Name`, filter where mean Profit < 0; show table.
4. Filter `(Discount_Percent >= 20) & (Profit < 0)`; summarise by product.
5. Group by `Product_Name`, compute mean Profit_Margin_%, get top 10 positive.
6. Group by `Product_Category`, sum `Shipping_Cost`; bar chart.
7. Add section headings.

**Status:** [ ] pending

---

## Sub-Task 9 — Page 7: Management Recommendations

**Intent:** Translate computed metrics into clear, data-driven written recommendations. Every
recommendation must cite a number calculated from the filtered data — no hard-coded text.

**Expected Outcomes:**
- "Observed Findings" section lists 6–8 bullet points built with f-strings from live calculations.
- "Recommended Actions" section lists matching action items.
- Findings and actions are clearly separated with headings.
- No recommendation is made that isn't backed by a computed value in the filtered DataFrame.

**Todo List:**
1. Implement `page_recommendations(df)`.
2. Compute ~8 key stats: overall margin, worst category margin, best category margin, loss-order
   pct, highest-discount category, top region, top segment, shipping drain ratio.
3. Build findings list using f-string formatting for each computed stat.
4. Build recommended actions list keyed to findings.
5. Render with `st.markdown` under two clear headings.
6. Add defensive check: if `df` is empty, show a "Select a wider date range" message.

**Status:** [ ] pending

---

## Sub-Task 10 — Polish, Validation & Syntax Check

**Intent:** Ensure the application is syntactically correct, handles edge cases, and presents a
clean, consistent visual style.

**Expected Outcomes:**
- No Python syntax errors (can be checked by `python -m py_compile`).
- All division-by-zero cases guarded with `np.where` or conditional checks.
- Empty DataFrame cases handled on every page.
- Consistent chart colour scheme throughout (use Plotly's built-in discrete or sequential scales).
- Sidebar date filter edge cases handled (start > end shows warning).
- All seven pages reachable and rendering without runtime errors on the full dataset.

**Todo List:**
1. Review every `/ Total_Sales` or `/ Profit` calculation for zero-division.
2. Add `if df.empty: st.warning(...); return` at the top of each page function.
3. Add `start > end` guard in `main()`.
4. Verify CSV path resolution works from project root.
5. Run `python -m py_compile ecommerce_intelligence_dashboard.py` and fix any errors.
6. Final read-through for style consistency.

**Status:** [ ] pending

---

## Implementation Notes

- **CSV path:** resolve with `pathlib.Path(__file__).parent / "data" / "global_ecommerce_sales.csv"`.
- **Caching:** `@st.cache_data` on `load_data()` only; filtering is fast enough without caching.
- **Chart library:** `plotly.express` for most charts; `plotly.graph_objects` only where px is insufficient.
- **Colours:** use `px.colors.qualitative.Set2` or `px.colors.qualitative.Plotly` for categorical consistency.
- **KPI cards:** `st.metric(label, value, delta=None)` in `st.columns`.
- **No ML, no internet, no external APIs.**
