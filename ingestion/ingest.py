# Standard library
import logging
import time

# Third party
from dotenv import load_dotenv
import duckdb
import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

MOTHERDUCK_DB = "olist"
RAW_SCHEMA = "raw"
OLIST_TABLES = {
    "orders": "olist_orders_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "product_category_translations": "product_category_name_translation.csv",
}

def load_kaggle_datasets() -> dict[str, pd.DataFrame]:
    """Loads all Olist tables from Kaggle into pandas          DataFrames.

    Returns:
        A dictionary mapping table name strings to pandas DataFrames.

    Raises:
        Exception: If all 3 attempts to load the dataset fail.
    """
    logger.info("Fetching data from Kaggle Olist dataset")

    datasets = {}
    for table_name, filename in OLIST_TABLES.items():
        for attempt in range(3):
            try:
                datasets[table_name] = kagglehub.dataset_load(
                    KaggleDatasetAdapter.PANDAS,
                    "olistbr/brazilian-ecommerce",
                    filename,
                )
                break
            except Exception as e:
                logger.error(
                    f"Attempt {attempt + 1}/3 failed: {e}"
                )
                if attempt < 2:
                    time.sleep(5)
                else:
                    logger.error(
                        "All attempts failed to return"
                    )
                    raise

    logger.info(
        f"{len(datasets)} datasets loaded successfully"
    )
    return datasets

def setup_schema(conn: duckdb.DuckDBPyConnection) -> None:
    """Creates the raw schema in MotherDuck if it doesn't exist.

    Args:
        conn: An active DuckDBPyConnection to the MotherDuck database.
    """
    logger.info(
        f"Setting up schema: {RAW_SCHEMA}"
    )

    for schema_attempt in range(3):
        try:
            conn.execute(
                f"CREATE DATABASE IF NOT EXISTS {MOTHERDUCK_DB}"
            )
            conn.execute(
                f"CREATE SCHEMA IF NOT EXISTS {MOTHERDUCK_DB}.{RAW_SCHEMA}"
            )
            logger.info(
                f"Schema {RAW_SCHEMA} is ready"
            )
            break
        except Exception as e:
            logger.error(
                f"Failed to create Schema: {e}. Attempt {schema_attempt + 1}/3"
            )
            if schema_attempt < 2:
                time.sleep(5)
            else:
                raise

def load_to_motherduck(
        conn: duckdb.DuckDBPyConnection,
        datasets: dict[str, pd.DataFrame]
) -> None:
    """Loads all Olist DataFrames into MotherDuck raw schema.

    Args:
        conn: An active DuckDBPyConnection to the MotherDuck database.
        datasets: A dictionary mapping table name strings to pandas DataFrames.
    """
    logger.info("Loading datasets into MotherDuck")

    for table_name, df in datasets.items():
        try:
            logger.info(f"Loading table {table_name}")
            conn.execute(
                f"CREATE OR REPLACE TABLE "
                f"{MOTHERDUCK_DB}.{RAW_SCHEMA}.{table_name} "
                f"AS SELECT * FROM df"
            )
            logger.info(
                f"Loaded {df.shape[0]} rows into {table_name}"
            )
        except Exception as e:
            logger.error(
                f"Failed to load {table_name}: {e}"
            )
            raise

    logger.info(
        "All datasets loaded successfully"
    )

def main() -> None:
    """Orchestrates the Kaggle to MotherDuck ingestion pipeline."""
    logger.info("Starting ingestion pipeline")

    datasets = load_kaggle_datasets()

    with duckdb.connect(f"md:{MOTHERDUCK_DB}") as conn:
        setup_schema(conn)
        load_to_motherduck(conn, datasets)

    logger.info("Ingestion pipeline completed successfully")


if __name__ == "__main__":
    main()
