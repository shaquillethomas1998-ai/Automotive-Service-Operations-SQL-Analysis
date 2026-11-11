USE AutomotiveServiceOperations;
GO

/* Each query should return zero rows after a successful load. */

-- 1. Appointments whose customer does not own the selected vehicle.
SELECT a.AppointmentID, a.CustomerID, a.VehicleID, v.CustomerID AS VehicleOwnerID
FROM dbo.Appointments AS a
JOIN dbo.Vehicles AS v ON v.VehicleID = a.VehicleID
WHERE a.CustomerID <> v.CustomerID;

-- 2. Completed repair orders missing a completion timestamp.
SELECT RepairOrderID, OrderStatus, CompletedAt
FROM dbo.RepairOrders
WHERE OrderStatus = 'Completed' AND CompletedAt IS NULL;

-- 3. Open repair orders that already have a completion timestamp.
SELECT RepairOrderID, OrderStatus, CompletedAt
FROM dbo.RepairOrders
WHERE OrderStatus <> 'Completed' AND CompletedAt IS NOT NULL;

-- 4. Repair-order totals that do not reconcile to subtotal plus Ontario HST.
SELECT RepairOrderID, LaborSubtotal, PartsSubtotal, TaxAmount, TotalAmount,
       LaborSubtotal + PartsSubtotal + TaxAmount AS ExpectedTotal
FROM dbo.RepairOrders
WHERE ABS(TotalAmount - (LaborSubtotal + PartsSubtotal + TaxAmount)) > 0.02
   OR ABS(TaxAmount - ROUND((LaborSubtotal + PartsSubtotal) * 0.13, 2)) > 0.02;

-- 5. Service labor that does not reconcile to its repair order.
SELECT ro.RepairOrderID, ro.LaborSubtotal, SUM(ros.LaborAmount) AS ServiceLabor
FROM dbo.RepairOrders AS ro
JOIN dbo.RepairOrderServices AS ros ON ros.RepairOrderID = ro.RepairOrderID
GROUP BY ro.RepairOrderID, ro.LaborSubtotal
HAVING ABS(ro.LaborSubtotal - SUM(ros.LaborAmount)) > 0.02;

-- 6. Part charges that do not reconcile to the repair-order parts subtotal.
SELECT ro.RepairOrderID, ro.PartsSubtotal,
       SUM(pu.QuantityUsed * pu.UnitPrice) AS CalculatedPartsSubtotal
FROM dbo.RepairOrders AS ro
JOIN dbo.PartUsage AS pu ON pu.RepairOrderID = ro.RepairOrderID
GROUP BY ro.RepairOrderID, ro.PartsSubtotal
HAVING ABS(ro.PartsSubtotal - SUM(pu.QuantityUsed * pu.UnitPrice)) > 0.02;

-- 7. Technician time logs with invalid or inconsistent durations.
SELECT TimeLogID, StartTime, EndTime, HoursWorked,
       DATEDIFF(MINUTE, StartTime, EndTime) / 60.0 AS CalculatedHours
FROM dbo.TechnicianTimeLogs
WHERE (EndTime IS NULL AND HoursWorked IS NOT NULL)
   OR (EndTime IS NOT NULL AND HoursWorked IS NULL)
   OR (EndTime IS NOT NULL AND ABS(HoursWorked - DATEDIFF(MINUTE, StartTime, EndTime) / 60.0) > 0.05);

-- 8. Overlapping time logs for the same technician.
WITH OrderedLogs AS (
    SELECT TimeLogID, TechnicianID, StartTime, EndTime,
           LAG(EndTime) OVER (PARTITION BY TechnicianID ORDER BY StartTime, TimeLogID) AS PreviousEndTime
    FROM dbo.TechnicianTimeLogs
    WHERE EndTime IS NOT NULL
)
SELECT TimeLogID, TechnicianID, StartTime, EndTime, PreviousEndTime
FROM OrderedLogs
WHERE StartTime < PreviousEndTime;

-- 9. Part-shortage rows that do not represent a true shortage.
SELECT ShortageID, QuantityNeeded, QuantityAvailable
FROM dbo.PartsShortages
WHERE QuantityNeeded <= 0
   OR QuantityAvailable < 0
   OR QuantityAvailable >= QuantityNeeded;

-- 10. Finished services attached to unfinished repair orders, or vice versa.
SELECT ro.RepairOrderID, ro.OrderStatus, ros.RepairOrderServiceID, ros.ServiceStatus
FROM dbo.RepairOrders AS ro
JOIN dbo.RepairOrderServices AS ros ON ros.RepairOrderID = ro.RepairOrderID
WHERE (ro.OrderStatus = 'Completed' AND ros.ServiceStatus <> 'Completed')
   OR (ro.OrderStatus <> 'Completed' AND ros.ServiceStatus = 'Completed');
GO

