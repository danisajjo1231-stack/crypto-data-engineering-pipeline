USE CryptoMarketDW;
GO

SELECT TOP 20
    crypto_id,
    crypto_name,
    current_price,
    market_cap,
    price_change_percentage_24h,
    snapshot_at_utc
FROM warehouse.CryptoPriceHistory
ORDER BY market_cap DESC;
GO

SELECT
    CAST(snapshot_at_utc AS DATE) AS Snapshot_Date,
    COUNT(*) AS Total_Records,
    COUNT(DISTINCT crypto_id) AS Unique_Cryptocurrencies,
    AVG(current_price) AS Average_Crypto_Price,
    MAX(current_price) AS Highest_Crypto_Price,
    MIN(current_price) AS Lowest_Crypto_Price
FROM warehouse.CryptoPriceHistory
GROUP BY CAST(snapshot_at_utc AS DATE)
ORDER BY Snapshot_Date DESC;
GO

WITH PriceComparison AS (
    SELECT
        crypto_id,
        crypto_name,
        current_price,
        snapshot_at_utc,
        LAG(current_price) OVER (
            PARTITION BY crypto_id
            ORDER BY snapshot_at_utc
        ) AS Previous_Price
    FROM warehouse.CryptoPriceHistory
)
SELECT
    crypto_id,
    crypto_name,
    Previous_Price,
    current_price AS Latest_Price,
    current_price - Previous_Price AS Price_Change,
    snapshot_at_utc
FROM PriceComparison
WHERE Previous_Price IS NOT NULL
ORDER BY ABS(current_price - Previous_Price) DESC;
GO
CREATE SCHEMA analytics;
GO

CREATE OR ALTER VIEW analytics.vw_CryptoSnapshotSummary
AS
SELECT
    CAST(snapshot_at_utc AS DATE) AS Snapshot_Date,
    COUNT_BIG(*) AS Total_Records,
    COUNT(DISTINCT crypto_id) AS Unique_Cryptocurrencies,
    AVG(current_price) AS Average_Crypto_Price,
    MAX(current_price) AS Highest_Crypto_Price,
    MIN(current_price) AS Lowest_Crypto_Price
FROM warehouse.CryptoPriceHistory
GROUP BY CAST(snapshot_at_utc AS DATE);
GO

SELECT *
FROM analytics.vw_CryptoSnapshotSummary
ORDER BY Snapshot_Date DESC;
GO

CREATE OR ALTER VIEW analytics.vw_CryptoMarketOverview
AS
SELECT
    crypto_id,
    crypto_name,
    symbol,
    current_price,
    market_cap,
    total_volume,
    price_change_percentage_24h,
    last_updated
FROM staging.crypto_market;
GO

SELECT TOP 20
    crypto_name,
    symbol,
    current_price,
    market_cap,
    total_volume,
    price_change_percentage_24h
FROM analytics.vw_CryptoMarketOverview
ORDER BY market_cap DESC;
GO

CREATE OR ALTER VIEW analytics.vw_CryptoPerformance
AS
SELECT
    crypto_id,
    crypto_name,
    symbol,
    current_price,
    market_cap,
    total_volume,
    price_change_percentage_24h,
    CASE
        WHEN price_change_percentage_24h > 0
            THEN 'Positive'
        WHEN price_change_percentage_24h < 0
            THEN 'Negative'
        WHEN price_change_percentage_24h = 0
            THEN 'No Change'
        ELSE 'Unavailable'
    END AS Performance_Status
FROM staging.crypto_market;
GO

SELECT
    Performance_Status,
    COUNT(*) AS Total_Cryptocurrencies
FROM analytics.vw_CryptoPerformance
GROUP BY Performance_Status
ORDER BY Total_Cryptocurrencies DESC;
GO