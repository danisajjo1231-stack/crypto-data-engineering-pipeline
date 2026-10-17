import logging
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRANSFORMED_DATA_DIR = PROJECT_ROOT / "data" / "transformed"
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


SERVER = "localhost"
DATABASE = "CryptoMarketDW"
ODBC_DRIVER = "ODBC Driver 18 for SQL Server"
CONNECTION_URL = URL.create(
    "mssql+pyodbc",
    query={
        "odbc_connect": (
            f"DRIVER={{{ODBC_DRIVER}}};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            "Trusted_Connection=yes;"
            "Encrypt=no;"
        )
    },
)


def load_crypto_data(input_file=None):
    """
    Validate transformed cryptocurrency data.
    Insert new cryptocurrency IDs into staging.
    Update changed records in staging.
    Save a consistent historical snapshot for each run.
    """

    engine = None

    # --------------------------------------------------
    # 4.1 FIND LATEST TRANSFORMED CSV
    # --------------------------------------------------

    if input_file is None:
        input_files = list(
            TRANSFORMED_DATA_DIR.glob(
                "crypto_transformed_*.csv"
            )
        )

        if not input_files:
            logger.error(
                "No transformed cryptocurrency CSV file found."
            )
            return False

        input_file = max(
            input_files,
            key=lambda file: file.stat().st_mtime,
        )

    input_file = Path(input_file)

    if not input_file.is_file():
        logger.error(
            "Input file does not exist: %s",
            input_file,
        )
        return False

    logger.info(
        "Reading transformed file: %s",
        input_file,
    )

    # --------------------------------------------------
    # 4.2 READ CSV
    # --------------------------------------------------

    try:
        df = pd.read_csv(input_file)

    except (
        OSError,
        pd.errors.ParserError,
        UnicodeError,
    ):
        logger.exception(
            "Unable to read transformed CSV file."
        )
        return False

    if df.empty:
        logger.error(
            "The transformed CSV file is empty."
        )
        return False

    # --------------------------------------------------
    # 4.3 CHECK REQUIRED COLUMNS
    # --------------------------------------------------

    required_columns = [
        "id",
        "symbol",
        "name",
        "current_price",
        "market_cap",
        "total_volume",
        "price_change_percentage_24h",
        "last_updated",
        "processed_at_utc",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        logger.error(
            "Required columns are missing: %s",
            missing_columns,
        )
        return False

    df = df[required_columns].copy()

    # --------------------------------------------------
    # 4.4 CLEAN TEXT COLUMNS
    # --------------------------------------------------

    for column in ["id", "symbol", "name"]:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

        invalid_text = (
            df[column].isna()
            | df[column].eq("")
        )

        if invalid_text.any():
            logger.error(
                "Missing or empty values found in %s.",
                column,
            )
            return False

    text_length_limits = {
        "id": 150,
        "symbol": 15,
        "name": 100,
    }

    for column, maximum_length in text_length_limits.items():
        too_long = (
            df[column]
            .str.len()
            .gt(maximum_length)
            .fillna(False)
        )

        if too_long.any():
            logger.error(
                "Values exceed VARCHAR(%s) limit in %s.",
                maximum_length,
                column,
            )

            print(
                df.loc[too_long, [column]].to_string(
                    index=False
                )
            )

            return False

    # --------------------------------------------------
    # 4.5 RENAME COLUMNS
    # --------------------------------------------------

    df.rename(
        columns={
            "id": "crypto_id",
            "name": "crypto_name",
        },
        inplace=True,
    )

    # --------------------------------------------------
    # 4.6 VALIDATE NUMERIC COLUMNS
    # --------------------------------------------------

    numeric_columns = [
        "current_price",
        "market_cap",
        "total_volume",
        "price_change_percentage_24h",
    ]

    for column in numeric_columns:
        original_values = df[column].copy()

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

        invalid_values = (
            original_values.notna()
            & df[column].isna()
        )

        if invalid_values.any():
            logger.error(
                "Invalid numeric values found in %s.",
                column,
            )
            return False

        values = df[column].dropna()

        if not values.map(
            lambda value: abs(value) != float("inf")
        ).all():
            logger.error(
                "Infinite numeric value found in %s.",
                column,
            )
            return False

    required_numeric_columns = [
        "current_price",
        "market_cap",
        "total_volume",
    ]

    if df[required_numeric_columns].isna().any().any():
        logger.error(
            "NULL values found in required numeric columns."
        )
        return False

    for column in [
        "current_price",
        "market_cap",
        "total_volume",
    ]:
        if (df[column] < 0).any():
            logger.error(
                "Negative values found in %s.",
                column,
            )
            return False

    # --------------------------------------------------
    # 4.7 CHECK DECIMAL CAPACITY
    # --------------------------------------------------

    decimal_limits = {
        "current_price": (28, 8),
        "market_cap": (28, 2),
        "total_volume": (28, 2),
        "price_change_percentage_24h": (12, 6),
    }

    for column, (precision, scale) in decimal_limits.items():
        values = df[column].dropna()
        maximum_value = 10 ** (precision - scale)

        if (values.abs() >= maximum_value).any():
            logger.error(
                "Value exceeds DECIMAL(%s,%s) capacity "
                "in column %s.",
                precision,
                scale,
                column,
            )
            return False

    # --------------------------------------------------
    # 4.8 CONVERT TIMESTAMPS
    # --------------------------------------------------

    timestamp_columns = [
        "last_updated",
        "processed_at_utc",
    ]

    for column in timestamp_columns:
        df[column] = (
            pd.to_datetime(
                df[column],
                errors="coerce",
                utc=True,
            )
            .dt.tz_localize(None)
        )

    if df[timestamp_columns].isna().any().any():
        logger.error(
            "Invalid or missing timestamp found."
        )
        return False

    # --------------------------------------------------
    # 4.9 CHECK DUPLICATE SOURCE IDS
    # --------------------------------------------------

    if df["crypto_id"].duplicated().any():
        logger.error(
            "Duplicate cryptocurrency IDs found."
        )
        return False

    logger.info(
        "Source validation successful: %s records.",
        len(df),
    )

    # --------------------------------------------------
    # 5. CONNECT TO SQL SERVER
    # --------------------------------------------------

    engine = create_engine(
        CONNECTION_URL,
        fast_executemany=False,
    )

    try:
        with engine.begin() as connection:

            # ------------------------------------------
            # 5.1 VERIFY STAGING TABLE
            # ------------------------------------------

            table_exists = connection.execute(
                text(
                    """
                    SELECT CASE
                        WHEN OBJECT_ID(
                            'staging.crypto_market',
                            'U'
                        ) IS NOT NULL
                        THEN 1
                        ELSE 0
                    END;
                    """
                )
            ).scalar_one()

            if not table_exists:
                raise RuntimeError(
                    "Table staging.crypto_market does not exist."
                )

            # ------------------------------------------
            # 5.2 VERIFY HISTORICAL TABLE
            # ------------------------------------------

            history_table_exists = connection.execute(
                text(
                    """
                    SELECT CASE
                        WHEN OBJECT_ID(
                            'warehouse.CryptoPriceHistory',
                            'U'
                        ) IS NOT NULL
                        THEN 1
                        ELSE 0
                    END;
                    """
                )
            ).scalar_one()

            if not history_table_exists:
                raise RuntimeError(
                    "Table warehouse.CryptoPriceHistory "
                    "does not exist."
                )

            # ------------------------------------------
            # 5.3 CREATE TEMPORARY TABLE
            # ------------------------------------------

            connection.execute(
                text(
                    """
                    DROP TABLE IF EXISTS #crypto_market_incoming;

                    CREATE TABLE #crypto_market_incoming (
                        crypto_id VARCHAR(150) NOT NULL PRIMARY KEY,
                        symbol VARCHAR(15) NOT NULL,
                        crypto_name VARCHAR(100) NOT NULL,
                        current_price DECIMAL(28,8) NOT NULL,
                        market_cap DECIMAL(28,2) NOT NULL,
                        total_volume DECIMAL(28,2) NOT NULL,
                        price_change_percentage_24h DECIMAL(12,6) NULL,
                        last_updated DATETIME2(0) NOT NULL,
                        processed_at_utc DATETIME2(0) NOT NULL
                    );
                    """
                )
            )

            # ------------------------------------------
            # 5.4 LOAD DATA INTO TEMPORARY TABLE
            # ------------------------------------------

            logger.info(
                "Loading %s records into temporary table.",
                len(df),
            )

            df.to_sql(
                name="#crypto_market_incoming",
                con=connection,
                if_exists="append",
                index=False,
                chunksize=100,
            )

            # ------------------------------------------
            # 5.5 COUNT MATCHING IDS
            # ------------------------------------------

            existing_matches = connection.execute(
                text(
                    """
                    SELECT COUNT_BIG(*)
                    FROM #crypto_market_incoming AS source
                    INNER JOIN staging.crypto_market AS target
                        ON target.crypto_id = source.crypto_id;
                    """
                )
            ).scalar_one()

            # ------------------------------------------
            # 5.6 UPDATE CHANGED RECORDS
            # ------------------------------------------

            update_result = connection.execute(
                text(
                    """
                    UPDATE target
                    SET
                        target.symbol = source.symbol,
                        target.crypto_name = source.crypto_name,
                        target.current_price = source.current_price,
                        target.market_cap = source.market_cap,
                        target.total_volume = source.total_volume,
                        target.price_change_percentage_24h =
                            source.price_change_percentage_24h,
                        target.last_updated = source.last_updated,
                        target.processed_at_utc =
                            source.processed_at_utc
                    FROM staging.crypto_market AS target
                    INNER JOIN #crypto_market_incoming AS source
                        ON target.crypto_id = source.crypto_id
                    WHERE
                        target.symbol <> source.symbol
                        OR target.crypto_name <> source.crypto_name
                        OR target.current_price <> source.current_price
                        OR target.market_cap <> source.market_cap
                        OR target.total_volume <> source.total_volume
                        OR (
                            target.price_change_percentage_24h
                            <> source.price_change_percentage_24h
                        )
                        OR (
                            target.price_change_percentage_24h IS NULL
                            AND source.price_change_percentage_24h IS NOT NULL
                        )
                        OR (
                            target.price_change_percentage_24h IS NOT NULL
                            AND source.price_change_percentage_24h IS NULL
                        )
                        OR target.last_updated <> source.last_updated;
                    """
                )
            )

            updated_records = max(
                update_result.rowcount or 0,
                0,
            )

            # ------------------------------------------
            # 5.7 INSERT NEW STAGING RECORDS
            # ------------------------------------------

            insert_result = connection.execute(
                text(
                    """
                    INSERT INTO staging.crypto_market (
                        crypto_id,
                        symbol,
                        crypto_name,
                        current_price,
                        market_cap,
                        total_volume,
                        price_change_percentage_24h,
                        last_updated,
                        processed_at_utc
                    )
                    SELECT
                        source.crypto_id,
                        source.symbol,
                        source.crypto_name,
                        source.current_price,
                        source.market_cap,
                        source.total_volume,
                        source.price_change_percentage_24h,
                        source.last_updated,
                        source.processed_at_utc
                    FROM #crypto_market_incoming AS source
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM staging.crypto_market AS target
                        WHERE target.crypto_id = source.crypto_id
                    );
                    """
                )
            )

            inserted_records = max(
                insert_result.rowcount or 0,
                0,
            )

            # ------------------------------------------
            # 5.8 SAVE CONSISTENT HISTORICAL SNAPSHOT
            # ------------------------------------------

            logger.info(
                "Saving historical snapshots for %s records.",
                len(df),
            )

            history_result = connection.execute(
                text(
                    """
                    DECLARE @SnapshotTime DATETIME2(7) =
                        SYSUTCDATETIME();

                    INSERT INTO warehouse.CryptoPriceHistory (
                        crypto_id,
                        symbol,
                        crypto_name,
                        current_price,
                        market_cap,
                        total_volume,
                        price_change_percentage_24h,
                        last_updated,
                        snapshot_at_utc
                    )
                    SELECT
                        crypto_id,
                        symbol,
                        crypto_name,
                        current_price,
                        market_cap,
                        total_volume,
                        price_change_percentage_24h,
                        last_updated,
                        @SnapshotTime
                    FROM #crypto_market_incoming;
                    """
                )
            )

            snapshot_records = max(
                history_result.rowcount or 0,
                0,
            )

            logger.info(
                "Historical snapshots saved: %s records.",
                snapshot_records,
            )

            # ------------------------------------------
            # 5.9 VERIFY STAGING TABLE
            # ------------------------------------------

            total_rows = connection.execute(
                text(
                    """
                    SELECT COUNT_BIG(*)
                    FROM staging.crypto_market;
                    """
                )
            ).scalar_one()

            duplicate_count = connection.execute(
                text(
                    """
                    SELECT COUNT_BIG(*)
                    FROM (
                        SELECT crypto_id
                        FROM staging.crypto_market
                        GROUP BY crypto_id
                        HAVING COUNT_BIG(*) > 1
                    ) AS duplicates;
                    """
                )
            ).scalar_one()

            if duplicate_count:
                raise RuntimeError(
                    "Duplicate crypto IDs detected in target table."
                )

            logger.info(
                "Upsert completed successfully."
            )

        # ----------------------------------------------
        # 6. LOAD SUMMARY
        # ----------------------------------------------

        print("\n" + "=" * 45)
        print("CRYPTO DATA LOAD SUMMARY")
        print("=" * 45)
        print(f"Source file: {input_file}")
        print(f"Source records: {len(df)}")
        print(f"Existing IDs matched: {existing_matches}")
        print(f"Records updated: {updated_records}")
        print(f"Records inserted: {inserted_records}")
        print(f"Historical snapshots saved: {snapshot_records}")
        print(f"Total target records: {total_rows}")
        print(f"Duplicate ID groups: {duplicate_count}")
        print("Status: SUCCESS")
        print("=" * 45)

        return True

    except Exception:
        logger.exception(
            "SQL Server data load failed."
        )
        return False

    finally:
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    success = load_crypto_data()
    if not success:
        raise SystemExit(1)

