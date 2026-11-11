"""Produce reproducible business findings from the generated portfolio data."""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "findings" / "analysis_findings.md"


def read(name: str, dates: list[str] | None = None) -> pd.DataFrame:
    frame = pd.read_csv(DATA / f"{name}.csv")
    for column in dates or []:
        frame[column] = pd.to_datetime(
            frame[column], format="mixed", dayfirst=True, errors="coerce"
        )
    return frame


def main() -> None:
    appointments = read("appointments", ["ScheduledStart"])
    orders = read("repair_orders", ["OpenedAt", "PromisedAt", "CompletedAt"])
    services = read("repair_order_services")
    service_types = read("service_types")
    shortages = read("parts_shortages")
    parts = read("parts")
    shifts = read("technician_shifts")
    logs = read("technician_time_logs")
    technicians = read("technicians")

    appointments["Weekday"] = appointments["ScheduledStart"].dt.day_name()
    weekday = appointments.groupby("Weekday").size().sort_values(ascending=False)

    completed = orders.dropna(subset=["CompletedAt"]).copy()
    completed["TurnaroundHours"] = (completed["CompletedAt"] - completed["OpenedAt"]).dt.total_seconds() / 3600
    completed["CompletedOnTime"] = completed["CompletedAt"] <= completed["PromisedAt"]
    completed["HadShortage"] = completed["RepairOrderID"].isin(set(shortages["RepairOrderID"]))
    impact = completed.groupby("HadShortage").agg(
        CompletedOrders=("RepairOrderID", "count"),
        AverageTurnaroundHours=("TurnaroundHours", "mean"),
        OnTimeRate=("CompletedOnTime", "mean"),
    )

    shortage_detail = shortages.merge(parts[["PartID", "PartNumber", "PartName"]], on="PartID")
    shortage_rank = shortage_detail.groupby(["PartNumber", "PartName"]).agg(
        Events=("ShortageID", "count"),
        TotalDelayHours=("DelayHours", "sum"),
    ).sort_values(["TotalDelayHours", "Events"], ascending=False)

    service_rank = services.merge(service_types[["ServiceTypeID", "ServiceName"]], on="ServiceTypeID")
    service_rank = service_rank.groupby("ServiceName").agg(
        ServiceCount=("RepairOrderServiceID", "count"),
        AverageActualHours=("ActualHours", "mean"),
        LaborRevenue=("LaborAmount", "sum"),
    ).sort_values("ServiceCount", ascending=False)

    shifts["ShiftStartDT"] = pd.to_datetime(shifts["ShiftDate"] + " " + shifts["ShiftStart"])
    shifts["ShiftEndDT"] = pd.to_datetime(shifts["ShiftDate"] + " " + shifts["ShiftEnd"])
    shifts["ScheduledHours"] = (shifts["ShiftEndDT"] - shifts["ShiftStartDT"]).dt.total_seconds() / 3600
    scheduled = shifts.groupby("TechnicianID")["ScheduledHours"].sum()
    logged = logs.groupby("TechnicianID")["HoursWorked"].sum()
    utilization = technicians[["TechnicianID", "FirstName", "LastName", "SkillLevel"]].copy()
    utilization["Technician"] = utilization["FirstName"] + " " + utilization["LastName"]
    utilization["ScheduledHours"] = utilization["TechnicianID"].map(scheduled).fillna(0)
    utilization["LoggedHours"] = utilization["TechnicianID"].map(logged).fillna(0)
    utilization["UtilizationRate"] = utilization["LoggedHours"] / utilization["ScheduledHours"]
    utilization = utilization.sort_values("UtilizationRate", ascending=False)

    no_shortage = impact.loc[False]
    with_shortage = impact.loc[True]
    top_part = shortage_rank.iloc[0]
    top_part_name = shortage_rank.index[0][1]
    top_service = service_rank.iloc[0]
    top_service_name = service_rank.index[0]
    top_tech = utilization.iloc[0]
    completed_revenue = completed["TotalAmount"].sum()
    completed_average_ticket = completed["TotalAmount"].mean()

    content = f"""# Analysis Findings

All figures below come from a deterministic, synthetic 2025 dataset created for the fictional Ottawa business Quazar Auto Care. They do not represent real customers or company performance.

## Executive Summary

- The dataset contains **{len(appointments):,} appointments** and **{len(orders):,} repair orders**, including **{len(completed):,} completed orders**.
- Completed-order revenue is **${completed_revenue:,.2f}**, with an average completed ticket of **${completed_average_ticket:,.2f}**. These are the values used on the Power BI overview page.
- Total recorded order value, including non-completed orders, is **${orders['TotalAmount'].sum():,.2f}**.
- **{weekday.index[0]}** is the busiest booking day with **{int(weekday.iloc[0]):,} appointments**.
- Completed jobs average **{completed['TurnaroundHours'].mean():.2f} hours** of turnaround time; the median is **{completed['TurnaroundHours'].median():.2f} hours**.
- The overall on-time completion rate is **{completed['CompletedOnTime'].mean() * 100:.2f}%**.
- The most common service is **{top_service_name}** with **{int(top_service['ServiceCount']):,} service lines**.

## Parts Shortage Impact

- Completed orders without a recorded shortage average **{no_shortage['AverageTurnaroundHours']:.2f} hours** and have an on-time rate of **{no_shortage['OnTimeRate'] * 100:.2f}%**.
- Completed orders with a shortage average **{with_shortage['AverageTurnaroundHours']:.2f} hours** and have an on-time rate of **{with_shortage['OnTimeRate'] * 100:.2f}%**.
- The highest-delay part is **{top_part_name}**, linked to **{int(top_part['Events'])} shortage events** and **{top_part['TotalDelayHours']:.0f} total delay hours**.

## Technician Capacity

- The highest recorded utilization belongs to **{top_tech['Technician']}** at **{top_tech['UtilizationRate'] * 100:.2f}%** of scheduled hours.
- Utilization is direct logged repair time divided by scheduled shift time; administrative work and idle time are excluded.

## Recommendations

1. Review Friday staffing and appointment-slot capacity because Friday has the highest booking volume.
2. Raise or dynamically review reorder points for brake pads and other parts producing the greatest accumulated delay.
3. Monitor service-level actual-versus-standard hours and revise estimates where the variance persists.
4. Use technician utilization together with service mix, not alone, when adjusting schedules or assigning training.
5. Track on-time completion and shortage-related turnaround monthly after inventory-policy changes.

## Limitations

- All records are synthetic and were generated using explicit business assumptions.
- The dataset models one location and one year, so it does not establish causal relationships.
- Technician utilization captures logged repair time only and does not represent total productivity.
- Shortage delays were simulated to support operational analysis and should not be interpreted as real benchmarks.
"""
    OUTPUT.write_text(content, encoding="utf-8")
    print(content)


if __name__ == "__main__":
    main()
