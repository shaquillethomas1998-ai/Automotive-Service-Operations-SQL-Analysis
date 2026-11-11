USE AutomotiveServiceOperations;
GO

-- Q1. Which weekdays carry the highest appointment volume?
SELECT DATENAME(WEEKDAY, ScheduledStart) AS WeekdayName,
       COUNT(*) AS AppointmentCount,
       SUM(CASE WHEN AppointmentStatus = 'Completed' THEN 1 ELSE 0 END) AS CompletedAppointments
FROM dbo.Appointments
GROUP BY DATENAME(WEEKDAY, ScheduledStart), DATEPART(WEEKDAY, ScheduledStart)
ORDER BY AppointmentCount DESC;

-- Q2. Monthly demand, revenue, and average ticket.
SELECT DATEFROMPARTS(YEAR(OpenedAt), MONTH(OpenedAt), 1) AS MonthStart,
       COUNT(*) AS RepairOrders,
       SUM(TotalAmount) AS Revenue,
       AVG(TotalAmount) AS AverageTicket
FROM dbo.RepairOrders
GROUP BY DATEFROMPARTS(YEAR(OpenedAt), MONTH(OpenedAt), 1)
ORDER BY MonthStart;

-- Q3. Turnaround and on-time performance by month.
WITH MonthlyOrders AS (
    SELECT DATEFROMPARTS(YEAR(OpenedAt), MONTH(OpenedAt), 1) AS MonthStart,
           RepairOrderID, TurnaroundHours, CompletedOnTime,
           PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY TurnaroundHours)
               OVER (PARTITION BY DATEFROMPARTS(YEAR(OpenedAt), MONTH(OpenedAt), 1)) AS MedianTurnaroundHours
    FROM dbo.vw_RepairOrderPerformance
    WHERE CompletedAt IS NOT NULL
)
SELECT MonthStart,
       COUNT(*) AS CompletedOrders,
       AVG(TurnaroundHours) AS AverageTurnaroundHours,
       MAX(MedianTurnaroundHours) AS MedianTurnaroundHours,
       AVG(CAST(CompletedOnTime AS DECIMAL(6,4))) AS OnTimeCompletionRate
FROM MonthlyOrders
GROUP BY MonthStart
ORDER BY MonthStart;

-- Q4. How much longer do jobs take when a part shortage occurs?
SELECT HadPartsShortage,
       COUNT(*) AS CompletedOrders,
       AVG(TurnaroundHours) AS AverageTurnaroundHours,
       AVG(CAST(CompletedOnTime AS DECIMAL(6,4))) AS OnTimeCompletionRate
FROM dbo.vw_RepairOrderPerformance
WHERE CompletedAt IS NOT NULL
GROUP BY HadPartsShortage;

-- Q5. Top shortage-causing parts by event count and total delay.
SELECT TOP (10) PartNumber, PartName, Category, ShortageEvents,
       AverageDelayHours, TotalDelayHours, ReorderLevel, StockOnHand
FROM dbo.vw_PartsShortageImpact
WHERE ShortageEvents > 0
ORDER BY TotalDelayHours DESC, ShortageEvents DESC;

-- Q6. Service volume, actual hours, and variance from standard.
SELECT ServiceName, Category, ServiceCount, StandardHours,
       AverageActualHours, AverageHoursVariance, LaborRevenue
FROM dbo.vw_ServicePerformance
ORDER BY ServiceCount DESC;

-- Q7. Technician scheduled-versus-recorded hours and utilization rank.
SELECT TechnicianID, TechnicianName, SkillLevel, ScheduledHours, LoggedHours,
       UtilizationRate,
       DENSE_RANK() OVER (ORDER BY UtilizationRate DESC) AS UtilizationRank
FROM dbo.vw_TechnicianUtilization
ORDER BY UtilizationRank, TechnicianName;

-- Q8. Rolling seven-day booking volume.
WITH Daily AS (
    SELECT CAST(ScheduledStart AS DATE) AS BookingDate, COUNT(*) AS DailyBookings
    FROM dbo.Appointments
    GROUP BY CAST(ScheduledStart AS DATE)
)
SELECT BookingDate, DailyBookings,
       SUM(DailyBookings) OVER (
           ORDER BY BookingDate ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ) AS Rolling7DayBookings
FROM Daily
ORDER BY BookingDate;

-- Q9. Services most often linked to a shortage event.
SELECT st.ServiceName,
       COUNT(DISTINCT ros.RepairOrderID) AS OrdersWithService,
       COUNT(DISTINCT ps.RepairOrderID) AS OrdersWithShortage,
       CAST(COUNT(DISTINCT ps.RepairOrderID) AS DECIMAL(10,4)) /
           NULLIF(COUNT(DISTINCT ros.RepairOrderID), 0) AS ShortageRate
FROM dbo.RepairOrderServices AS ros
JOIN dbo.ServiceTypes AS st ON st.ServiceTypeID = ros.ServiceTypeID
LEFT JOIN dbo.PartsShortages AS ps ON ps.RepairOrderID = ros.RepairOrderID
GROUP BY st.ServiceName
ORDER BY ShortageRate DESC, OrdersWithService DESC;

-- Q10. Candidate parts for reorder-policy review.
SELECT PartNumber, PartName, Category, StockOnHand, ReorderLevel,
       SupplierLeadDays, ShortageEvents, TotalDelayHours
FROM dbo.vw_PartsShortageImpact
WHERE StockOnHand <= ReorderLevel OR ShortageEvents >= 5
ORDER BY ShortageEvents DESC, SupplierLeadDays DESC;
GO

