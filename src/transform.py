import os
import logging
import psycopg

logger = logging.getLogger(__name__)

def execute_sql_file(conn: psycopg.Connection, filepath: str):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"SQL file not found at {filepath}")
        
    with open(filepath, "r", encoding="utf-8") as f:
        sql = f.read()
        
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()

def run_transformation(db_host, db_port, db_user, db_password, db_name_olap):
    """Executes the OLAP dimension and fact loading scripts using PostgreSQL FDW."""
    conn_str = f"host={db_host} port={db_port} user={db_user} password={db_password} dbname={db_name_olap}"
    
    try:
        with psycopg.connect(conn_str) as conn:
            # 1. Initialize OLAP schema (Tables)
            logger.info("Initializing OLAP Star Schema tables...")
            execute_sql_file(conn, os.path.join("data", "sql", "olap", "olap_init.sql"))
            
            # 2. Run FDW configuration and Transformations
            logger.info("Loading Dimensions and Facts into OLAP (via postgres_fdw)...")
            execute_sql_file(conn, os.path.join("data", "sql", "olap", "transform.sql"))
            
            logger.info("OLAP transformations completed successfully!")
            
    except Exception as e:
        logger.error(f"Error during OLAP transformation: {e}")
        raise
