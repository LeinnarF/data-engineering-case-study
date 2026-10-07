-- =============================================================================
-- FOREIGN DATA WRAPPER SETUP
-- =============================================================================
CREATE EXTENSION IF NOT EXISTS postgres_fdw;
DROP SERVER IF EXISTS oltp_server CASCADE;
CREATE SERVER oltp_server FOREIGN DATA WRAPPER postgres_fdw OPTIONS (host 'localhost', dbname 'asb_oltp', port '5432');
CREATE USER MAPPING FOR current_user SERVER oltp_server OPTIONS (user 'db_user', password 'db_password');

CREATE SCHEMA IF NOT EXISTS oltp_application;
CREATE SCHEMA IF NOT EXISTS oltp_sales;
CREATE SCHEMA IF NOT EXISTS oltp_warehouse;

IMPORT FOREIGN SCHEMA application FROM SERVER oltp_server INTO oltp_application;
IMPORT FOREIGN SCHEMA sales FROM SERVER oltp_server INTO oltp_sales;
IMPORT FOREIGN SCHEMA warehouse FROM SERVER oltp_server INTO oltp_warehouse;

-- =============================================================================
-- 1. LOAD DIMENSIONS
-- =============================================================================

-- 1A. dim_date
TRUNCATE TABLE dim_date;
INSERT INTO dim_date (date_key, full_date, day_of_month, month_number, month_name, calendar_quarter, calendar_year, fiscal_month_number, fiscal_quarter, fiscal_year, weekday_name)
SELECT 
    TO_CHAR(datum, 'YYYYMMDD')::INT AS date_key,
    datum AS full_date,
    EXTRACT(DAY FROM datum) AS day_of_month,
    EXTRACT(MONTH FROM datum) AS month_number,
    TRIM(TO_CHAR(datum, 'Month')) AS month_name,
    EXTRACT(QUARTER FROM datum) AS calendar_quarter,
    EXTRACT(YEAR FROM datum) AS calendar_year,
    CASE WHEN EXTRACT(MONTH FROM datum) >= 11 THEN EXTRACT(MONTH FROM datum) - 10 ELSE EXTRACT(MONTH FROM datum) + 2 END AS fiscal_month_number,
    CASE WHEN EXTRACT(MONTH FROM datum) >= 11 THEN 1
         WHEN EXTRACT(MONTH FROM datum) IN (1,2,3) THEN 2
         WHEN EXTRACT(MONTH FROM datum) IN (4,5,6) THEN 3
         ELSE 4 END AS fiscal_quarter,
    CASE WHEN EXTRACT(MONTH FROM datum) >= 11 THEN EXTRACT(YEAR FROM datum) + 1 ELSE EXTRACT(YEAR FROM datum) END AS fiscal_year,
    TRIM(TO_CHAR(datum, 'Day')) AS weekday_name
FROM (
    SELECT generate_series('2013-01-01'::date, '2020-12-31'::date, '1 day'::interval)::date AS datum
) dates;

-- 1B. dim_city
TRUNCATE TABLE dim_city RESTART IDENTITY CASCADE;
INSERT INTO dim_city (city_id, city_name, state_province_name, country_name, continent, region, subregion, latest_recorded_population)
SELECT 
    c.CityID,
    c.CityName,
    sp.StateProvinceName,
    co.CountryName,
    co.Continent,
    co.Region,
    co.Subregion,
    c.LatestRecordedPopulation
FROM oltp_application.cities c
JOIN oltp_application.state_provinces sp ON c.StateProvinceID = sp.StateProvinceID
JOIN oltp_application.countries co ON sp.CountryID = co.CountryID;

-- 1C. dim_employee
TRUNCATE TABLE dim_employee RESTART IDENTITY CASCADE;
INSERT INTO dim_employee (person_id, full_name, preferred_name, is_salesperson)
SELECT 
    PersonID,
    FullName,
    PreferredName,
    IsSalesperson
FROM oltp_application.people
WHERE IsEmployee = TRUE;

-- 1D. dim_stock_item
TRUNCATE TABLE dim_stock_item RESTART IDENTITY CASCADE;
INSERT INTO dim_stock_item (stock_item_id, stock_item_name, color_name, package_type_name, brand, size, is_chiller_stock, tax_rate, unit_price, recommended_retail_price)
SELECT 
    si.StockItemID,
    si.StockItemName,
    c.ColorName,
    pt.PackageTypeName,
    si.Brand,
    si.Size,
    si.IsChillerStock,
    si.TaxRate,
    si.UnitPrice,
    si.RecommendedRetailPrice
FROM oltp_warehouse.stock_items si
LEFT JOIN oltp_warehouse.colors c ON si.ColorID = c.ColorID
LEFT JOIN oltp_warehouse.package_types pt ON si.UnitPackageID = pt.PackageTypeID;

-- 1E. dim_customer (SCD Type 2 Implementation)
WITH source AS (
    SELECT 
        c.CustomerID AS customer_id,
        c.CustomerName AS customer_name,
        cc.CustomerCategoryName AS customer_category_name,
        bg.BuyingGroupName AS buying_group_name,
        ci.CityName AS delivery_city_name,
        c.StandardDiscountPercentage AS standard_discount_percentage,
        c.IsStatementSent AS is_statement_sent,
        c.IsOnCreditHold AS is_on_credit_hold,
        c.PaymentDays AS payment_days,
        CURRENT_TIMESTAMP AS valid_from,
        '9999-12-31 23:59:59'::timestamp AS valid_to,
        TRUE AS is_current
    FROM oltp_sales.customers c
    LEFT JOIN oltp_sales.customer_categories cc ON c.CustomerCategoryID = cc.CustomerCategoryID
    LEFT JOIN oltp_sales.buying_groups bg ON c.BuyingGroupID = bg.BuyingGroupID
    LEFT JOIN oltp_application.cities ci ON c.DeliveryCityID = ci.CityID
),
updated AS (
    UPDATE dim_customer target
    SET valid_to = CURRENT_TIMESTAMP, is_current = FALSE
    FROM source
    WHERE target.customer_id = source.customer_id
      AND target.is_current = TRUE
      AND (
          target.customer_category_name IS DISTINCT FROM source.customer_category_name OR
          target.buying_group_name IS DISTINCT FROM source.buying_group_name OR
          target.standard_discount_percentage IS DISTINCT FROM source.standard_discount_percentage OR
          target.delivery_city_name IS DISTINCT FROM source.delivery_city_name
      )
    RETURNING target.customer_id
)
INSERT INTO dim_customer (customer_id, customer_name, customer_category_name, buying_group_name, delivery_city_name, standard_discount_percentage, is_statement_sent, is_on_credit_hold, payment_days, valid_from, valid_to, is_current)
SELECT 
    s.customer_id, s.customer_name, s.customer_category_name, s.buying_group_name, s.delivery_city_name, s.standard_discount_percentage, s.is_statement_sent, s.is_on_credit_hold, s.payment_days, s.valid_from, s.valid_to, s.is_current
FROM source s
LEFT JOIN dim_customer target 
    ON s.customer_id = target.customer_id AND target.is_current = TRUE
WHERE target.customer_id IS NULL;


-- =============================================================================
-- 2. LOAD FACTS
-- =============================================================================

-- 2A. fact_order
TRUNCATE TABLE fact_order RESTART IDENTITY;
INSERT INTO fact_order (order_id, order_line_id, order_date_key, picked_date_key, customer_key, salesperson_key, picker_key, stock_item_key, ordered_quantity, picked_quantity, unit_price, tax_rate, is_undersupply_backordered)
SELECT 
    o.OrderID,
    ol.OrderLineID,
    TO_CHAR(o.OrderDate, 'YYYYMMDD')::INT,
    TO_CHAR(ol.PickingCompletedWhen, 'YYYYMMDD')::INT,
    COALESCE(c.customer_key, -1),
    COALESCE(sp.employee_key, -1),
    COALESCE(pk.employee_key, -1),
    COALESCE(si.stock_item_key, -1),
    ol.Quantity,
    ol.PickedQuantity,
    ol.UnitPrice,
    ol.TaxRate,
    o.IsUndersupplyBackordered
FROM oltp_sales.order_lines ol
JOIN oltp_sales.orders o ON ol.OrderID = o.OrderID
LEFT JOIN dim_customer c ON o.CustomerID = c.customer_id AND c.is_current = TRUE
LEFT JOIN dim_employee sp ON o.SalespersonPersonID = sp.person_id
LEFT JOIN dim_employee pk ON o.PickedByPersonID = pk.person_id
LEFT JOIN dim_stock_item si ON ol.StockItemID = si.stock_item_id;

-- 2B. fact_sale
TRUNCATE TABLE fact_sale RESTART IDENTITY;
INSERT INTO fact_sale (invoice_id, invoice_line_id, invoice_date_key, delivery_date_key, customer_key, salesperson_key, stock_item_key, invoiced_quantity, unit_price, tax_rate, tax_amount, line_profit, extended_price, days_from_order_to_invoice)
SELECT 
    i.InvoiceID,
    il.InvoiceLineID,
    TO_CHAR(i.InvoiceDate, 'YYYYMMDD')::INT,
    TO_CHAR(i.ConfirmedDeliveryTime, 'YYYYMMDD')::INT,
    COALESCE(c.customer_key, -1),
    COALESCE(sp.employee_key, -1),
    COALESCE(si.stock_item_key, -1),
    il.Quantity,
    il.UnitPrice,
    il.TaxRate,
    il.TaxAmount,
    il.LineProfit,
    il.ExtendedPrice,
    i.InvoiceDate - o.OrderDate AS days_from_order_to_invoice
FROM oltp_sales.invoice_lines il
JOIN oltp_sales.invoices i ON il.InvoiceID = i.InvoiceID
LEFT JOIN oltp_sales.orders o ON i.OrderID = o.OrderID
LEFT JOIN dim_customer c ON i.CustomerID = c.customer_id AND c.is_current = TRUE
LEFT JOIN dim_employee sp ON i.SalespersonPersonID = sp.person_id
LEFT JOIN dim_stock_item si ON il.StockItemID = si.stock_item_id;
