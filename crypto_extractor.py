import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests


# Project directories
PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

# CoinGecko API configuration
API_URL = "https://api.coingecko.com/api/v3/coins/markets"

PARAMETERS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 100,
    "page": 1,
    "sparkline": False,
}

# Logging configuration
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


def extract_crypto_data():
    """Fetch cryptocurrency market data from CoinGecko."""

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Starting cryptocurrency data extraction.")

    try:
        response = requests.get(
            API_URL,
            params=PARAMETERS,
            timeout=30,
        )

        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list) or not data:
            logger.error("API returned an empty or unexpected response.")
            return None

        df = pd.DataFrame(data)

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
            logger.error("API response is missing columns: %s", missing_columns)
            return None

        df = df[required_columns].copy()

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_file = RAW_DATA_DIR / f"crypto_market_{timestamp}.csv"

        df.to_csv(output_file, index=False, encoding="utf-8")

        logger.info("Extraction completed successfully.")
        logger.info("Records extracted: %s", len(df))
        logger.info("Raw data saved to: %s", output_file)

        print("\nExtracted Cryptocurrency Data:")
        print(df.head(10).to_string(index=False).encode("utf-8", errors="replace").decode("utf-8"))

        return df

    except requests.exceptions.Timeout:
        logger.exception("API request timed out.")
    except requests.exceptions.HTTPError:
        logger.exception("API returned an unsuccessful HTTP status.")
    except requests.exceptions.RequestException:
        logger.exception("Unable to connect to the cryptocurrency API.")
    except (ValueError, OSError):
        logger.exception("Unable to process the API response or save the file.")

    return None


if __name__ == "__main__":
    extract_crypto_data()

