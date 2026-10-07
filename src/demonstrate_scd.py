import os
import logging
import psycopg
import pandas as pd
from dotenv import load_dotenv
from transform import run_transformation

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def demonstrate_scd():
    load_dotenv()
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_user = os.getenv("DB_USER", "db_user")
    db_password = os.getenv("DB_PASSWORD", "db_password")
    db_name_oltp = os.getenv("DB_NAME_OLTP", "asb_oltp")
    db_name_olap = os.getenv("DB_NAME_OLAP", "asb_olap")

    target_customer_id = 1
    new_category_id = 4 # Changing category

    logger.info("=== SCD Type 2 Demonstration ===")
    logger.info(f"Target Customer ID: {target_customer_id}")

    # 1. Update the record in OLTP
    logger.info("1. Simulating a change in the OLTP source system...")
    oltp_conn_str = f"host={db_host} port={db_port} user={db_user} password={db_password} dbname={db_name_oltp}"
    with psycopg.connect(oltp_conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute(f"UPDATE sales.customers SET CustomerCategoryID = {new_category_id} WHERE CustomerID = {target_customer_id};")
        conn.commit()
    logger.info(f"Successfully updated CustomerCategoryID to {new_category_id} for Customer {target_customer_id} in OLTP.")

    # 2. Trigger OLAP Transformation
    logger.info("2. Triggering the OLAP transformation (Pipeline Step 5-7) to capture changes...")
    run_transformation(db_host, db_port, db_user, db_password, db_name_olap)

    # 3. Query the results from OLAP to show history
    logger.info("3. Querying dim_customer in OLAP to prove SCD Type 2 history is maintained...")
    olap_conn_str = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name_olap}"
    
    query = f"""
    SELECT customer_key, customer_id, customer_name, customer_category_name, valid_from, valid_to, is_current 
    FROM dim_customer 
    WHERE customer_id = {target_customer_id}
    ORDER BY valid_from;
    """
    
    df = pd.read_sql(query, olap_conn_str)
    print("\n--- SCD TYPE 2 RESULTS ---")
    print(df.to_string(index=False))
    print("--------------------------\n")

if __name__ == "__main__":
    demonstrate_scd()
