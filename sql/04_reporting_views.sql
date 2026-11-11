USE AutomotiveServiceOperations;
GO

CREATE OR ALTER VIEW dbo.vw_RepairOrderPerformance AS
SELECT
    ro.RepairOrderID,
    ro.AppointmentID,
    ro.VehicleID,
    v.Make,
    v.Model,
    ro.OpenedAt,
    ro.PromisedAt,
    ro.CompletedAt,
    ro.OrderStatus,
    ro.Priority,
    ro.TotalAmount,
    CASE WHEN ro.CompletedAt IS NULL THEN NULL
         ELSE DATEDIFF(MINUTE, ro.OpenedAt, ro.CompletedAt) / 60.0 END AS TurnaroundHours,
    CASE WHEN ro.CompletedAt IS NULL THEN NULL
         WHEN ro.CompletedAt <= ro.PromisedAt THEN 1 ELSE 0 END AS CompletedOnTime,
    CASE WHEN EXISTS (
        SELECT 1 FROM dbo.PartsShortages AS ps WHERE ps.RepairOrderID = ro.RepairOrderID
    ) THEN 1 ELSE 0 END AS HadPartsShortage
FROM dbo.RepairOrders AS ro
JOIN dbo.Vehicles AS v ON v.VehicleID = ro.VehicleID;
GO

CREATE OR ALTER VIEW dbo.vw_DailyBookings AS
SELECT
    CAST(ScheduledStart AS DATE) AS BookingDate,
    DATENAME(WEEKDAY, ScheduledStart) AS WeekdayName,
    BookingChannel,
    AppointmentStatus,
    COUNT_BIG(*) AS AppointmentCount
FROM dbo.Appointments
GROUP BY CAST(ScheduledStart AS DATE), DATENAME(WEEKDAY, ScheduledStart), BookingChannel, AppointmentStatus;
GO

CREATE OR ALTER VIEW dbo.vw_ServicePerformance AS
SELECT
    st.ServiceTypeID,
    st.ServiceName,
    st.Category,
    COUNT_BIG(*) AS ServiceCount,
    AVG(CAST(ros.ActualHours AS DECIMAL(10,2))) AS AverageActualHours,
    st.StandardHours,
    SUM(ros.LaborAmount) AS LaborRevenue,
    AVG(CAST(ros.ActualHours - st.StandardHours AS DECIMAL(10,2))) AS AverageHoursVariance
FROM dbo.RepairOrderServices AS ros
JOIN dbo.ServiceTypes AS st ON st.ServiceTypeID = ros.ServiceTypeID
GROUP BY st.ServiceTypeID, st.ServiceName, st.Category, st.StandardHours;
GO

CREATE OR ALTER VIEW dbo.vw_TechnicianUtilization AS
WITH Scheduled AS (
    SELECT TechnicianID,
           SUM(DATEDIFF(MINUTE, ShiftStart, ShiftEnd)) / 60.0 AS ScheduledHours
    FROM dbo.TechnicianShifts
    GROUP BY TechnicianID
), Logged AS (
    SELECT TechnicianID, SUM(HoursWorked) AS LoggedHours
    FROM dbo.TechnicianTimeLogs
    WHERE HoursWorked IS NOT NULL
    GROUP BY TechnicianID
)
SELECT
    t.TechnicianID,
    CONCAT(t.FirstName, ' ', t.LastName) AS TechnicianName,
    t.SkillLevel,
    COALESCE(s.ScheduledHours, 0) AS ScheduledHours,
    COALESCE(l.LoggedHours, 0) AS LoggedHours,
    CASE WHEN COALESCE(s.ScheduledHours, 0) = 0 THEN 0
         ELSE COALESCE(l.LoggedHours, 0) / s.ScheduledHours END AS UtilizationRate
FROM dbo.Technicians AS t
LEFT JOIN Scheduled AS s ON s.TechnicianID = t.TechnicianID
LEFT JOIN Logged AS l ON l.TechnicianID = t.TechnicianID;
GO

CREATE OR ALTER VIEW dbo.vw_PartsShortageImpact AS
SELECT
    p.PartID,
    p.PartNumber,
    p.PartName,
    p.Category,
    p.ReorderLevel,
    p.StockOnHand,
    p.SupplierLeadDays,
    COUNT_BIG(ps.ShortageID) AS ShortageEvents,
    AVG(CAST(ps.DelayHours AS DECIMAL(10,2))) AS AverageDelayHours,
    SUM(CAST(ps.DelayHours AS DECIMAL(12,2))) AS TotalDelayHours
FROM dbo.Parts AS p
LEFT JOIN dbo.PartsShortages AS ps ON ps.PartID = p.PartID
GROUP BY p.PartID, p.PartNumber, p.PartName, p.Category,
         p.ReorderLevel, p.StockOnHand, p.SupplierLeadDays;
GO

