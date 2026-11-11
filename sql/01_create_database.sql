/* Automotive Service Operations SQL Analysis
   Target platform: Microsoft SQL Server 2019+
   Data: synthetic portfolio data for fictional Quazar Auto Care, Ottawa.
*/

IF DB_ID(N'AutomotiveServiceOperations') IS NULL
BEGIN
    CREATE DATABASE AutomotiveServiceOperations;
END;
GO

USE AutomotiveServiceOperations;
GO

