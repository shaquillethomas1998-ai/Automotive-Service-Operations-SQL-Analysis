USE AutomotiveServiceOperations;
GO

DROP TABLE IF EXISTS dbo.PartsShortages;
DROP TABLE IF EXISTS dbo.PartUsage;
DROP TABLE IF EXISTS dbo.TechnicianTimeLogs;
DROP TABLE IF EXISTS dbo.RepairOrderServices;
DROP TABLE IF EXISTS dbo.RepairOrders;
DROP TABLE IF EXISTS dbo.Appointments;
DROP TABLE IF EXISTS dbo.TechnicianShifts;
DROP TABLE IF EXISTS dbo.Parts;
DROP TABLE IF EXISTS dbo.ServiceTypes;
DROP TABLE IF EXISTS dbo.Technicians;
DROP TABLE IF EXISTS dbo.Vehicles;
DROP TABLE IF EXISTS dbo.Customers;
GO

CREATE TABLE dbo.Customers (
    CustomerID      INT           NOT NULL CONSTRAINT PK_Customers PRIMARY KEY,
    FirstName       NVARCHAR(50)  NOT NULL,
    LastName        NVARCHAR(50)  NOT NULL,
    Phone           VARCHAR(20)   NOT NULL,
    Email           VARCHAR(120)  NOT NULL CONSTRAINT UQ_Customers_Email UNIQUE,
    City            NVARCHAR(60)  NOT NULL,
    Province        CHAR(2)       NOT NULL CONSTRAINT DF_Customers_Province DEFAULT ('ON'),
    CreatedDate     DATE          NOT NULL,
    CONSTRAINT CK_Customers_Province CHECK (Province = 'ON')
);

CREATE TABLE dbo.Vehicles (
    VehicleID       INT           NOT NULL CONSTRAINT PK_Vehicles PRIMARY KEY,
    CustomerID      INT           NOT NULL,
    VIN             CHAR(17)      NOT NULL CONSTRAINT UQ_Vehicles_VIN UNIQUE,
    VehicleYear     SMALLINT      NOT NULL,
    Make            NVARCHAR(40)  NOT NULL,
    Model           NVARCHAR(50)  NOT NULL,
    OdometerKM      INT           NOT NULL,
    CONSTRAINT FK_Vehicles_Customers FOREIGN KEY (CustomerID) REFERENCES dbo.Customers(CustomerID),
    CONSTRAINT CK_Vehicles_Year CHECK (VehicleYear BETWEEN 1980 AND 2030),
    CONSTRAINT CK_Vehicles_Odometer CHECK (OdometerKM >= 0)
);

CREATE TABLE dbo.Technicians (
    TechnicianID    INT           NOT NULL CONSTRAINT PK_Technicians PRIMARY KEY,
    FirstName       NVARCHAR(50)  NOT NULL,
    LastName        NVARCHAR(50)  NOT NULL,
    SkillLevel      VARCHAR(20)   NOT NULL,
    HireDate        DATE          NOT NULL,
    HourlyRate      DECIMAL(10,2) NOT NULL,
    ActiveFlag      BIT           NOT NULL CONSTRAINT DF_Technicians_Active DEFAULT (1),
    CONSTRAINT CK_Technicians_Skill CHECK (SkillLevel IN ('Apprentice', 'Licensed', 'Master')),
    CONSTRAINT CK_Technicians_Rate CHECK (HourlyRate > 0)
);

CREATE TABLE dbo.ServiceTypes (
    ServiceTypeID   INT            NOT NULL CONSTRAINT PK_ServiceTypes PRIMARY KEY,
    ServiceName     NVARCHAR(100)  NOT NULL CONSTRAINT UQ_ServiceTypes_Name UNIQUE,
    Category        NVARCHAR(40)   NOT NULL,
    StandardHours   DECIMAL(6,2)   NOT NULL,
    BasePrice       DECIMAL(10,2)  NOT NULL,
    CONSTRAINT CK_ServiceTypes_Hours CHECK (StandardHours > 0),
    CONSTRAINT CK_ServiceTypes_Price CHECK (BasePrice >= 0)
);

CREATE TABLE dbo.Parts (
    PartID             INT            NOT NULL CONSTRAINT PK_Parts PRIMARY KEY,
    PartNumber         VARCHAR(30)    NOT NULL CONSTRAINT UQ_Parts_Number UNIQUE,
    PartName           NVARCHAR(100)  NOT NULL,
    Category           NVARCHAR(40)   NOT NULL,
    UnitCost           DECIMAL(10,2)  NOT NULL,
    UnitPrice          DECIMAL(10,2)  NOT NULL,
    ReorderLevel       INT            NOT NULL,
    StockOnHand        INT            NOT NULL,
    SupplierLeadDays   INT            NOT NULL,
    CONSTRAINT CK_Parts_Cost CHECK (UnitCost >= 0),
    CONSTRAINT CK_Parts_Price CHECK (UnitPrice >= UnitCost),
    CONSTRAINT CK_Parts_Inventory CHECK (ReorderLevel >= 0 AND StockOnHand >= 0),
    CONSTRAINT CK_Parts_LeadDays CHECK (SupplierLeadDays BETWEEN 0 AND 90)
);

CREATE TABLE dbo.TechnicianShifts (
    ShiftID          INT       NOT NULL CONSTRAINT PK_TechnicianShifts PRIMARY KEY,
    TechnicianID     INT       NOT NULL,
    ShiftDate        DATE      NOT NULL,
    ShiftStart       TIME(0)   NOT NULL,
    ShiftEnd         TIME(0)   NOT NULL,
    CONSTRAINT FK_Shifts_Technicians FOREIGN KEY (TechnicianID) REFERENCES dbo.Technicians(TechnicianID),
    CONSTRAINT UQ_Shifts_TechnicianDate UNIQUE (TechnicianID, ShiftDate),
    CONSTRAINT CK_Shifts_TimeOrder CHECK (ShiftEnd > ShiftStart)
);

CREATE TABLE dbo.Appointments (
    AppointmentID       INT           NOT NULL CONSTRAINT PK_Appointments PRIMARY KEY,
    CustomerID          INT           NOT NULL,
    VehicleID           INT           NOT NULL,
    ScheduledStart      DATETIME2(0)  NOT NULL,
    ScheduledEnd        DATETIME2(0)  NOT NULL,
    BookingChannel      VARCHAR(20)   NOT NULL,
    AppointmentStatus   VARCHAR(20)   NOT NULL,
    CreatedAt           DATETIME2(0)  NOT NULL,
    CONSTRAINT FK_Appointments_Customers FOREIGN KEY (CustomerID) REFERENCES dbo.Customers(CustomerID),
    CONSTRAINT FK_Appointments_Vehicles FOREIGN KEY (VehicleID) REFERENCES dbo.Vehicles(VehicleID),
    CONSTRAINT CK_Appointments_TimeOrder CHECK (ScheduledEnd > ScheduledStart),
    CONSTRAINT CK_Appointments_Channel CHECK (BookingChannel IN ('Phone', 'Online', 'Walk-In')),
    CONSTRAINT CK_Appointments_Status CHECK (AppointmentStatus IN ('Completed', 'Cancelled', 'No-Show', 'Scheduled', 'Arrived'))
);

CREATE TABLE dbo.RepairOrders (
    RepairOrderID     INT            NOT NULL CONSTRAINT PK_RepairOrders PRIMARY KEY,
    AppointmentID    INT            NOT NULL CONSTRAINT UQ_RepairOrders_Appointment UNIQUE,
    VehicleID        INT            NOT NULL,
    OpenedAt         DATETIME2(0)   NOT NULL,
    PromisedAt       DATETIME2(0)   NOT NULL,
    CompletedAt      DATETIME2(0)   NULL,
    OrderStatus      VARCHAR(25)    NOT NULL,
    Priority         VARCHAR(10)    NOT NULL,
    OdometerKM       INT            NOT NULL,
    LaborSubtotal    DECIMAL(12,2)  NOT NULL,
    PartsSubtotal    DECIMAL(12,2)  NOT NULL,
    TaxAmount        DECIMAL(12,2)  NOT NULL,
    TotalAmount      DECIMAL(12,2)  NOT NULL,
    CONSTRAINT FK_RepairOrders_Appointments FOREIGN KEY (AppointmentID) REFERENCES dbo.Appointments(AppointmentID),
    CONSTRAINT FK_RepairOrders_Vehicles FOREIGN KEY (VehicleID) REFERENCES dbo.Vehicles(VehicleID),
    CONSTRAINT CK_RepairOrders_TimeOrder CHECK (CompletedAt IS NULL OR CompletedAt >= OpenedAt),
    CONSTRAINT CK_RepairOrders_Status CHECK (OrderStatus IN ('Completed', 'In Progress', 'Waiting for Parts', 'Cancelled')),
    CONSTRAINT CK_RepairOrders_Priority CHECK (Priority IN ('Normal', 'High', 'Urgent')),
    CONSTRAINT CK_RepairOrders_Money CHECK (LaborSubtotal >= 0 AND PartsSubtotal >= 0 AND TaxAmount >= 0 AND TotalAmount >= 0),
    CONSTRAINT CK_RepairOrders_Odometer CHECK (OdometerKM >= 0)
);

CREATE TABLE dbo.RepairOrderServices (
    RepairOrderServiceID  INT            NOT NULL CONSTRAINT PK_RepairOrderServices PRIMARY KEY,
    RepairOrderID         INT            NOT NULL,
    ServiceTypeID         INT            NOT NULL,
    TechnicianID          INT            NOT NULL,
    ActualHours           DECIMAL(7,2)   NOT NULL,
    LaborAmount           DECIMAL(10,2)  NOT NULL,
    ServiceStatus         VARCHAR(20)    NOT NULL,
    CONSTRAINT FK_ROServices_RepairOrders FOREIGN KEY (RepairOrderID) REFERENCES dbo.RepairOrders(RepairOrderID),
    CONSTRAINT FK_ROServices_ServiceTypes FOREIGN KEY (ServiceTypeID) REFERENCES dbo.ServiceTypes(ServiceTypeID),
    CONSTRAINT FK_ROServices_Technicians FOREIGN KEY (TechnicianID) REFERENCES dbo.Technicians(TechnicianID),
    CONSTRAINT CK_ROServices_Hours CHECK (ActualHours > 0),
    CONSTRAINT CK_ROServices_Labor CHECK (LaborAmount >= 0),
    CONSTRAINT CK_ROServices_Status CHECK (ServiceStatus IN ('Completed', 'In Progress', 'Cancelled'))
);

CREATE TABLE dbo.TechnicianTimeLogs (
    TimeLogID             INT            NOT NULL CONSTRAINT PK_TechnicianTimeLogs PRIMARY KEY,
    RepairOrderServiceID  INT            NOT NULL,
    TechnicianID          INT            NOT NULL,
    StartTime             DATETIME2(0)   NOT NULL,
    EndTime               DATETIME2(0)   NULL,
    HoursWorked           DECIMAL(7,2)   NULL,
    CONSTRAINT FK_TimeLogs_ROServices FOREIGN KEY (RepairOrderServiceID) REFERENCES dbo.RepairOrderServices(RepairOrderServiceID),
    CONSTRAINT FK_TimeLogs_Technicians FOREIGN KEY (TechnicianID) REFERENCES dbo.Technicians(TechnicianID),
    CONSTRAINT CK_TimeLogs_TimeOrder CHECK (EndTime IS NULL OR EndTime > StartTime),
    CONSTRAINT CK_TimeLogs_Hours CHECK (HoursWorked IS NULL OR HoursWorked > 0)
);

CREATE TABLE dbo.PartUsage (
    PartUsageID       INT            NOT NULL CONSTRAINT PK_PartUsage PRIMARY KEY,
    RepairOrderID     INT            NOT NULL,
    PartID            INT            NOT NULL,
    QuantityUsed      INT            NOT NULL,
    UnitCost          DECIMAL(10,2)  NOT NULL,
    UnitPrice         DECIMAL(10,2)  NOT NULL,
    CONSTRAINT FK_PartUsage_RepairOrders FOREIGN KEY (RepairOrderID) REFERENCES dbo.RepairOrders(RepairOrderID),
    CONSTRAINT FK_PartUsage_Parts FOREIGN KEY (PartID) REFERENCES dbo.Parts(PartID),
    CONSTRAINT CK_PartUsage_Quantity CHECK (QuantityUsed > 0),
    CONSTRAINT CK_PartUsage_Money CHECK (UnitCost >= 0 AND UnitPrice >= UnitCost)
);

CREATE TABLE dbo.PartsShortages (
    ShortageID          INT            NOT NULL CONSTRAINT PK_PartsShortages PRIMARY KEY,
    RepairOrderID       INT            NOT NULL,
    PartID              INT            NOT NULL,
    ReportedAt          DATETIME2(0)   NOT NULL,
    QuantityNeeded      INT            NOT NULL,
    QuantityAvailable   INT            NOT NULL,
    ResolvedAt          DATETIME2(0)   NULL,
    DelayHours          DECIMAL(8,2)   NOT NULL,
    CONSTRAINT FK_Shortages_RepairOrders FOREIGN KEY (RepairOrderID) REFERENCES dbo.RepairOrders(RepairOrderID),
    CONSTRAINT FK_Shortages_Parts FOREIGN KEY (PartID) REFERENCES dbo.Parts(PartID),
    CONSTRAINT CK_Shortages_Quantity CHECK (QuantityNeeded > 0 AND QuantityAvailable >= 0 AND QuantityAvailable < QuantityNeeded),
    CONSTRAINT CK_Shortages_TimeOrder CHECK (ResolvedAt IS NULL OR ResolvedAt >= ReportedAt),
    CONSTRAINT CK_Shortages_Delay CHECK (DelayHours >= 0)
);
GO

CREATE INDEX IX_Appointments_ScheduledStart ON dbo.Appointments(ScheduledStart);
CREATE INDEX IX_RepairOrders_OpenedAt_Status ON dbo.RepairOrders(OpenedAt, OrderStatus);
CREATE INDEX IX_ROServices_ServiceType ON dbo.RepairOrderServices(ServiceTypeID);
CREATE INDEX IX_TimeLogs_Technician_Start ON dbo.TechnicianTimeLogs(TechnicianID, StartTime);
CREATE INDEX IX_PartUsage_Part ON dbo.PartUsage(PartID);
CREATE INDEX IX_Shortages_Part_Reported ON dbo.PartsShortages(PartID, ReportedAt);
GO

