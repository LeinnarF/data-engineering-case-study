import os
import logging
from dotenv import load_dotenv

from ingest import run_ingestion

from data_quality import validate_oltp, validate_olap
from transform import run_transformation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Data Engineering Pipeline...")
    
    # Load environment variables
    load_dotenv()
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_user = os.getenv("DB_USER", "db_user")
    db_password = os.getenv("DB_PASSWORD", "db_password")
    db_name_oltp = os.getenv("DB_NAME_OLTP", "asb_oltp")
    db_name_olap = os.getenv("DB_NAME_OLAP", "asb_olap")
    
    # 1. Validate that the required source files are available
    logger.info("Step 1: Validating raw data files...")
    if not os.path.exists("data/raw_data/archive/Sales/Sales.Orders.csv"):
        logger.error("Raw data not found! Please download and extract Kaggle dataset to data/raw_data/archive/")
        return
    
    # 2 & 3. Create OLTP schema and ingest data
    logger.info("Steps 2 & 3: Creating OLTP schema and ingesting CSV data...")
    run_ingestion(db_host, db_port, db_user, db_password, db_name_oltp)
    
    # 4. Validate the OLTP load
    logger.info("Step 4: Validating OLTP load...")
    validate_oltp(db_host, db_port, db_user, db_password, db_name_oltp)
    
    # 5, 6, 7. Prepare schemas and load Dimensions/Facts
    logger.info("Steps 5, 6, 7: Preparing OLAP database schemas and loading data...")
    run_transformation(db_host, db_port, db_user, db_password, db_name_olap)
    
    # 8. Run final data-quality checks
    logger.info("Step 8: Running final data quality checks...")
    validate_olap(db_host, db_port, db_user, db_password, db_name_olap)
    
    logger.info("Pipeline completed successfully!")

if __name__ == "__main__":
    main()
