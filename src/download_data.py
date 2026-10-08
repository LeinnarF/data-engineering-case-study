import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def download_kaggle_dataset():
    dataset = "pauloviniciusornelas/wwimporters"
    target_dir = "data/raw_data/archive"
    
    # Check if the critical files already exist
    if os.path.exists(os.path.join(target_dir, "Sales", "Sales.Orders.csv")):
        logger.info("Dataset already exists in data/raw_data/archive/. Skipping download.")
        return

    logger.info("Initializing Kaggle API...")
    try:
        # Import kaggle module. It automatically tries to authenticate using ~/.kaggle/kaggle.json
        import kaggle
    except ImportError:
        logger.error("Kaggle Python package not found. Please install it using: pip install kaggle")
        return
    except OSError as e:
        logger.error("Kaggle Authentication Error: Could not find kaggle.json!")
        logger.error("Please create a Kaggle API token from your Kaggle account settings")
        logger.error("and place the kaggle.json file in ~/.kaggle/ (Linux/Mac) or C:\\Users\\<User>\\.kaggle\\ (Windows).")
        logger.error(f"Details: {e}")
        return

    logger.info(f"Downloading dataset '{dataset}'...")
    try:
        kaggle.api.authenticate()
        
        # This automatically downloads and unzips the files into the target_dir
        kaggle.api.dataset_download_files(dataset, path=target_dir, unzip=True)
        
        logger.info(f"Successfully downloaded and extracted dataset to {target_dir}")
        
    except Exception as e:
        logger.error(f"Failed to download dataset: {e}")

if __name__ == "__main__":
    download_kaggle_dataset()
