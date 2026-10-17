# Cryptocurrency Market Data Engineering Pipeline

An end-to-end data engineering project that extracts cryptocurrency market data from the CoinGecko API, validates and transforms the data using Python, loads it into Microsoft SQL Server, automates the workflow with Apache Airflow, and presents market insights through Power BI.

## Project Overview

This project demonstrates how to build an automated data pipeline for cryptocurrency market data, from API extraction to database storage and business intelligence reporting.

The pipeline is designed to support repeatable data processing, data quality checks, structured SQL storage, and historical market analysis.

## Architecture

```text
CoinGecko API
      |
      v
Python Data Extraction
      |
      v
Raw CSV Data
      |
      v
Data Validation
      |
      +------> Rejected Records
      |
      v
Data Transformation
      |
      v
Transformed CSV Data
      |
      v
Microsoft SQL Server
      |
      +------> Staging Tables
      |
      +------> Historical Warehouse
      |
      v
SQL Analytics
      |
      v
Power BI Dashboard

Apache Airflow
      |
      +------> Orchestrates the Pipeline
```

## Technologies Used

| Technology           | Purpose                                  |
| -------------------- | ---------------------------------------- |
| Python               | Pipeline development and data processing |
| Pandas               | Data cleaning and transformation         |
| NumPy                | Numerical data processing                |
| Requests             | API integration                          |
| CoinGecko API        | Cryptocurrency market data source        |
| Microsoft SQL Server | Data storage and querying                |
| SQLAlchemy           | Database connectivity                    |
| pyodbc               | SQL Server connectivity                  |
| Apache Airflow       | Workflow orchestration and scheduling    |
| Power BI             | Dashboard development and visualization  |
| Git and GitHub       | Version control and project hosting      |

## Key Features

* **API Extraction:** Retrieves cryptocurrency market data from CoinGecko.
* **Data Validation:** Checks incoming records and separates rejected records.
* **Data Transformation:** Processes validated data before loading.
* **CSV Data Storage:** Maintains raw, processed, transformed, and rejected data files.
* **SQL Server Integration:** Loads market data into a relational database.
* **Historical Data Storage:** Stores cryptocurrency snapshots for historical analysis.
* **Workflow Automation:** Uses Apache Airflow to schedule and monitor pipeline execution.
* **SQL Analytics:** Supports market analysis through SQL queries.
* **Power BI Dashboard:** Visualizes cryptocurrency market information.
* **Logging and Monitoring:** Maintains pipeline execution logs.

## Project Structure

```text
crypto_data_pipeline/
│
├── crypto_extractor.py
├── crypto_pipeline.py
├── requirements.txt
├── .gitignore
│
├── src/
│   ├── crypto_validator.py
│   ├── crypto_transformer.py
│   └── crypto_loader.py
│
├── crypto_sql_scripts/
│   ├── _analytics_and_analysis.sql
│   ├── crypto.schema.sql
│   ├── crypto.validation.sql
│   └── crypto_Tabel_and _Views.sql
│
├── dags/
│   └── crypto_market_pipeline_dag.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── transformed/
│   └── rejected/
│
├── logs/
│
└── powerbi_1/
    └── Crypto_Market_Intelligence_Dashboard.pbix
```

## Pipeline Workflow

### 1. Extract

The extraction component retrieves cryptocurrency market information from the CoinGecko API and saves the raw response as CSV files.

### 2. Validate

The validation component checks incoming records and separates valid data from rejected records.

### 3. Transform

The transformation component prepares validated data for database loading and downstream analysis.

### 4. Load

The loading component connects Python to Microsoft SQL Server and loads cryptocurrency market records into the database.

### 5. Store Historical Data

Historical cryptocurrency snapshots are stored in the warehouse to support time-based analysis.

### 6. Automate with Airflow

Apache Airflow orchestrates the pipeline, allowing scheduled execution and monitoring of pipeline runs.

### 7. Analyze with SQL and Power BI

SQL scripts support database validation and market analysis. The Power BI dashboard presents market information in a visual format.

## Database

**Database:** `CryptoMarketDW`

The project uses the following SQL Server objects:

| Object                         | Purpose                                      |
| ------------------------------ | -------------------------------------------- |
| `staging.crypto_market`        | Stores current cryptocurrency market records |
| `warehouse.CryptoPriceHistory` | Stores historical market snapshots           |

Additional SQL scripts support schema setup, validation, analysis, and database views.

## Power BI Dashboard

The project includes a Power BI dashboard named:

`Crypto_Market_Intelligence_Dashboard.pbix`

The dashboard is intended to help users explore cryptocurrency market information and historical trends.

To view the dashboard, download the PBIX file from the repository and open it using Power BI Desktop.

Database connectivity or data refresh may require your own SQL Server connection settings.

## Prerequisites

Before running the project, install or configure:

* Python 3.12 or a compatible Python version
* Microsoft SQL Server
* SQL Server ODBC driver
* Apache Airflow in a supported environment
* Power BI Desktop (for dashboard viewing)
* Git

You also need access to the CoinGecko API.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/danisajjo1231-stack/crypto-data-engineering-pipeline.git
```

### 2. Open the project directory

```bash
cd crypto-data-engineering-pipeline
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure SQL Server

Configure the SQL Server connection in the project's database-loading component to match your local environment.

Create or configure the `CryptoMarketDW` database and required schemas and tables using the supplied SQL scripts.

Do not publish database passwords, API secrets, or other sensitive credentials to GitHub.

## Running the Pipeline

After configuring the database connection and required dependencies, run the main pipeline from the project root:

```bash
python crypto_pipeline.py
```

The pipeline processes market data through its extraction, validation, transformation, and loading stages.

Check the console output and application logs to monitor execution and identify errors.

## Running with Apache Airflow

The Airflow DAG is located at:

```text
dags/crypto_market_pipeline_dag.py
```

The DAG is named:

`crypto_market_pipeline`

Configure Airflow and the DAG's execution environment according to your local setup before enabling scheduled runs.

The pipeline's Python environment and SQL Server connection must be accessible to the Airflow tasks.

## Data Quality

Data quality is an important part of this project.

The pipeline includes validation and separates rejected records from valid records. This helps prevent invalid input data from being processed as if it were correct.

The raw and processed CSV files also make it easier to inspect data at different stages of the workflow.

## Future Improvements

Potential improvements include:

* Add automated unit and integration tests.
* Introduce a dedicated data quality reporting layer.
* Add retry handling and alerting for API failures.
* Improve incremental loading and historical snapshot management.
* Add Docker-based deployment.
* Deploy the pipeline to a cloud platform.
* Add CI/CD checks through GitHub Actions.

## Author

**Danish Muhammad**

Aspiring Data Engineer | Python | SQL Server | ETL Pipelines | Apache Airflow | Power BI

GitHub: [Danish311 / Crypto Data Engineering Pipeline](https://github.com/danisajjo1231-stack/crypto-data-engineering-pipeline)

---

This project was developed as part of a hands-on data engineering portfolio, focusing on API integration, data processing, database loading, workflow orchestration, and business intelligence.
