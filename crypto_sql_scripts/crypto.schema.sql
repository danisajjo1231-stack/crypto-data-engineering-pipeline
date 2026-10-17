IF DB_ID('CryptoMarketDW') IS NULL
BEGIN
    CREATE DATABASE CryptoMarketDW;
END;
GO

USE CryptoMarketDW;
GO

IF SCHEMA_ID('staging') IS NULL
BEGIN
    EXEC('CREATE SCHEMA staging');
END;
GO

SELECT
    DB_NAME() AS CurrentDatabase,
    SCHEMA_NAME() AS StagingSchema;
GO

