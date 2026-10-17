USE CryptoMarketDW;
GO

-- 1. Database ke tamam tables aur views
SELECT
    s.name AS SchemaName,
    o.name AS ObjectName,
    o.type_desc AS ObjectType
FROM sys.objects AS o
INNER JOIN sys.schemas AS s
    ON o.schema_id = s.schema_id
WHERE o.type IN ('U', 'V')
ORDER BY s.name, o.name;


-- 2. Tables ke columns aur data types
SELECT
    s.name AS SchemaName,
    t.name AS TableName,
    c.column_id AS ColumnNumber,
    c.name AS ColumnName,
    TYPE_NAME(c.user_type_id) AS DataType,
    c.is_nullable AS IsNullable
FROM sys.tables AS t
INNER JOIN sys.schemas AS s
    ON t.schema_id = s.schema_id
INNER JOIN sys.columns AS c
    ON t.object_id = c.object_id
ORDER BY s.name, t.name, c.column_id;


-- 3. Har table mein records ki tadaad
SELECT
    s.name AS SchemaName,
    t.name AS TableName,
    SUM(p.rows) AS TotalRecords
FROM sys.tables AS t
INNER JOIN sys.schemas AS s
    ON t.schema_id = s.schema_id
INNER JOIN sys.partitions AS p
    ON t.object_id = p.object_id
WHERE p.index_id IN (0, 1)
GROUP BY s.name, t.name
ORDER BY s.name, t.name;



-- Create warehouse schema if it does not exist
IF NOT EXISTS (
    SELECT 1
    FROM sys.schemas
    WHERE name = 'warehouse'
)
BEGIN
    EXEC('CREATE SCHEMA warehouse');
END;
GO

-- Create historical price snapshot table
IF OBJECT_ID(
    'warehouse.CryptoPriceHistory',
    'U'
) IS NULL
BEGIN
    CREATE TABLE warehouse.CryptoPriceHistory
    (
        Snapshot_ID BIGINT IDENTITY(1,1) PRIMARY KEY,
        crypto_id VARCHAR(100) NOT NULL,
        symbol VARCHAR(30) NOT NULL,
        crypto_name VARCHAR(200) NOT NULL,
        current_price DECIMAL(28,10) NOT NULL,
        market_cap DECIMAL(28,2) NOT NULL,
        total_volume DECIMAL(28,2) NOT NULL,
        price_change_percentage_24h DECIMAL(18,8) NULL,
        last_updated DATETIME2 NOT NULL,
        snapshot_at_utc DATETIME2 NOT NULL
            DEFAULT SYSUTCDATETIME()
    );
END;
GO

-- Verify table creation
SELECT
    s.name AS SchemaName,
    t.name AS TableName
FROM sys.tables AS t
INNER JOIN sys.schemas AS s
    ON t.schema_id = s.schema_id
WHERE s.name = 'warehouse'
  AND t.name = 'CryptoPriceHistory';
GO


ALTER TABLE warehouse.CryptoPriceHistory
ALTER COLUMN crypto_id VARCHAR(150) NOT NULL;
GO


SELECT
    COUNT_BIG(*) AS TotalHistoricalRecords,
    COUNT(DISTINCT crypto_id) AS UniqueCryptocurrencies,
    MIN(snapshot_at_utc) AS FirstSnapshot,
    MAX(snapshot_at_utc) AS LatestSnapshot
FROM warehouse.CryptoPriceHistory;
GO
