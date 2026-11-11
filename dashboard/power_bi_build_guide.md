# Power BI Dashboard Build Guide

## Data Connection

Connect to the `AutomotiveServiceOperations` SQL Server database and import:

- `vw_RepairOrderPerformance`
- `vw_DailyBookings`
- `vw_ServicePerformance`
- `vw_TechnicianUtilization`
- `vw_PartsShortageImpact`

Create the Calendar table and measures in `power_bi_measures.dax`. Relate Calendar[Date] to the date used by the reporting view. Keep the model single-directional unless a visual has a verified need for another filter path.

## Page 1: Operations Overview

KPI cards:

- Total Revenue
- Completed Orders
- Average Ticket
- Average Turnaround Hours
- On-Time Completion %
- Parts Shortage Rate

Visuals:

1. Line chart: repair orders and revenue by month.
2. Clustered column chart: completed orders by weekday.
3. Bar chart: top services by service count.
4. Donut chart: appointment status distribution.
5. Slicers: month, priority, vehicle make and order status.

## Page 2: Parts and Delays

Visuals:

1. Bar chart: total delay hours by part.
2. Scatter plot: shortage events versus average delay hours.
3. Table: part number, part name, stock on hand, reorder level, supplier lead days and shortage events.
4. Column chart: average turnaround with and without a shortage.
5. Conditional formatting: highlight stock at or below reorder level.

## Page 3: Technician Capacity

Visuals:

1. Bar chart: utilization rate by technician.
2. Clustered bar chart: scheduled hours versus logged hours.
3. Matrix: technician by service category and actual hours.
4. Table: technician, skill level, scheduled hours, logged hours and utilization.

## Formatting Standard

- Use a dark navy or charcoal background with high-contrast white text.
- Use blue for neutral operational measures, green for on-time performance and orange/red for shortage or delay measures.
- Display currency as Canadian dollars, rates as percentages and hours with one decimal place.
- Sort month labels by Month Number and weekday labels by Weekday Number.
- Add a visible note: `Synthetic portfolio data - Quazar Auto Care, Ottawa, 2025`.

