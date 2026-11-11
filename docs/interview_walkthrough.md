# Interview Walkthrough

## 60-Second Summary

I built a SQL Server portfolio project for a fictional Ottawa automotive service business called Quazar Auto Care. I created a normalized 12-table database covering customers, vehicles, appointments, repair orders, technicians, time logs, services, parts usage and shortages. I generated one year of clearly labeled synthetic data, validated relationships and business rules, then used joins, aggregations, CTEs and window functions to analyze demand, turnaround time, technician capacity and shortage delays. I also created reporting views and a Power BI dashboard plan so the analysis could be reused by managers.

## Business Problem

The shop needs one consistent way to answer:

- When is demand highest?
- Which services consume the most time?
- Are repair orders completed by the promised time?
- How much delay is associated with parts shortages?
- Are scheduled technician hours aligned with recorded repair time?
- Which inventory settings should management review?

## Technical Decisions to Explain

1. **Separate appointments from repair orders.** An appointment represents planned demand, while a repair order represents work that entered the shop.
2. **Use bridge tables.** RepairOrderServices handles multiple services per order, and PartUsage handles multiple parts per order.
3. **Keep time logs separate.** This permits comparison between assigned services, scheduled shifts and actual recorded labor.
4. **Preserve transaction prices.** PartUsage stores the cost and selling price used at the time instead of depending only on the current Parts table.
5. **Add constraints and indexes.** Primary keys, foreign keys, checks, unique constraints and targeted indexes protect data quality and improve common filters and joins.
6. **Create reporting views.** Views centralize repeated KPI logic and provide Power BI with stable, understandable datasets.

## Validation Story

Before loading SQL Server, a Python validation script checks duplicate identifiers, orphaned relationships, invalid timestamps, nonpositive quantities, negative monetary values, overlapping technician logs, customer-vehicle ownership and financial reconciliation. The generated dataset passes all checks with zero issues. SQL Server checks repeat important controls after the load.

## SQL Skills Demonstrated

- Inner and left joins across operational tables
- Aggregation and conditional aggregation
- Common table expressions
- Window functions including `LAG`, `DENSE_RANK`, rolling sums and `PERCENTILE_CONT`
- Reusable views for reporting
- Primary keys, foreign keys, unique constraints and check constraints
- Indexes designed around date, status, technician, service and part analysis

## Findings to Discuss

- Friday has the highest booking volume.
- Parts shortages are associated with much longer average turnaround and lower on-time completion in the synthetic scenario.
- Front brake pads create the greatest accumulated shortage delay.
- Oil changes are the highest-volume service.
- Technician utilization is intentionally defined as direct logged repair time divided by scheduled shift time, not as a complete productivity measure.

## Honest Limitations

- The data is synthetic and intentionally shaped to demonstrate operational analysis.
- One location and one year are not enough to establish causation or seasonality across years.
- The utilization KPI excludes administrative, training and other indirect work.
- Recommendations should be tested using real inventory costs, service levels and supplier performance before implementation.

## Likely Interview Questions

**Why SQL Server?**  
It demonstrates relational design, T-SQL analysis and a realistic connection to Power BI.

**Why not put everything in one table?**  
That would duplicate customers, vehicles, services and parts, making updates inconsistent and analysis less reliable.

**What was the most important validation?**  
Cross-table reconciliation: ensuring repair-order labor and part subtotals equal their detailed service and usage rows.

**What would you add with real company data?**  
Supplier purchase orders, inventory receipts, warranty claims, customer satisfaction, bay capacity and labor categories for indirect time.

