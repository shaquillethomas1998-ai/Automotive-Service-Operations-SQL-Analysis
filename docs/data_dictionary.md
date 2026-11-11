# Data Dictionary

All data is synthetic and represents the fictional Quazar Auto Care location in Ottawa during 2025.

| Table | Primary key | Important foreign keys | Purpose |
|---|---|---|---|
| Customers | CustomerID | - | Stores customer contact and location data. |
| Vehicles | VehicleID | CustomerID | Connects each vehicle to its owner. |
| Appointments | AppointmentID | CustomerID, VehicleID | Captures scheduled demand, status and booking channel. |
| RepairOrders | RepairOrderID | AppointmentID, VehicleID | Stores work-order timing, status, priority and financial totals. |
| ServiceTypes | ServiceTypeID | - | Defines the service catalogue, standard hours and base price. |
| RepairOrderServices | RepairOrderServiceID | RepairOrderID, ServiceTypeID, TechnicianID | Stores the services performed on each order. |
| Technicians | TechnicianID | - | Stores technician skill level, hire date and hourly rate. |
| TechnicianShifts | ShiftID | TechnicianID | Stores scheduled technician availability. |
| TechnicianTimeLogs | TimeLogID | RepairOrderServiceID, TechnicianID | Stores recorded start, end and direct labor time. |
| Parts | PartID | - | Stores the parts catalogue, cost, selling price and inventory settings. |
| PartUsage | PartUsageID | RepairOrderID, PartID | Stores parts and quantities consumed by repair orders. |
| PartsShortages | ShortageID | RepairOrderID, PartID | Stores stockout events, resolution timing and delay hours. |

## Key Business Fields

- **ScheduledStart / ScheduledEnd:** planned appointment window.
- **OpenedAt / CompletedAt:** actual repair-order lifecycle timestamps.
- **PromisedAt:** customer-facing completion target used for on-time performance.
- **StandardHours / ActualHours:** baseline and observed service duration.
- **ScheduledHours / HoursWorked:** capacity and direct repair time used for utilization.
- **ReorderLevel / StockOnHand:** inventory controls used to identify review candidates.
- **DelayHours:** simulated operational delay associated with a recorded part shortage.
- **LaborSubtotal / PartsSubtotal / TaxAmount / TotalAmount:** repair-order financial measures using Ontario HST at 13%.

## Permitted Status Values

- AppointmentStatus: Completed, Cancelled, No-Show, Scheduled, Arrived.
- OrderStatus: Completed, In Progress, Waiting for Parts, Cancelled.
- ServiceStatus: Completed, In Progress, Cancelled.
- Priority: Normal, High, Urgent.
- SkillLevel: Apprentice, Licensed, Master.
