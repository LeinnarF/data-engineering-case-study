import json

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Wide World Importers - Business Queries\n",
                "This notebook connects to the `asb_olap` dimensional database to answer the 10 business questions from the case study."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import os\n",
                "import pandas as pd\n",
                "from sqlalchemy import create_engine\n",
                "from dotenv import load_dotenv\n",
                "\n",
                "load_dotenv()\n",
                "db_user = os.getenv('DB_USER', 'db_user')\n",
                "db_password = os.getenv('DB_PASSWORD', 'db_password')\n",
                "db_host = os.getenv('DB_HOST', 'localhost')\n",
                "db_port = os.getenv('DB_PORT', '5432')\n",
                "db_name = os.getenv('DB_NAME_OLAP', 'asb_olap')\n",
                "\n",
                "engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')\n",
                "\n",
                "def run_query(sql):\n",
                "    return pd.read_sql(sql, engine)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["### Q1. What are total sales, quantity sold, and profit by month and fiscal year?"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "q1 = \"\"\"\n",
                "SELECT \n",
                "    d.fiscal_year,\n",
                "    d.month_name,\n",
                "    SUM(f.extended_price) AS total_sales,\n",
                "    SUM(f.invoiced_quantity) AS total_quantity_sold,\n",
                "    SUM(f.line_profit) AS total_profit\n",
                "FROM fact_sale f\n",
                "JOIN dim_date d ON f.invoice_date_key = d.date_key\n",
                "GROUP BY d.fiscal_year, d.month_number, d.month_name\n",
                "ORDER BY d.fiscal_year, d.month_number;\n",
                "\"\"\"\n",
                "run_query(q1).head(12)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["### Q2. Which products and product categories generate the highest sales and profit?"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "q2 = \"\"\"\n",
                "SELECT \n",
                "    s.stock_item_name,\n",
                "    s.package_type_name,\n",
                "    SUM(f.extended_price) AS total_sales,\n",
                "    SUM(f.line_profit) AS total_profit\n",
                "FROM fact_sale f\n",
                "JOIN dim_stock_item s ON f.stock_item_key = s.stock_item_key\n",
                "GROUP BY s.stock_item_name, s.package_type_name\n",
                "ORDER BY total_profit DESC\n",
                "LIMIT 10;\n",
                "\"\"\"\n",
                "run_query(q2)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["### Q3. Which customers and customer categories contribute the most revenue?"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "q3 = \"\"\"\n",
                "SELECT \n",
                "    c.customer_name,\n",
                "    c.customer_category_name,\n",
                "    SUM(f.extended_price) AS total_revenue\n",
                "FROM fact_sale f\n",
                "JOIN dim_customer c ON f.customer_key = c.customer_key\n",
                "GROUP BY c.customer_name, c.customer_category_name\n",
                "ORDER BY total_revenue DESC\n",
                "LIMIT 10;\n",
                "\"\"\"\n",
                "run_query(q3)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["### Q4. How do sales and profit vary by city, state or province, and sales territory?"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "q4 = \"\"\"\n",
                "SELECT \n",
                "    ci.city_name,\n",
                "    ci.state_province_name,\n",
                "    ci.region AS sales_territory,\n",
                "    SUM(f.extended_price) AS total_sales,\n",
                "    SUM(f.line_profit) AS total_profit\n",
                "FROM fact_sale f\n",
                "JOIN dim_customer c ON f.customer_key = c.customer_key\n",
                "-- We can join ci through the customer's delivery city name, or join dim_city directly if we had a city_key in the fact. \n",
                "-- Since we embedded delivery_city_name in dim_customer, we can use that, or join dim_city to get state and region:\n",
                "JOIN dim_city ci ON c.delivery_city_name = ci.city_name\n",
                "GROUP BY ci.city_name, ci.state_province_name, ci.region\n",
                "ORDER BY total_sales DESC\n",
                "LIMIT 10;\n",
                "\"\"\"\n",
                "run_query(q4)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["### Q5. Which employees or salespeople manage the highest-value orders and sales?"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "q5 = \"\"\"\n",
                "SELECT \n",
                "    e.full_name AS salesperson_name,\n",
                "    COUNT(DISTINCT f.invoice_id) AS total_invoices,\n",
                "    SUM(f.extended_price) AS total_sales_value\n",
                "FROM fact_sale f\n",
                "JOIN dim_employee e ON f.salesperson_key = e.employee_key\n",
                "GROUP BY e.full_name\n",
                "ORDER BY total_sales_value DESC;\n",
                "\"\"\"\n",
                "run_query(q5)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["### Q6. What proportion of ordered quantities is later invoiced?"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "q6 = \"\"\"\n",
                "-- This query compares total ordered quantity vs total invoiced quantity across the entire dataset.\n",
                "SELECT \n",
                "    (SELECT SUM(ordered_quantity) FROM fact_order) AS total_ordered,\n",
                "    (SELECT SUM(invoiced_quantity) FROM fact_sale) AS total_invoiced,\n",
                "    ROUND(CAST((SELECT SUM(invoiced_quantity) FROM fact_sale) AS DECIMAL) / \n",
                "          CAST((SELECT SUM(ordered_quantity) FROM fact_order) AS DECIMAL) * 100, 2) AS proportion_percent;\n",
                "\"\"\"\n",
                "run_query(q6)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["### Q7. How long does it take, on average, for an order to be invoiced?"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "q7 = \"\"\"\n",
                "SELECT \n",
                "    ROUND(AVG(days_from_order_to_invoice), 2) AS avg_days_to_invoice\n",
                "FROM fact_sale;\n",
                "\"\"\"\n",
                "run_query(q7)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["### Q8. Which orders contain backordered items, and what is their business impact?"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "q8 = \"\"\"\n",
                "SELECT \n",
                "    COUNT(DISTINCT order_id) AS total_backordered_orders,\n",
                "    SUM(ordered_quantity - COALESCE(picked_quantity, 0)) AS total_items_delayed,\n",
                "    SUM((ordered_quantity - COALESCE(picked_quantity, 0)) * unit_price) AS estimated_revenue_delayed\n",
                "FROM fact_order\n",
                "WHERE is_undersupply_backordered = TRUE;\n",
                "\"\"\"\n",
                "run_query(q8)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["### Q9 & Q10. Slowly Changing Dimensions (Tracking Historical Changes)"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "q9_10 = \"\"\"\n",
                "-- To demonstrate this, let's look at a customer that might have multiple records if we ran an update.\n",
                "-- Since we only loaded a single snapshot, most customers will have 1 active record.\n",
                "SELECT \n",
                "    customer_id, \n",
                "    customer_name, \n",
                "    customer_category_name, \n",
                "    valid_from, \n",
                "    valid_to, \n",
                "    is_current \n",
                "FROM dim_customer \n",
                "ORDER BY customer_id LIMIT 5;\n",
                "\"\"\"\n",
                "run_query(q9_10)"
            ]
        }
    ],
    "metadata": {
        "language_info": {
            "name": "python"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open("business_queries.ipynb", "w") as f:
    json.dump(notebook, f, indent=1)
