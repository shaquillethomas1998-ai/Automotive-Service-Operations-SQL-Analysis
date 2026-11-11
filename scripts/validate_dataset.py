"""Validate generated CSV relationships and business rules before SQL Server load."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FINDINGS = ROOT / "findings"


def load(name: str, dates: list[str] | None = None) -> pd.DataFrame:
    frame = pd.read_csv(DATA / f"{name}.csv")
    for column in dates or []:
        frame[column] = pd.to_datetime(
            frame[column], format="mixed", dayfirst=True, errors="coerce"
        )
    return frame


def main() -> None:
    customers = load("customers", ["CreatedDate"])
    vehicles = load("vehicles")
    appointments = load("appointments", ["ScheduledStart", "ScheduledEnd", "CreatedAt"])
    repair_orders = load("repair_orders", ["OpenedAt", "PromisedAt", "CompletedAt"])
    services = load("repair_order_services")
    technicians = load("technicians", ["HireDate"])
    logs = load("technician_time_logs", ["StartTime", "EndTime"])
    parts = load("parts")
    usage = load("part_usage")
    shortages = load("parts_shortages", ["ReportedAt", "ResolvedAt"])

    checks: dict[str, int] = {}
    checks["duplicate_customer_ids"] = int(customers["CustomerID"].duplicated().sum())
    checks["duplicate_vehicle_ids"] = int(vehicles["VehicleID"].duplicated().sum())
    checks["duplicate_appointment_ids"] = int(appointments["AppointmentID"].duplicated().sum())
    checks["duplicate_repair_order_ids"] = int(repair_orders["RepairOrderID"].duplicated().sum())
    checks["orphan_vehicles"] = int((~vehicles["CustomerID"].isin(customers["CustomerID"])).sum())
    checks["orphan_appointments_customers"] = int((~appointments["CustomerID"].isin(customers["CustomerID"])).sum())
    checks["orphan_appointments_vehicles"] = int((~appointments["VehicleID"].isin(vehicles["VehicleID"])).sum())
    checks["orphan_order_services"] = int((~services["RepairOrderID"].isin(repair_orders["RepairOrderID"])).sum())
    checks["orphan_service_technicians"] = int((~services["TechnicianID"].isin(technicians["TechnicianID"])).sum())
    checks["orphan_part_usage"] = int((~usage["PartID"].isin(parts["PartID"])).sum())
    checks["invalid_appointment_time_order"] = int((appointments["ScheduledEnd"] <= appointments["ScheduledStart"]).sum())
    checks["invalid_repair_completion_order"] = int((repair_orders["CompletedAt"].notna() & (repair_orders["CompletedAt"] < repair_orders["OpenedAt"])).sum())
    checks["completed_orders_without_timestamp"] = int(((repair_orders["OrderStatus"] == "Completed") & repair_orders["CompletedAt"].isna()).sum())
    checks["open_orders_with_completion_timestamp"] = int(((repair_orders["OrderStatus"] != "Completed") & repair_orders["CompletedAt"].notna()).sum())
    checks["nonpositive_part_quantities"] = int((usage["QuantityUsed"] <= 0).sum())
    checks["negative_money_values"] = int((repair_orders[["LaborSubtotal", "PartsSubtotal", "TaxAmount", "TotalAmount"]].lt(0)).sum().sum())
    checks["invalid_time_log_order"] = int((logs["EndTime"].notna() & (logs["EndTime"] <= logs["StartTime"])).sum())
    checks["invalid_shortage_resolution_order"] = int((shortages["ResolvedAt"].notna() & (shortages["ResolvedAt"] < shortages["ReportedAt"])).sum())

    log_order = logs.dropna(subset=["EndTime"]).sort_values(["TechnicianID", "StartTime", "TimeLogID"]).copy()
    log_order["PreviousEndTime"] = log_order.groupby("TechnicianID")["EndTime"].shift(1)
    checks["overlapping_technician_logs"] = int((log_order["StartTime"] < log_order["PreviousEndTime"]).sum())

    vehicle_owner = vehicles.set_index("VehicleID")["CustomerID"]
    expected_owner = appointments["VehicleID"].map(vehicle_owner)
    checks["appointment_vehicle_owner_mismatch"] = int((appointments["CustomerID"] != expected_owner).sum())

    expected_total = repair_orders["LaborSubtotal"] + repair_orders["PartsSubtotal"] + repair_orders["TaxAmount"]
    checks["repair_order_total_mismatch"] = int(((repair_orders["TotalAmount"] - expected_total).abs() > 0.02).sum())

    labor_by_order = services.groupby("RepairOrderID")["LaborAmount"].sum()
    expected_labor = repair_orders["RepairOrderID"].map(labor_by_order)
    checks["repair_order_labor_mismatch"] = int(((repair_orders["LaborSubtotal"] - expected_labor).abs() > 0.02).sum())

    usage["ExtendedPrice"] = usage["QuantityUsed"] * usage["UnitPrice"]
    parts_by_order = usage.groupby("RepairOrderID")["ExtendedPrice"].sum()
    expected_parts = repair_orders["RepairOrderID"].map(parts_by_order)
    checks["repair_order_parts_mismatch"] = int(((repair_orders["PartsSubtotal"] - expected_parts).abs() > 0.02).sum())

    result = {
        "status": "PASS" if sum(checks.values()) == 0 else "FAIL",
        "total_issues": int(sum(checks.values())),
        "checks": checks,
    }
    (FINDINGS / "data_quality_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
