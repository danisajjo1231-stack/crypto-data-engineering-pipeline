import logging
import sys
from pathlib import Path
# Fix 3: Ensure consistent import paths (assuming all are in src or root)
from crypto_extractor import extract_crypto_data
from src.crypto_validator import validate_crypto_data
from src.crypto_transformer import transform_crypto_data
from src.crypto_loader import load_crypto_data

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")



# PROJECT CONFIGURATION
# Fix 1: Added double underscores to __file__
PROJECT_ROOT = Path(__file__).resolve().parent
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
logger = logging.getLogger("crypto_pipeline")


# MAIN PIPELINE
def run_pipeline():
    """Run extraction, validation, transformation, and loading."""
    print("\n" + "=" * 55)
    print("CRYPTO DATA ENGINEERING PIPELINE")
    print("=" * 55)

    try:
        # STEP 1: EXTRACT
        logger.info("STEP 1: Extracting cryptocurrency data.")
        extracted_data = extract_crypto_data()

        if extracted_data is None or extracted_data.empty:
            raise RuntimeError("Extraction failed or returned no records.")

        logger.info(
            "Extraction successful: %s records.",
            len(extracted_data),
        )

        # STEP 2: VALIDATE (Passing extracted_data)
        logger.info("STEP 2: Validating raw data.")
        validated_data = validate_crypto_data()

        if validated_data is None or (isinstance(validated_data, bool) and not validated_data):
            raise RuntimeError("Data validation failed.")

        logger.info("Validation function completed.")

        # STEP 3: TRANSFORM (Passing validated_data)
        logger.info("STEP 3: Transforming validated data.")
        transformed_data = transform_crypto_data()

        if transformed_data is None or (isinstance(transformed_data, bool) and not transformed_data):
            raise RuntimeError("Data transformation failed.")

        logger.info("Transformation function completed.")

        # STEP 4: LOAD (Passing transformed_data)
        logger.info("STEP 4: Loading data into SQL Server.")
        loading_result = load_crypto_data()

        if loading_result is False:
            raise RuntimeError("SQL Server loading failed.")

        logger.info("Loading function completed.")

        # SUCCESS
        print("\n" + "=" * 55)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 55)

        logger.info("Pipeline execution finished.")
        return True

    except Exception:
        logger.exception("PIPELINE FAILED.")

        print("\nPIPELINE FAILED.")
        print("Check the error details above.")
        print("Log file: logs/pipeline.log")

        return False


# PROGRAM ENTRY POINT
# Fix 1: Added double underscores to __name__ and "__main__"
if __name__ == "__main__":
    success = run_pipeline()
    if not success:
        sys.exit(1)





