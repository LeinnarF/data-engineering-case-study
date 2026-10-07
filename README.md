# Wide World Importers - Data Engineering Pipeline

This project builds an end-to-end data pipeline using the Wide World Importers dataset, demonstrating the flow from raw CSV files to a normalized OLTP database, and finally to an analytics-ready dimensional model (OLAP).

## Tech Stack
- **Database**: PostgreSQL (via Docker)
- **Orchestration**: Python (`src/pipeline.py`)
- **Transformations**: Python/SQL

## Project Structure
- `raw_data/`: Directory to place the raw CSV files downloaded from Kaggle.
- `sql/`: Contains SQL scripts for schema creation and transformations.
  - `oltp/`: Scripts to initialize and validate the operational database.
  - `olap/`: Scripts to create staging, dimension, and fact tables.
- `src/`: Python source code for orchestrating the pipeline.
- `docker-compose.yml`: Local PostgreSQL setup.
- `.env`: Environment variables for database connection.

## Setup Instructions

### 1. Start the Database
Ensure Docker is installed and running, then start the PostgreSQL container:
```bash
docker-compose up -d
```

### 2. Download the Dataset
1. Go to the [Wide World Importers CSV dataset on Kaggle](https://www.kaggle.com/datasets/pauloviniciusornelas/wwimporters).
2. Download the dataset archive and extract all CSV files into the `raw_data/` directory.

### 3. Setup Python Environment
It is recommended to use a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Run the Pipeline
Execute the main orchestrator script:
```bash
python src/pipeline.py
```

## Next Steps
- Write SQL definitions for the OLTP tables based on the CSV schema.
- Implement the CSV ingestion logic in Python (e.g. using `psycopg2` or `pandas`).
- Design the OLAP star schema (`dim_date`, `dim_customer`, `fact_sales`, etc.) and write the transformation queries.
