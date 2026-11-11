# Analysis Findings

All figures below come from a deterministic, synthetic 2025 dataset created for the fictional Ottawa business Quazar Auto Care. They do not represent real customers or company performance.

## Executive Summary

- The dataset contains **1,800 appointments** and **1,513 repair orders**, including **1,476 completed orders**.
- Completed-order revenue is **$465,049.53**, with an average completed ticket of **$315.07**. These are the values used on the Power BI overview page.
- Total recorded order value, including non-completed orders, is **$476,257.64**.
- **Friday** is the busiest booking day with **410 appointments**.
- Completed jobs average **4.93 hours** of turnaround time; the median is **2.89 hours**.
- The overall on-time completion rate is **77.37%**.
- The most common service is **Oil Change** with **485 service lines**.

## Parts Shortage Impact

- Completed orders without a recorded shortage average **3.89 hours** and have an on-time rate of **81.00%**.
- Completed orders with a shortage average **24.03 hours** and have an on-time rate of **10.53%**.
- The highest-delay part is **Front Brake Pad Set A**, linked to **19 shortage events** and **450 total delay hours**.

## Technician Capacity

- The highest recorded utilization belongs to **Renee Chen** at **23.02%** of scheduled hours.
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
