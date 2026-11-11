# Entity Relationship Diagram

```mermaid
erDiagram
    CUSTOMERS ||--o{ VEHICLES : owns
    CUSTOMERS ||--o{ APPOINTMENTS : books
    VEHICLES ||--o{ APPOINTMENTS : scheduled_for
    APPOINTMENTS ||--o| REPAIR_ORDERS : becomes
    VEHICLES ||--o{ REPAIR_ORDERS : receives
    REPAIR_ORDERS ||--o{ REPAIR_ORDER_SERVICES : contains
    SERVICE_TYPES ||--o{ REPAIR_ORDER_SERVICES : classifies
    TECHNICIANS ||--o{ REPAIR_ORDER_SERVICES : performs
    TECHNICIANS ||--o{ TECHNICIAN_SHIFTS : works
    REPAIR_ORDER_SERVICES ||--o{ TECHNICIAN_TIME_LOGS : records
    TECHNICIANS ||--o{ TECHNICIAN_TIME_LOGS : logs
    REPAIR_ORDERS ||--o{ PART_USAGE : consumes
    PARTS ||--o{ PART_USAGE : used_as
    REPAIR_ORDERS ||--o{ PARTS_SHORTAGES : experiences
    PARTS ||--o{ PARTS_SHORTAGES : unavailable
```

## Design Choices

- Customers and vehicles are separated because one customer may own multiple vehicles.
- Appointments represent planned demand; repair orders represent work that actually entered the shop.
- RepairOrderServices resolves the many-to-many relationship between repair orders and service types.
- TechnicianTimeLogs are separated from service assignment so scheduled responsibility and recorded labor can be compared.
- PartUsage records actual consumption, while PartsShortages records inventory failures and their operational delay.
- Monetary values are stored on the transaction rows to preserve the price or cost used at that time.
