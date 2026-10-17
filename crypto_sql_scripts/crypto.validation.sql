USE CryptoMarketDW;
GO

-- 1. Total rows
SELECT
    COUNT(*) AS Total_Rows,
    COUNT(DISTINCT crypto_id) AS Unique_Crypto_IDs
FROM staging.crypto_market;
GO

-- 2. Duplicate crypto IDs
SELECT
    crypto_id,
    COUNT(*) AS Duplicate_Count
FROM staging.crypto_market
GROUP BY crypto_id
HAVING COUNT(*) > 1;
GO

-- 3. Missing important values
SELECT
    SUM(CASE WHEN crypto_id IS NULL THEN 1 ELSE 0 END)
        AS Missing_Crypto_ID,
    SUM(CASE WHEN crypto_name IS NULL THEN 1 ELSE 0 END)
        AS Missing_Crypto_Name,
    SUM(CASE WHEN current_price IS NULL THEN 1 ELSE 0 END)
        AS Missing_Price,
    SUM(CASE WHEN market_cap IS NULL THEN 1 ELSE 0 END)
        AS Missing_Market_Cap
FROM staging.crypto_market;
GO

USE CryptoMarketDW;
GO

SELECT
    COUNT(*) AS Total_Historical_Records,
    COUNT(DISTINCT crypto_id) AS Unique_Cryptocurrencies,
    COUNT(DISTINCT snapshot_at_utc) AS Unique_Snapshot_Times,
    MIN(snapshot_at_utc) AS First_Snapshot,
    MAX(snapshot_at_utc) AS Latest_Snapshot
FROM warehouse.CryptoPriceHistory;
GO


SELECT
    s.crypto_id,
    s.crypto_name,
    s.symbol
FROM staging.crypto_market AS s
LEFT JOIN (
    SELECT DISTINCT crypto_id
    FROM warehouse.CryptoPriceHistory
) AS h
    ON s.crypto_id = h.crypto_id
WHERE h.crypto_id IS NULL;
GO


SELECT *
FROM staging.crypto_market
WHERE crypto_id = 'pyth-network';
GO

SELECT *
FROM warehouse.CryptoPriceHistory
WHERE crypto_id = 'pyth-network';
GO

SELECT
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'warehouse'
  AND TABLE_NAME = 'CryptoPriceHistory'
ORDER BY ORDINAL_POSITION;
GO

SELECT
    COUNT(*) AS Total_Historical_Records,
    COUNT(DISTINCT crypto_id) AS Unique_Cryptocurrencies,
    COUNT(DISTINCT snapshot_at_utc) AS Unique_Snapshot_Times,
    MIN(snapshot_at_utc) AS First_Snapshot,
    MAX(snapshot_at_utc) AS Latest_Snapshot
FROM warehouse.CryptoPriceHistory;
GO

SELECT
    crypto_id,
    crypto_name,
    symbol,
    snapshot_at_utc
FROM warehouse.CryptoPriceHistory
WHERE crypto_id = 'pyth-network'
ORDER BY snapshot_at_utc DESC;
GO

USE CryptoMarketDW;
GO

SELECT TOP 10 *
FROM warehouse.CryptoPriceHistory
ORDER BY Snapshot_ID DESC;
GO



SELECT
    COUNT(*) AS Total_Records,
    COUNT(DISTINCT snapshot_at_utc) AS Snapshot_Count,
    MAX(snapshot_at_utc) AS Latest_Snapshot
FROM warehouse.CryptoPriceHistory;
GO

USE CryptoMarketDW;
GO

INSERT INTO warehouse.CryptoPriceHistory (
    crypto_id,
    symbol,
    crypto_name,
    current_price,
    market_cap,
    total_volume,
    price_change_percentage_24h,
    last_updated
)
SELECT
    s.crypto_id,
    s.symbol,
    s.crypto_name,
    s.current_price,
    s.market_cap,
    s.total_volume,
    s.price_change_percentage_24h,
    s.last_updated
FROM staging.crypto_market AS s
WHERE NOT EXISTS (
    SELECT 1
    FROM warehouse.CryptoPriceHistory AS h
    WHERE h.crypto_id = s.crypto_id
      AND h.snapshot_at_utc = (
          SELECT MAX(snapshot_at_utc)
          FROM warehouse.CryptoPriceHistory
      )
);
GO


USE CryptoMarketDW;
GO

SELECT
    COUNT(*) AS Total_Historical_Records,
    COUNT(DISTINCT crypto_id) AS Unique_Cryptocurrencies,
    COUNT(DISTINCT snapshot_at_utc) AS Unique_Snapshot_Times
FROM warehouse.CryptoPriceHistory;
GO

SELECT
    crypto_id,
    crypto_name,
    symbol,
    current_price,
    snapshot_at_utc
FROM warehouse.CryptoPriceHistory
WHERE crypto_id = 'pyth-network';
GO

SELECT
    snapshot_at_utc,
    COUNT(*) AS Total_Coins
FROM warehouse.CryptoPriceHistory
GROUP BY snapshot_at_utc
ORDER BY snapshot_at_utc;
GO


UPDATE warehouse.CryptoPriceHistory
SET snapshot_at_utc = '2026-10-14T20:20:59.7503102'
WHERE crypto_id = 'pyth-network'
  AND snapshot_at_utc = '2026-10-14T20:27:07.8202617';
GO

SELECT
    snapshot_at_utc,
    COUNT(*) AS Total_Coins
FROM warehouse.CryptoPriceHistory
GROUP BY snapshot_at_utc
ORDER BY snapshot_at_utc;
GO

USE CryptoMarketDW;
GO

SELECT
    COUNT(*) AS Total_Records,
    COUNT(DISTINCT crypto_id) AS Unique_Cryptocurrencies,
    COUNT(DISTINCT snapshot_at_utc) AS Total_Snapshots
FROM warehouse.CryptoPriceHistory;
GO




USE CryptoMarketDW;
GO

IF OBJECT_ID('staging.crypto_market', 'U') IS NULL
BEGIN
    CREATE TABLE staging.crypto_market
    (
        crypto_id VARCHAR(50) NOT NULL,
        symbol VARCHAR(15) NOT NULL,
        crypto_name VARCHAR(100) NOT NULL,

        current_price DECIMAL(28, 8) NOT NULL,
        market_cap DECIMAL(28, 2) NOT NULL,
        total_volume DECIMAL(28, 2) NOT NULL,
        price_change_percentage_24h DECIMAL(12, 6) NULL,

        last_updated DATETIME2(0) NOT NULL,
        processed_at_utc DATETIME2(0) NOT NULL,

        CONSTRAINT PK_staging_crypto_market
            PRIMARY KEY (crypto_id)
    );
END;
GO

SELECT
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'staging'
  AND TABLE_NAME = 'crypto_market'
ORDER BY ORDINAL_POSITION;
GO

USE CryptoMarketDW;
GO

SELECT *
FROM staging.crypto_market;
GO

SELECT COUNT(*) AS Total_Cryptocurrencies
FROM staging.crypto_market;
GO

USE CryptoMarketDW;
GO

SELECT
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'staging'
  AND TABLE_NAME = 'crypto_market'
  AND COLUMN_NAME IN ('crypto_id', 'symbol', 'crypto_name');

ALTER TABLE staging.crypto_market
ALTER COLUMN crypto_id VARCHAR(150) NOT NULL;


SELECT COUNT(*) AS Total_Crypto_Records
FROM staging.crypto_market;

SELECT TOP 10 *
FROM staging.crypto_market;

USE CryptoMarketDW;
GO

-- Total records
SELECT COUNT(*) AS Total_Records
FROM staging.crypto_market;

-- Duplicate IDs
SELECT
    crypto_id,
    COUNT(*) AS Duplicate_Count
FROM staging.crypto_market
GROUP BY crypto_id
HAVING COUNT(*) > 1;

-- Latest cryptocurrency records
SELECT TOP 10
    crypto_id,
    symbol,
    crypto_name,
    current_price,
    market_cap,
    last_updated,
    processed_at_utc
FROM staging.crypto_market
ORDER BY processed_at_utc DESC;



SELECT TOP 5
    crypto_id,
    crypto_name,
    current_price,
    processed_at_utc
FROM staging.crypto_market
ORDER BY market_cap DESC;






SELECT
KU.COLUMN_NAME,
TC.CONSTRAINT_TYPE,
TC.CONSTRAINT_NAME
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS TC
INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS KU
ON TC.CONSTRAINT_NAME = KU.CONSTRAINT_NAME
AND TC.TABLE_SCHEMA = KU.TABLE_SCHEMA
AND TC.TABLE_NAME = KU.TABLE_NAME
WHERE TC.TABLE_SCHEMA = 'staging'
AND TC.TABLE_NAME = 'crypto_market'
AND TC.CONSTRAINT_TYPE = 'PRIMARY KEY';
