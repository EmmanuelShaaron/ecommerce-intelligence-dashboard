# E-Commerce Customer & Sales Intelligence Dashboard

## 1. Project Overview

The **E-Commerce Customer & Sales Intelligence Dashboard** is a Python-based business intelligence application developed to analyze e-commerce transaction data.

The project transforms raw transaction data into meaningful business insights covering:

- Key Performance Indicators (KPIs)
- Sales and profit trends
- Product and category performance
- Customer segment behavior
- Geographic performance
- Business risks
- Growth opportunities
- Management recommendations

The objective is to move beyond simple descriptive analysis and provide actionable insights that can support business decision-making.

---

## 2. Business Problem

E-commerce businesses generate large amounts of transaction data, but raw sales records alone do not clearly explain business performance.

This project analyzes transaction-level e-commerce data to identify:

- What is happening with sales and profitability
- Where sales and profit are heading over time
- Which factors influence business performance
- Where financial and operational risks exist
- Where opportunities for growth and improvement exist

The findings are presented through an interactive dashboard.

---

## 3. Business Objective

The main objective is to analyze e-commerce sales and customer data and convert the results into actionable business intelligence.

The project focuses on:

1. Measuring overall sales and profitability.
2. Identifying monthly and yearly sales trends.
3. Understanding product and category performance.
4. Comparing customer segments.
5. Analyzing geographic performance.
6. Identifying loss-making and high-discount transactions.
7. Identifying business opportunities.
8. Providing management recommendations based on the analysis.

---

## 4. Dataset

The project uses the **Global E-Commerce Sales & Customer Data** dataset.

The dataset contains transaction-level information including:

- Order ID
- Order Date
- Customer Name
- Customer Segment
- Country
- Region
- Product Category
- Product Name
- Quantity
- Unit Price
- Discount Percentage
- Total Sales
- Shipping Cost
- Profit
- Payment Method

The dataset covers transactions from **2023 to 2025**.

### Dataset Source

Kaggle:

https://www.kaggle.com/code/muhammadaammartufail/global-e-commerce-sales-customer-analytics/input

---

## 5. Key Business Intelligence Areas

### KPIs — What is happening?

The dashboard calculates important business metrics such as:

- Total Revenue
- Total Profit
- Profit Margin
- Number of Orders
- Units Sold
- Average Order Value
- Average Profit per Order
- Loss-Making Orders
- Average Discount
- Shipping Cost Ratio

### Trends — Where is the business heading?

The application analyzes:

- Monthly revenue trends
- Monthly profit trends
- Order trends
- Year-over-year performance
- Seasonal performance
- Category trends
- Discount trends
- Profit margin trends

### Drivers — Why is it happening?

The analysis investigates relationships between:

- Discounts and profit margins
- Product categories and profitability
- Customer segments and sales
- Shipping costs and profitability
- Quantity and profit
- Regions and profitability
- Payment methods and order value

### Risks

The dashboard identifies potential business risks including:

- Loss-making orders
- High-discount loss-making transactions
- High shipping-cost impact
- Category-level margin problems
- Regional concentration
- Products with negative cumulative profit

### Opportunities

The analysis identifies opportunities such as:

- High-margin products
- Strong products with lower discount dependency
- High-performing customer segments
- Emerging geographic markets
- High-volume products
- Areas where pricing or discount strategies can be improved

---

## 6. Dashboard Pages

The application contains seven main analytical sections.

### Page 1 — Executive Overview

Provides a high-level summary of business performance using major KPIs and overview visualizations.

### Page 2 — Sales & Trend Analysis

Analyzes revenue, profit, orders and other business metrics over time.

It includes monthly, yearly and seasonal trend analysis.

### Page 3 — Product & Category Intelligence

Analyzes product and category performance using sales, profit, quantity and margin-related metrics.

### Page 4 — Customer & Segment Analysis

Examines customer segments and purchasing behavior to understand how different customer groups contribute to business performance.

### Page 5 — Geographic Intelligence

Analyzes sales and profitability across countries and regions to identify geographic performance patterns.

### Page 6 — Risk & Opportunity Dashboard

Highlights potentially risky transactions, loss-making orders, discount-related issues and areas of business opportunity.

### Page 7 — Management Recommendations

Converts the analytical findings into practical recommendations that management can consider for improving sales, profitability and business performance.

---

## 7. Technologies Used

- Python
- Streamlit
- Pandas
- NumPy
- Plotly

### Python Libraries

The required Python dependencies are listed in:

`requirements.txt`

---

## 8. Project Structure

```text
ecommerce-intelligence-project/
│
├── ecommerce_intelligence_dashboard.py
├── requirements.txt
├── Project_Report.docx
├── README.md
│
└── data/
    └── global_ecommerce_sales.csv  