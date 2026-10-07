DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;

-- =============================================================================
-- DIMENSIONS
-- =============================================================================

CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    day_of_month INT,
    month_number INT,
    month_name VARCHAR(20),
    calendar_quarter INT,
    calendar_year INT,
    fiscal_month_number INT,
    fiscal_quarter INT,
    fiscal_year INT,
    weekday_name VARCHAR(20)
);

CREATE TABLE dim_city (
    city_key SERIAL PRIMARY KEY,
    city_id INT NOT NULL, -- Business Key
    city_name VARCHAR(255),
    state_province_name VARCHAR(255),
    country_name VARCHAR(255),
    continent VARCHAR(255),
    region VARCHAR(255),
    subregion VARCHAR(255),
    latest_recorded_population BIGINT
);

CREATE TABLE dim_employee (
    employee_key SERIAL PRIMARY KEY,
    person_id INT NOT NULL, -- Business Key
    full_name VARCHAR(255),
    preferred_name VARCHAR(255),
    is_salesperson BOOLEAN
);

CREATE TABLE dim_stock_item (
    stock_item_key SERIAL PRIMARY KEY,
    stock_item_id INT NOT NULL, -- Business Key
    stock_item_name VARCHAR(255),
    color_name VARCHAR(255),
    package_type_name VARCHAR(255),
    brand VARCHAR(255),
    size VARCHAR(255),
    is_chiller_stock BOOLEAN,
    tax_rate DECIMAL(18,3),
    unit_price DECIMAL(18,2),
    recommended_retail_price DECIMAL(18,2)
);

-- =============================================================================
-- SLOWLY CHANGING DIMENSION TYPE 2
-- =============================================================================

CREATE TABLE dim_customer (
    customer_key SERIAL PRIMARY KEY, -- Surrogate Key
    customer_id INT NOT NULL,        -- Business Key
    customer_name VARCHAR(255),
    customer_category_name VARCHAR(255),
    buying_group_name VARCHAR(255),
    delivery_city_name VARCHAR(255),
    standard_discount_percentage DECIMAL(18,3),
    is_statement_sent BOOLEAN,
    is_on_credit_hold BOOLEAN,
    payment_days INT,
    -- SCD Type 2 Tracking Columns
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP NOT NULL,
    is_current BOOLEAN NOT NULL
);

-- =============================================================================
-- FACTS
-- =============================================================================

CREATE TABLE fact_order (
    order_line_key SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    order_line_id INT NOT NULL,
    order_date_key INT NOT NULL,
    picked_date_key INT,
    customer_key INT NOT NULL,
    salesperson_key INT NOT NULL,
    picker_key INT,
    stock_item_key INT NOT NULL,
    ordered_quantity INT,
    picked_quantity INT,
    unit_price DECIMAL(18,2),
    tax_rate DECIMAL(18,3),
    is_undersupply_backordered BOOLEAN
);

CREATE TABLE fact_sale (
    invoice_line_key SERIAL PRIMARY KEY,
    invoice_id INT NOT NULL,
    invoice_line_id INT NOT NULL,
    invoice_date_key INT NOT NULL,
    delivery_date_key INT,
    customer_key INT NOT NULL,
    salesperson_key INT NOT NULL,
    stock_item_key INT NOT NULL,
    invoiced_quantity INT,
    unit_price DECIMAL(18,2),
    tax_rate DECIMAL(18,3),
    tax_amount DECIMAL(18,2),
    line_profit DECIMAL(18,2),
    extended_price DECIMAL(18,2),
    days_from_order_to_invoice INT
);
