import logging
from pathlib import Path
import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
TRANSFORMED_DATA_DIR = PROJECT_ROOT / "data" / "transformed"
LOG_DIR = PROJECT_ROOT / "logs"

LOG_DIR.mkdir(parents=True, exist_ok=True)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            LOG_DIR / "pipeline.log",
            encoding="utf-8",
        ),
    ],
)

logger = logging.getLogger(__name__)


def transform_crypto_data(input_file=None):
    """Transform validated cryptocurrency data into a consistent format."""

    TRANSFORMED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Find the latest validated CSV if no file is provided.
    if input_file is None:
        input_files = sorted(
            PROCESSED_DATA_DIR.glob("crypto_validated_*.csv"),
            key=lambda file: file.stat().st_mtime,
        )

        if not input_files:
            logger.error("No validated cryptocurrency CSV file found.")
            return None

        input_file = input_files[-1]

    logger.info("Reading validated data from: %s", input_file)

    try:
        df = pd.read_csv(input_file)
    except (OSError, pd.errors.ParserError, UnicodeError):
        logger.exception("Unable to read the validated CSV file.")
        return None

    if df.empty:
        logger.error("The validated CSV file contains no records.")
        return None

    required_columns = [
        "id",
        "symbol",
        "name",
        "current_price",
        "market_cap",
        "total_volume",
        "price_change_percentage_24h",
        "last_updated",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        logger.error("Required columns are missing: %s", missing_columns)
        return None

    # Keep the expected columns and avoid modifying the original DataFrame.
    df = df[required_columns].copy()

    # Standardize text values.
    for column in ["id", "symbol", "name"]:
        df[column] = df[column].astype("string").str.strip()

    df["id"] = df["id"].str.lower()
    df["symbol"] = df["symbol"].str.upper()

    # Convert numeric columns into numeric data types.
    numeric_columns = [
        "current_price",
        "market_cap",
        "total_volume",
        "price_change_percentage_24h",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Convert the timestamp into a consistent UTC datetime format.
    df["last_updated"] = pd.to_datetime(
        df["last_updated"],
        errors="coerce",
        utc=True,
    )

    # Stop if conversion has introduced invalid required values.
    required_value_columns = [
        "id",
        "symbol",
        "name",
        "current_price",
        "market_cap",
        "total_volume",
        "last_updated",
    ]

    if df[required_value_columns].isna().any().any():
        logger.error(
            "Transformation produced missing required values. "
            "Please review the validated input data."
        )
        return None

    if (
        df["current_price"].le(0).any()
        or df["market_cap"].lt(0).any()
        or df["total_volume"].lt(0).any()
    ):
        logger.error("Transformation detected invalid numeric values.")
        return None

    # Add a pipeline processing timestamp in UTC.
    df["processed_at_utc"] = pd.Timestamp.now(tz="UTC")

    # Save transformed data.
    file_tag = Path(input_file).stem.replace("crypto_validated_", "")

    output_file = (
        TRANSFORMED_DATA_DIR / f"crypto_transformed_{file_tag}.csv"
    )

    # Save timestamps in a consistent ISO 8601 format.
    df["last_updated"] = df["last_updated"].dt.strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    df["processed_at_utc"] = df["processed_at_utc"].dt.strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    df.to_csv(output_file, index=False, encoding="utf-8")

    logger.info("Transformation completed successfully.")
    logger.info("Records transformed: %s", len(df))
    logger.info("Transformed data saved to: %s", output_file)

    print("\n--- DATA TRANSFORMATION SUMMARY ---")
    print(f"Records transformed: {len(df)}")
    print(f"Output file: {output_file}")
    print("\nTransformed data:")
    print(df.head(10).to_string(index=False).encode("utf-8", errors="replace").decode("utf-8"))

    return df


if __name__ == "__main__":
    transform_crypto_data()
