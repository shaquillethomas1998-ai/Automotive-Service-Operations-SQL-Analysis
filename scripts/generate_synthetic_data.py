"""Generate a deterministic one-year synthetic dataset for Quazar Auto Care.

The records are fictional and are intended only for portfolio demonstration.
"""

from __future__ import annotations

import json
import random
from collections import defaultdict
from datetime import date, datetime, time, timedelta
from pathlib import Path

import pandas as pd


SEED = 20261109
random.seed(SEED)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
FINDINGS_DIR = ROOT / "findings"
DATA_DIR.mkdir(parents=True, exist_ok=True)
FINDINGS_DIR.mkdir(parents=True, exist_ok=True)

START_DATE = date(2025, 1, 1)
END_DATE = date(2025, 12, 31)
HST_RATE = 0.13

FIRST_NAMES = [
    "Aiden", "Amara", "Andre", "Ava", "Brianna", "Caleb", "Chloe", "Daniel",
    "Elijah", "Emily", "Ethan", "Gabrielle", "Isaiah", "Jada", "Jamal",
    "Jasmine", "Jordan", "Kai", "Leah", "Liam", "Maya", "Michael", "Naomi",
    "Noah", "Olivia", "Owen", "Priya", "Renee", "Samuel", "Sofia", "Zoe",
]

LAST_NAMES = [
    "Anderson", "Brown", "Campbell", "Chen", "Clarke", "Davis", "Edwards",
    "Evans", "Foster", "Fraser", "Garcia", "Grant", "Green", "Hall", "Harris",
    "Jackson", "Johnson", "Khan", "Lewis", "Martin", "Mitchell", "Morgan",
    "Patel", "Reid", "Robinson", "Singh", "Smith", "Taylor", "Thomas", "Walker",
]

VEHICLE_CATALOG = [
    ("Toyota", "Corolla"), ("Toyota", "RAV4"), ("Honda", "Civic"),
    ("Honda", "CR-V"), ("Ford", "F-150"), ("Ford", "Escape"),
    ("Hyundai", "Elantra"), ("Hyundai", "Tucson"), ("Kia", "Forte"),
    ("Kia", "Sportage"), ("Mazda", "Mazda3"), ("Mazda", "CX-5"),
    ("Nissan", "Rogue"), ("Subaru", "Outback"), ("Volkswagen", "Jetta"),
    ("BMW", "3 Series"), ("Chevrolet", "Equinox"), ("Jeep", "Wrangler"),
]

SERVICE_TYPES = [
    (1, "Oil Change", "Maintenance", 0.7, 89.99),
    (2, "Brake Inspection", "Brakes", 0.8, 79.99),
    (3, "Front Brake Pad Replacement", "Brakes", 2.0, 249.99),
    (4, "Rear Brake Pad Replacement", "Brakes", 2.2, 269.99),
    (5, "Diagnostic Scan", "Diagnostics", 1.0, 99.99),
    (6, "Battery Replacement", "Electrical", 0.8, 189.99),
    (7, "Tire Rotation", "Tires", 0.6, 59.99),
    (8, "Seasonal Tire Change", "Tires", 1.2, 139.99),
    (9, "Wheel Alignment", "Tires", 1.5, 149.99),
    (10, "Cooling System Service", "Maintenance", 1.5, 179.99),
    (11, "Spark Plug Replacement", "Engine", 2.0, 299.99),
    (12, "Air Filter Replacement", "Maintenance", 0.4, 49.99),
]

PARTS = [
    (1, "OIL-5W30", "Synthetic Engine Oil 5W-30", "Fluids", 38.00, 62.00, 20, 46, 3),
    (2, "FILTER-OIL", "Standard Oil Filter", "Filters", 7.50, 16.00, 18, 38, 3),
    (3, "PAD-FRONT-A", "Front Brake Pad Set A", "Brakes", 72.00, 128.00, 8, 10, 6),
    (4, "PAD-FRONT-B", "Front Brake Pad Set B", "Brakes", 79.00, 139.00, 8, 7, 7),
    (5, "PAD-REAR-A", "Rear Brake Pad Set A", "Brakes", 64.00, 119.00, 8, 9, 6),
    (6, "PAD-REAR-B", "Rear Brake Pad Set B", "Brakes", 69.00, 124.00, 8, 6, 7),
    (7, "BAT-24F", "Battery Group 24F", "Electrical", 118.00, 189.00, 5, 6, 5),
    (8, "BAT-48", "Battery Group 48", "Electrical", 132.00, 209.00, 5, 4, 6),
    (9, "COOLANT-UNI", "Universal Coolant 4 L", "Fluids", 19.00, 36.00, 10, 22, 4),
    (10, "PLUG-IR4", "Iridium Spark Plug Set 4", "Engine", 44.00, 88.00, 6, 11, 5),
    (11, "PLUG-IR6", "Iridium Spark Plug Set 6", "Engine", 62.00, 118.00, 5, 7, 6),
    (12, "FILTER-AIR-A", "Engine Air Filter A", "Filters", 13.00, 31.00, 10, 18, 4),
    (13, "FILTER-AIR-B", "Engine Air Filter B", "Filters", 15.00, 34.00, 10, 13, 5),
    (14, "TIRE-VALVE", "Tire Valve Stem", "Tires", 2.50, 8.00, 25, 55, 3),
    (15, "ALIGN-SHIM", "Alignment Shim Kit", "Tires", 12.00, 29.00, 8, 16, 5),
    (16, "BRAKE-CLEAN", "Brake Cleaner", "Brakes", 5.00, 12.00, 12, 27, 3),
    (17, "SHOP-SUPPLY", "General Shop Supplies", "Supplies", 3.00, 9.00, 30, 70, 2),
    (18, "WASHER-FLUID", "Washer Fluid 4 L", "Fluids", 4.00, 11.00, 15, 31, 3),
]

SERVICE_PARTS = {
    1: [(1, 1), (2, 1)],
    3: [(3, 1), (16, 1)],
    4: [(5, 1), (16, 1)],
    6: [(7, 1)],
    7: [(14, 4)],
    8: [(14, 4)],
    9: [(15, 1)],
    10: [(9, 1)],
    11: [(10, 1)],
    12: [(12, 1)],
}


def random_phone() -> str:
    return f"613-{random.randint(200, 999)}-{random.randint(1000, 9999)}"


def random_vin(vehicle_id: int) -> str:
    chars = "ABCDEFGHJKLMNPRSTUVWXYZ0123456789"
    prefix = "QA"
    body = "".join(random.choice(chars) for _ in range(10))
    return f"{prefix}{body}{vehicle_id:05d}"[:17]


def pick_service_ids(month: int) -> list[int]:
    weights = [23, 5, 9, 7, 10, 6, 9, 12 if month in (4, 5, 10, 11) else 5, 5, 5, 3, 9]
    count = random.choices([1, 2, 3], [70, 25, 5], k=1)[0]
    selected: list[int] = []
    while len(selected) < count:
        service_id = random.choices(range(1, 13), weights=weights, k=1)[0]
        if service_id not in selected:
            selected.append(service_id)
    return selected


def choose_part(service_id: int) -> list[tuple[int, int]]:
    base = SERVICE_PARTS.get(service_id, [(17, 1)])
    selected = list(base)
    if service_id == 3:
        selected[0] = (random.choice([3, 4]), 1)
    elif service_id == 4:
        selected[0] = (random.choice([5, 6]), 1)
    elif service_id == 6:
        selected[0] = (random.choice([7, 8]), 1)
    elif service_id == 11:
        selected[0] = (random.choice([10, 11]), 1)
    elif service_id == 12:
        selected[0] = (random.choice([12, 13]), 1)
    return selected


def to_iso(value):
    if value is None or value == "":
        return ""
    if isinstance(value, (datetime, date)):
        return value.isoformat(sep=" ") if isinstance(value, datetime) else value.isoformat()
    return value


def write_csv(name: str, rows: list[dict]) -> None:
    frame = pd.DataFrame(rows)
    for column in frame.columns:
        if frame[column].map(lambda x: isinstance(x, (datetime, date))).any():
            frame[column] = frame[column].map(to_iso)
    frame.to_csv(DATA_DIR / f"{name}.csv", index=False)


def main() -> None:
    customers = []
    for customer_id in range(1, 401):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        customers.append({
            "CustomerID": customer_id,
            "FirstName": first,
            "LastName": last,
            "Phone": random_phone(),
            "Email": f"{first.lower()}.{last.lower()}{customer_id}@example.com",
            "City": random.choices(["Ottawa", "Kanata", "Nepean", "Orleans", "Gloucester"], [55, 12, 14, 12, 7], k=1)[0],
            "Province": "ON",
            "CreatedDate": START_DATE - timedelta(days=random.randint(30, 1100)),
        })

    vehicles = []
    vehicle_id = 1
    for customer in customers:
        vehicle_count = random.choices([1, 2, 3], [76, 21, 3], k=1)[0]
        for _ in range(vehicle_count):
            make, model = random.choice(VEHICLE_CATALOG)
            year = random.randint(2011, 2026)
            vehicles.append({
                "VehicleID": vehicle_id,
                "CustomerID": customer["CustomerID"],
                "VIN": random_vin(vehicle_id),
                "VehicleYear": year,
                "Make": make,
                "Model": model,
                "OdometerKM": random.randint(12000, min(310000, (2027 - year) * 24000 + 35000)),
            })
            vehicle_id += 1

    technicians = []
    skill_levels = ["Apprentice", "Licensed", "Licensed", "Master"]
    for technician_id in range(1, 5):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        technicians.append({
            "TechnicianID": technician_id,
            "FirstName": first,
            "LastName": last,
            "SkillLevel": skill_levels[technician_id - 1],
            "HireDate": START_DATE - timedelta(days=random.randint(180, 2800)),
            "HourlyRate": round(random.uniform(23, 43), 2),
            "ActiveFlag": 1,
        })

    service_types = [
        {"ServiceTypeID": row[0], "ServiceName": row[1], "Category": row[2], "StandardHours": row[3], "BasePrice": row[4]}
        for row in SERVICE_TYPES
    ]
    service_lookup = {row[0]: row for row in SERVICE_TYPES}
    parts = [
        {
            "PartID": row[0], "PartNumber": row[1], "PartName": row[2], "Category": row[3],
            "UnitCost": row[4], "UnitPrice": row[5], "ReorderLevel": row[6],
            "StockOnHand": row[7], "SupplierLeadDays": row[8],
        }
        for row in PARTS
    ]
    part_lookup = {row[0]: row for row in PARTS}

    shifts = []
    shift_id = 1
    current = START_DATE
    while current <= END_DATE:
        if current.weekday() < 6:
            for tech in technicians:
                if random.random() < 0.07:
                    continue
                start_hour, end_hour = (8, 14) if current.weekday() == 5 else (8, 17)
                shifts.append({
                    "ShiftID": shift_id,
                    "TechnicianID": tech["TechnicianID"],
                    "ShiftDate": current,
                    "ShiftStart": f"{start_hour:02d}:00:00",
                    "ShiftEnd": f"{end_hour:02d}:00:00",
                })
                shift_id += 1
        current += timedelta(days=1)

    eligible_dates = []
    date_weights = []
    current = START_DATE
    while current <= END_DATE:
        if current.weekday() < 6:
            eligible_dates.append(current)
            date_weights.append(1.28 if current.weekday() == 4 else (0.72 if current.weekday() == 5 else 1.0))
        current += timedelta(days=1)

    appointments = []
    for appointment_id in range(1, 1801):
        scheduled_date = random.choices(eligible_dates, weights=date_weights, k=1)[0]
        start_hour = random.choice([8, 9, 10, 11, 12, 13, 14, 15, 16])
        start_minute = random.choice([0, 15, 30, 45])
        scheduled_start = datetime.combine(scheduled_date, time(start_hour, start_minute))
        scheduled_end = scheduled_start + timedelta(minutes=random.choice([60, 90, 120, 180]))
        vehicle = random.choice(vehicles)
        days_before = random.randint(1, 28)
        status = random.choices(
            ["Completed", "Cancelled", "No-Show", "Scheduled", "Arrived"],
            [82, 7, 5, 4, 2], k=1
        )[0]
        appointments.append({
            "AppointmentID": appointment_id,
            "CustomerID": vehicle["CustomerID"],
            "VehicleID": vehicle["VehicleID"],
            "ScheduledStart": scheduled_start,
            "ScheduledEnd": scheduled_end,
            "BookingChannel": random.choices(["Phone", "Online", "Walk-In"], [43, 47, 10], k=1)[0],
            "AppointmentStatus": status,
            "CreatedAt": scheduled_start - timedelta(days=days_before, hours=random.randint(0, 8)),
        })

    repair_orders = []
    repair_order_services = []
    time_logs = []
    part_usage = []
    shortages = []
    repair_order_id = 1
    ros_id = 1
    time_log_id = 1
    usage_id = 1
    shortage_id = 1
    tech_available: dict[tuple[int, date], datetime] = {}

    for appt in appointments:
        if appt["AppointmentStatus"] not in ("Completed", "Arrived"):
            continue

        opened_at = appt["ScheduledStart"] + timedelta(minutes=random.randint(0, 25))
        service_ids = pick_service_ids(opened_at.month)
        order_open = appt["AppointmentStatus"] == "Arrived"
        order_status = random.choice(["In Progress", "Waiting for Parts"]) if order_open else "Completed"
        priority = random.choices(["Normal", "High", "Urgent"], [84, 13, 3], k=1)[0]
        promised_at = opened_at + timedelta(hours=sum(service_lookup[s][3] for s in service_ids) * 1.6 + 4)

        order_service_rows = []
        order_usage_rows = []
        order_shortages = []
        last_work_end = opened_at

        for service_id in service_ids:
            service = service_lookup[service_id]
            standard_hours = service[3]
            actual_hours = round(max(0.3, random.gauss(standard_hours, standard_hours * 0.18)), 2)
            tech_id = random.randint(1, 4)
            key = (tech_id, opened_at.date())
            start_time = max(opened_at, tech_available.get(key, datetime.combine(opened_at.date(), time(8, 0))))
            end_time = start_time + timedelta(hours=actual_hours)
            tech_available[key] = end_time + timedelta(minutes=15)
            last_work_end = max(last_work_end, end_time)
            service_status = "In Progress" if order_open else "Completed"
            labor_amount = round(service[4] * random.uniform(0.96, 1.08), 2)

            order_service_rows.append({
                "RepairOrderServiceID": ros_id,
                "RepairOrderID": repair_order_id,
                "ServiceTypeID": service_id,
                "TechnicianID": tech_id,
                "ActualHours": actual_hours,
                "LaborAmount": labor_amount,
                "ServiceStatus": service_status,
            })
            time_logs.append({
                "TimeLogID": time_log_id,
                "RepairOrderServiceID": ros_id,
                "TechnicianID": tech_id,
                "StartTime": start_time,
                "EndTime": "" if order_open else end_time,
                "HoursWorked": "" if order_open else actual_hours,
            })

            for part_id, quantity in choose_part(service_id):
                part = part_lookup[part_id]
                order_usage_rows.append({
                    "PartUsageID": usage_id,
                    "RepairOrderID": repair_order_id,
                    "PartID": part_id,
                    "QuantityUsed": quantity,
                    "UnitCost": part[4],
                    "UnitPrice": part[5],
                })
                usage_id += 1

                shortage_probability = 0.17 if service_id in (3, 4) else (0.12 if service_id == 6 else 0.035)
                critical_parts = {3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15}
                if part_id in critical_parts and random.random() < shortage_probability:
                    delay_hours = random.choices([2, 4, 8, 16, 24, 36, 48], [8, 12, 18, 20, 18, 14, 10], k=1)[0]
                    reported_at = opened_at + timedelta(minutes=random.randint(20, 100))
                    resolved_at = "" if order_open else reported_at + timedelta(hours=delay_hours)
                    order_shortages.append({
                        "ShortageID": shortage_id,
                        "RepairOrderID": repair_order_id,
                        "PartID": part_id,
                        "ReportedAt": reported_at,
                        "QuantityNeeded": quantity,
                        "QuantityAvailable": max(0, quantity - 1),
                        "ResolvedAt": resolved_at,
                        "DelayHours": delay_hours,
                    })
                    shortage_id += 1

            ros_id += 1
            time_log_id += 1

        repair_order_services.extend(order_service_rows)
        part_usage.extend(order_usage_rows)
        shortages.extend(order_shortages)

        labor_subtotal = round(sum(row["LaborAmount"] for row in order_service_rows), 2)
        parts_subtotal = round(sum(row["QuantityUsed"] * row["UnitPrice"] for row in order_usage_rows), 2)
        shortage_delay = max([row["DelayHours"] for row in order_shortages], default=0)
        completed_at = "" if order_open else last_work_end + timedelta(minutes=random.randint(20, 80), hours=shortage_delay)
        tax_amount = round((labor_subtotal + parts_subtotal) * HST_RATE, 2)
        total_amount = round(labor_subtotal + parts_subtotal + tax_amount, 2)

        vehicle = vehicles[appt["VehicleID"] - 1]
        repair_orders.append({
            "RepairOrderID": repair_order_id,
            "AppointmentID": appt["AppointmentID"],
            "VehicleID": appt["VehicleID"],
            "OpenedAt": opened_at,
            "PromisedAt": promised_at,
            "CompletedAt": completed_at,
            "OrderStatus": order_status,
            "Priority": priority,
            "OdometerKM": vehicle["OdometerKM"] + random.randint(0, 12000),
            "LaborSubtotal": labor_subtotal,
            "PartsSubtotal": parts_subtotal,
            "TaxAmount": tax_amount,
            "TotalAmount": total_amount,
        })
        repair_order_id += 1

    datasets = {
        "customers": customers,
        "vehicles": vehicles,
        "technicians": technicians,
        "service_types": service_types,
        "parts": parts,
        "technician_shifts": shifts,
        "appointments": appointments,
        "repair_orders": repair_orders,
        "repair_order_services": repair_order_services,
        "technician_time_logs": time_logs,
        "part_usage": part_usage,
        "parts_shortages": shortages,
    }
    for name, rows in datasets.items():
        write_csv(name, rows)

    ro_frame = pd.DataFrame(repair_orders)
    ro_frame["OpenedAt"] = pd.to_datetime(ro_frame["OpenedAt"])
    ro_frame["CompletedAt"] = pd.to_datetime(ro_frame["CompletedAt"], errors="coerce")
    completed = ro_frame.dropna(subset=["CompletedAt"]).copy()
    completed["TurnaroundHours"] = (completed["CompletedAt"] - completed["OpenedAt"]).dt.total_seconds() / 3600
    completed["OnTime"] = completed["CompletedAt"] <= pd.to_datetime(completed["PromisedAt"])

    appt_frame = pd.DataFrame(appointments)
    appt_frame["ScheduledStart"] = pd.to_datetime(appt_frame["ScheduledStart"])
    appt_frame["Weekday"] = appt_frame["ScheduledStart"].dt.day_name()
    weekday_counts = appt_frame.groupby("Weekday").size().sort_values(ascending=False)

    shortage_frame = pd.DataFrame(shortages)
    service_frame = pd.DataFrame(repair_order_services)
    service_frame = service_frame.merge(pd.DataFrame(service_types), on="ServiceTypeID")
    service_counts = service_frame.groupby("ServiceName").size().sort_values(ascending=False)

    summary = {
        "seed": SEED,
        "period": {"start": START_DATE.isoformat(), "end": END_DATE.isoformat()},
        "row_counts": {name: len(rows) for name, rows in datasets.items()},
        "completed_repair_orders": int(len(completed)),
        "average_turnaround_hours": round(float(completed["TurnaroundHours"].mean()), 2),
        "median_turnaround_hours": round(float(completed["TurnaroundHours"].median()), 2),
        "on_time_completion_rate": round(float(completed["OnTime"].mean() * 100), 2),
        "completed_order_revenue": round(float(completed["TotalAmount"].sum()), 2),
        "completed_average_ticket": round(float(completed["TotalAmount"].mean()), 2),
        "total_recorded_order_value": round(float(ro_frame["TotalAmount"].sum()), 2),
        "parts_shortage_events": int(len(shortage_frame)),
        "highest_booking_weekday": weekday_counts.index[0],
        "highest_booking_weekday_count": int(weekday_counts.iloc[0]),
        "most_common_service": service_counts.index[0],
        "most_common_service_count": int(service_counts.iloc[0]),
    }
    (FINDINGS_DIR / "dataset_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
