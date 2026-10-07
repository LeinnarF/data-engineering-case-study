DROP SCHEMA IF EXISTS application CASCADE;
DROP SCHEMA IF EXISTS sales CASCADE;
DROP SCHEMA IF EXISTS warehouse CASCADE;

CREATE SCHEMA application;
CREATE SCHEMA sales;
CREATE SCHEMA warehouse;

-- =============================================================================
-- APPLICATION SCHEMA
-- =============================================================================

CREATE TABLE application.countries (
    CountryID INT PRIMARY KEY,
    CountryName VARCHAR(255),
    FormalName VARCHAR(255),
    LatestRecordedPopulation BIGINT,
    Continent VARCHAR(255),
    Region VARCHAR(255),
    Subregion VARCHAR(255)
);

CREATE TABLE application.state_provinces (
    StateProvinceID INT PRIMARY KEY,
    StateProvinceCode VARCHAR(50),
    StateProvinceName VARCHAR(255),
    CountryID INT,
    SalesTerritory VARCHAR(255),
    LatestRecordedPopulation BIGINT
);

CREATE TABLE application.cities (
    CityID INT PRIMARY KEY,
    CityName VARCHAR(255),
    StateProvinceID INT,
    Latitude VARCHAR(255),
    Longitude VARCHAR(255),
    LatestRecordedPopulation BIGINT
);

CREATE TABLE application.people (
    PersonID INT PRIMARY KEY,
    FullName VARCHAR(255),
    PreferredName VARCHAR(255),
    SearchName VARCHAR(255),
    IsEmployee BOOLEAN,
    IsSalesperson BOOLEAN
);

CREATE TABLE application.delivery_methods (
    DeliveryMethodID INT PRIMARY KEY,
    DeliveryMethodName VARCHAR(255)
);

CREATE TABLE application.payment_methods (
    PaymentMethodID INT PRIMARY KEY,
    PaymentMethodName VARCHAR(255)
);

CREATE TABLE application.transaction_types (
    TransactionTypeID INT PRIMARY KEY,
    TransactionTypeName VARCHAR(255)
);

-- =============================================================================
-- WAREHOUSE SCHEMA
-- =============================================================================

CREATE TABLE warehouse.colors (
    ColorID INT PRIMARY KEY,
    ColorName VARCHAR(255)
);

CREATE TABLE warehouse.package_types (
    PackageTypeID INT PRIMARY KEY,
    PackageTypeName VARCHAR(255)
);

CREATE TABLE warehouse.stock_groups (
    StockGroupID INT PRIMARY KEY,
    StockGroupName VARCHAR(255)
);

CREATE TABLE warehouse.stock_items (
    StockItemID INT PRIMARY KEY,
    StockItemName VARCHAR(255),
    SupplierID INT,
    ColorID INT,
    UnitPackageID INT,
    OuterPackageID INT,
    Brand VARCHAR(255),
    Size VARCHAR(255),
    LeadTimeDays INT,
    QuantityPerOuter INT,
    IsChillerStock BOOLEAN,
    Barcode VARCHAR(255),
    TaxRate DECIMAL(18,3),
    UnitPrice DECIMAL(18,2),
    RecommendedRetailPrice DECIMAL(18,2),
    TypicalWeightPerUnit DECIMAL(18,3)
);

-- =============================================================================
-- SALES SCHEMA
-- =============================================================================

CREATE TABLE sales.customer_categories (
    CustomerCategoryID INT PRIMARY KEY,
    CustomerCategoryName VARCHAR(255)
);

CREATE TABLE sales.buying_groups (
    BuyingGroupID INT PRIMARY KEY,
    BuyingGroupName VARCHAR(255)
);

CREATE TABLE sales.customers (
    CustomerID INT PRIMARY KEY,
    CustomerName VARCHAR(255),
    BillToCustomerID INT,
    CustomerCategoryID INT,
    BuyingGroupID INT,
    PrimaryContactPersonID INT,
    AlternateContactPersonID INT,
    DeliveryMethodID INT,
    DeliveryCityID INT,
    CreditLimit DECIMAL(18,2),
    AccountOpenedDate DATE,
    StandardDiscountPercentage DECIMAL(18,3),
    IsStatementSent BOOLEAN,
    IsOnCreditHold BOOLEAN,
    PaymentDays INT,
    PhoneNumber VARCHAR(255),
    WebsiteURL VARCHAR(255),
    DeliveryAddressLine TEXT,
    DeliveryLocationLat VARCHAR(255),
    DeliveryLocationLong VARCHAR(255)
);

CREATE TABLE sales.orders (
    OrderID INT PRIMARY KEY,
    CustomerID INT,
    SalespersonPersonID INT,
    PickedByPersonID INT,
    ContactPersonID INT,
    BackorderOrderID INT,
    OrderDate DATE,
    ExpectedDeliveryDate DATE,
    CustomerPurchaseOrderNumber VARCHAR(255),
    IsUndersupplyBackordered BOOLEAN,
    PickingCompletedWhen TIMESTAMP
);

CREATE TABLE sales.order_lines (
    OrderLineID INT PRIMARY KEY,
    OrderID INT,
    StockItemID INT,
    Description TEXT,
    PackageTypeID INT,
    Quantity INT,
    UnitPrice DECIMAL(18,2),
    TaxRate DECIMAL(18,3),
    PickedQuantity INT,
    PickingCompletedWhen TIMESTAMP
);

CREATE TABLE sales.invoices (
    InvoiceID INT PRIMARY KEY,
    CustomerID INT,
    BillToCustomerID INT,
    OrderID INT,
    DeliveryMethodID INT,
    ContactPersonID INT,
    AccountsPersonID INT,
    SalespersonPersonID INT,
    PackedByPersonID INT,
    InvoiceDate DATE,
    CustomerPurchaseOrderNumber VARCHAR(255),
    DeliveryInstructions TEXT,
    TotalDryItems INT,
    TotalChillerItems INT,
    ConfirmedDeliveryTime TIMESTAMP,
    ConfirmedReceivedBy VARCHAR(255)
);

CREATE TABLE sales.invoice_lines (
    InvoiceLineID INT PRIMARY KEY,
    InvoiceID INT,
    StockItemID INT,
    Description TEXT,
    PackageTypeID INT,
    Quantity INT,
    UnitPrice DECIMAL(18,2),
    TaxRate DECIMAL(18,3),
    TaxAmount DECIMAL(18,2),
    LineProfit DECIMAL(18,2),
    ExtendedPrice DECIMAL(18,2)
);

-- =============================================================================
-- FOREIGN KEY CONSTRAINTS (Optional but recommended for OLTP)
-- =============================================================================
-- We can add these later once data is loaded to avoid ingestion constraint errors,
-- or we can ensure they're loaded in the correct topological order.
