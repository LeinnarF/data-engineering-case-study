import logging
import psycopg

logger = logging.getLogger(__name__)

def validate_oltp(db_host, db_port, db_user, db_password, db_name):
    """Runs data quality checks against the loaded OLTP database."""
    conn_str = f"host={db_host} port={db_port} user={db_user} password={db_password} dbname={db_name}"
    
    checks = [
        {
            "name": "Check for NULL Primary Keys in Orders",
            "query": "SELECT COUNT(*) FROM sales.orders WHERE OrderID IS NULL;",
            "expected": 0,
            "error_msg": "Found NULL OrderIDs in sales.orders"
        },
        {
            "name": "Check for Duplicate Primary Keys in Customers",
            "query": "SELECT COUNT(*) FROM (SELECT CustomerID FROM sales.customers GROUP BY CustomerID HAVING COUNT(*) > 1) AS duplicates;",
            "expected": 0,
            "error_msg": "Found duplicate CustomerIDs in sales.customers"
        },
        {
            "name": "Check Foreign Key Integrity (OrderLines -> Orders)",
            "query": "SELECT COUNT(*) FROM sales.order_lines WHERE OrderID NOT IN (SELECT OrderID FROM sales.orders);",
            "expected": 0,
            "error_msg": "Found OrderLines referencing non-existent Orders"
        },
        {
            "name": "Check Foreign Key Integrity (Orders -> Customers)",
            "query": "SELECT COUNT(*) FROM sales.orders WHERE CustomerID NOT IN (SELECT CustomerID FROM sales.customers);",
            "expected": 0,
            "error_msg": "Found Orders referencing non-existent Customers"
        },
        {
            "name": "Validate Quantities (Quantity >= 0 in OrderLines)",
            "query": "SELECT COUNT(*) FROM sales.order_lines WHERE Quantity < 0;",
            "expected": 0,
            "error_msg": "Found negative quantities in sales.order_lines"
        },
        {
            "name": "Validate Monetary Values (UnitPrice >= 0 in StockItems)",
            "query": "SELECT COUNT(*) FROM warehouse.stock_items WHERE UnitPrice < 0;",
            "expected": 0,
            "error_msg": "Found negative UnitPrice in warehouse.stock_items"
        }
    ]

    failed_checks = 0

    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                for check in checks:
                    cur.execute(check["query"])
                    result = cur.fetchone()[0]
                    
                    if result == check["expected"]:
                        logger.info(f"PASS - {check['name']}")
                    else:
                        logger.error(f"FAIL - {check['name']}: Expected {check['expected']}, but got {result}. {check['error_msg']}")
                        failed_checks += 1
                        
        if failed_checks > 0:
            logger.warning(f"OLTP Validation finished with {failed_checks} failed checks. Check logs for details.")
        else:
            logger.info("All OLTP data quality checks passed successfully!")
            
    except Exception as e:
        logger.error(f"Error executing data quality checks: {e}")
        raise

def validate_olap(db_host, db_port, db_user, db_password, db_name):
    """Runs data quality checks against the loaded OLAP database."""
    conn_str = f"host={db_host} port={db_port} user={db_user} password={db_password} dbname={db_name}"
    
    checks = [
        {
            "name": "Check for Orphaned Facts (fact_sale -> dim_customer)",
            "query": "SELECT COUNT(*) FROM fact_sale WHERE customer_key = -1;",
            "expected": 0,
            "error_msg": "Found Sales Facts that did not resolve to a valid Customer dimension."
        },
        {
            "name": "Check for Orphaned Facts (fact_sale -> dim_stock_item)",
            "query": "SELECT COUNT(*) FROM fact_sale WHERE stock_item_key = -1;",
            "expected": 0,
            "error_msg": "Found Sales Facts that did not resolve to a valid Stock Item dimension."
        },
        {
            "name": "SCD2: Only one active record per Customer",
            "query": "SELECT COUNT(*) FROM (SELECT customer_id FROM dim_customer WHERE is_current = TRUE GROUP BY customer_id HAVING COUNT(*) > 1) AS duplicates;",
            "expected": 0,
            "error_msg": "Found customers with multiple active (is_current = TRUE) SCD2 records."
        },
        {
            "name": "SCD2: No overlapping date ranges",
            "query": "SELECT COUNT(*) FROM dim_customer c1 JOIN dim_customer c2 ON c1.customer_id = c2.customer_id AND c1.customer_key != c2.customer_key WHERE c1.valid_from < c2.valid_to AND c1.valid_to > c2.valid_from;",
            "expected": 0,
            "error_msg": "Found overlapping effective date ranges in dim_customer."
        }
    ]

    failed_checks = 0

    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                for check in checks:
                    cur.execute(check["query"])
                    result = cur.fetchone()[0]
                    
                    if result == check["expected"]:
                        logger.info(f"PASS - {check['name']}")
                    else:
                        logger.error(f"FAIL - {check['name']}: Expected {check['expected']}, but got {result}. {check['error_msg']}")
                        failed_checks += 1
                        
        if failed_checks > 0:
            logger.warning(f"OLAP Validation finished with {failed_checks} failed checks. Check logs for details.")
        else:
            logger.info("All OLAP data quality checks passed successfully!")
            
    except Exception as e:
        logger.error(f"Error executing OLAP data quality checks: {e}")
        raise
