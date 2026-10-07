import os
import logging
import psycopg

logger = logging.getLogger(__name__)

def init_oltp_schema(conn: psycopg.Connection):
    """Executes the OLTP initialization SQL script to create schemas and tables."""
    sql_file_path = os.path.join("data", "sql", "oltp", "oltp_init.sql")
    
    if not os.path.exists(sql_file_path):
        raise FileNotFoundError(f"Initialization script not found at {sql_file_path}")
        
    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql = f.read()
        
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    logger.info("OLTP schemas and tables successfully created.")

def load_csv_to_table(conn: psycopg.Connection, table_name: str, csv_path: str):
    """Loads a CSV file directly into a PostgreSQL table using the highly efficient COPY command."""
    if not os.path.exists(csv_path):
        logger.warning(f"File not found, skipping: {csv_path}")
        return

    # Using psycopg COPY. The files are semicolon-delimited and contain headers.
    with conn.cursor() as cur:
        # The CSV uses DD/MM/YYYY date formatting
        cur.execute("SET DateStyle = 'DMY';")
        # We use encoding="utf-8-sig" to automatically handle the BOM (\ufeff) present in the files
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            with cur.copy(f"COPY {table_name} FROM STDIN WITH (FORMAT csv, HEADER true, DELIMITER ';', NULL 'NULL')") as copy:
                while data := f.read(8192):
                    copy.write(data)
    conn.commit()
    logger.info(f"Loaded {table_name} from {csv_path}")

def run_ingestion(db_host, db_port, db_user, db_password, db_name):
    """Main ingestion flow."""
    conn_str = f"host={db_host} port={db_port} user={db_user} password={db_password} dbname={db_name}"
    
    # Mapping of tables to their corresponding CSV file paths
    # Note: These paths assume the user extracted the Kaggle dataset into data/raw_data/archive/
    base_dir = os.path.join("data", "raw_data", "archive")
    
    table_files = {
        "application.countries": os.path.join(base_dir, "Application", "Application.Countries.csv"),
        "application.state_provinces": os.path.join(base_dir, "Application", "Application.StateProvinces.csv"),
        "application.cities": os.path.join(base_dir, "Application", "Application.Cities.csv"),
        "application.people": os.path.join(base_dir, "Application", "Application.People.csv"),
        "application.delivery_methods": os.path.join(base_dir, "Application", "Application.DeliveryMethods.csv"),
        "application.payment_methods": os.path.join(base_dir, "Application", "Application.PaymentMethods.csv"),
        "application.transaction_types": os.path.join(base_dir, "Application", "Application.TransactionTypes.csv"),
        
        "warehouse.colors": os.path.join(base_dir, "Warehouse", "Warehouse.Colors.csv"),
        "warehouse.package_types": os.path.join(base_dir, "Warehouse", "Warehouse.PackageTypes.csv"),
        "warehouse.stock_groups": os.path.join(base_dir, "Warehouse", "Warehouse.StockGroups.csv"),
        "warehouse.stock_items": os.path.join(base_dir, "Warehouse", "Warehouse.StockItems.csv"),
        
        "sales.customer_categories": os.path.join(base_dir, "Sales", "Sales.CustomerCategories.csv"),
        "sales.buying_groups": os.path.join(base_dir, "Sales", "Sales.BuyingGroups.csv"),
        "sales.customers": os.path.join(base_dir, "Sales", "Sales.Customers.csv"),
        "sales.orders": os.path.join(base_dir, "Sales", "Sales.Orders.csv"),
        "sales.order_lines": os.path.join(base_dir, "Sales", "Sales.OrderLines.csv"),
        "sales.invoices": os.path.join(base_dir, "Sales", "Sales.Invoices.csv"),
        "sales.invoice_lines": os.path.join(base_dir, "Sales", "Sales.InvoiceLines.csv")
    }

    try:
        with psycopg.connect(conn_str) as conn:
            # 1. Initialize schema
            logger.info("Initializing OLTP schema...")
            init_oltp_schema(conn)
            
            # 2. Load all CSVs
            logger.info("Loading CSV files into OLTP tables...")
            for table_name, csv_path in table_files.items():
                load_csv_to_table(conn, table_name, csv_path)
                
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        raise
