import logging
from pathlib import Path
import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
REJECTED_DATA_DIR = PROJECT_ROOT / "data" / "rejected"

# Logging configuration
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

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


def validate_crypto_data(input_file=None):
    """Validate raw cryptocurrency data and separate valid and rejected records."""

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    REJECTED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Find the latest raw CSV file if no file is provided.
    if input_file is None:
        raw_files = sorted(
            RAW_DATA_DIR.glob("crypto_market_*.csv"),
            key=lambda file: file.stat().st_mtime,
        )

        if not raw_files:
            logger.error("No raw cryptocurrency CSV file found.")
            return None, None

        input_file = raw_files[-1]

    logger.info("Reading raw data from: %s", input_file)

    try:
        df = pd.read_csv(input_file)
    except (OSError, pd.errors.ParserError, UnicodeError):
        logger.exception("Unable to read the raw CSV file.")
        return None, None

    if df.empty:
        logger.error("The input CSV file contains no records.")
        return None, None

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
        return None, None

    # Keep only the columns required by our pipeline.
    df = df[required_columns].copy()

    # Remove duplicate records using cryptocurrency ID.
    duplicate_mask = df.duplicated(subset=["id"], keep="first")
    duplicate_count = int(duplicate_mask.sum())

    duplicate_rows = df.loc[duplicate_mask].copy()
    duplicate_rows["rejection_reason"] = "Duplicate cryptocurrency ID"

    df = df.loc[~duplicate_mask].copy()

    # Convert numeric columns safely.
    numeric_columns = [
        "current_price",
        "market_cap",
        "total_volume",
        "price_change_percentage_24h",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Check mandatory fields.
    required_value_columns = [
        "id",
        "symbol",
        "name",
        "current_price",
        "market_cap",
        "total_volume",
        "last_updated",
    ]

    missing_value_mask = df[required_value_columns].isna().any(axis=1)

    # Reject blank text values.
    for column in ["id", "symbol", "name", "last_updated"]:
        blank_mask = (
            df[column]
            .astype("string")
            .str.strip()
            .eq("")
            .fillna(False)
        )
        missing_value_mask = missing_value_mask | blank_mask

    # Reject invalid numeric values.
    invalid_numeric_mask = (
        df["current_price"].le(0)
        | df["market_cap"].lt(0)
        | df["total_volume"].lt(0)
    ).fillna(True)

    # Reject invalid or unparseable timestamps.
    parsed_timestamps = pd.to_datetime(
        df["last_updated"],
        errors="coerce",
        utc=True,
    )
    invalid_timestamp_mask = parsed_timestamps.isna()

    # Build rejection reasons for each record.
    rejection_reasons = []

    for index in df.index:
        reasons = []

        if missing_value_mask.loc[index]:
            reasons.append("Missing required value")

        if invalid_numeric_mask.loc[index]:
            reasons.append("Invalid price, market cap, or volume")

        if invalid_timestamp_mask.loc[index]:
            reasons.append("Invalid last_updated timestamp")

        rejection_reasons.append((index, reasons))

    reasons_by_index = {
        index: "; ".join(reasons)
        for index, reasons in rejection_reasons
        if reasons
    }

    rejected_mask = df.index.isin(reasons_by_index)

    rejected_rows = df.loc[rejected_mask].copy()
    rejected_rows["rejection_reason"] = [
        reasons_by_index[index]
        for index in rejected_rows.index
    ]

    valid_rows = df.loc[~rejected_mask].copy()

    # Combine duplicate records with other rejected records.
    rejected_columns = required_columns + ["rejection_reason"]

    rejected_rows = pd.concat(
        [
            rejected_rows.reindex(columns=rejected_columns),
            duplicate_rows.reindex(columns=rejected_columns),
        ],
        ignore_index=True,
    )

    # Generate output filenames based on the input filename.
    file_tag = Path(input_file).stem.replace("crypto_market_", "")

    processed_file = PROCESSED_DATA_DIR / f"crypto_validated_{file_tag}.csv"
    rejected_file = REJECTED_DATA_DIR / f"crypto_rejected_{file_tag}.csv"

    valid_rows.to_csv(processed_file, index=False)
    rejected_rows.to_csv(rejected_file, index=False)

    # Print validation summary.
    logger.info("Validation completed.")
    logger.info("Input records: %s", len(pd.read_csv(input_file)))
    logger.info("Duplicate records: %s", duplicate_count)
    logger.info("Valid records: %s", len(valid_rows))
    logger.info("Rejected records: %s", len(rejected_rows))
    logger.info("Validated data saved to: %s", processed_file)
    logger.info("Rejected data saved to: %s", rejected_file)

    print("\n--- DATA VALIDATION SUMMARY ---")
    print(f"Input file: {input_file}")
    print(f"Valid records: {len(valid_rows)}")
    print(f"Rejected records: {len(rejected_rows)}")
    print(f"Duplicate records: {duplicate_count}")
    print(f"Validated file: {processed_file}")
    print(f"Rejected file: {rejected_file}")

    return valid_rows, rejected_rows


if __name__ == "__main__":
    validate_crypto_data()

