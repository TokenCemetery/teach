---
title: Dimensional Modelling
description: the four design steps, schema shapes and the slowly changing dimension types
type: reference
---

# Dimensional Modelling

Stage 5 compressed for lookup: [lesson 11](../lessons/0011-facts-dimensions-and-the-grain.md) (the grain, fact table types, surrogate and conformed keys), [lesson 12](../lessons/0012-star-schemas-wide-tables-and-nesting.md) (schema shapes on a columnar warehouse) and [lesson 13](../lessons/0013-slowly-changing-dimensions.md) (slowly changing dimensions).

## The four design steps

Decided in this order, from the Kimball Group's [Four-Step Dimensional Design Process](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/four-4-step-design-process/):

| Step | Decide | Test |
|---|---|---|
| 1. Business process | The activity that produces measurements: an order, a shipment, a payment, a stock count | It is something the organization does, not a department or a report |
| 2. Grain | What exactly one fact row represents, as one sentence | A colleague could check any row against the sentence |
| 3. Dimensions | The descriptive context: who, what, where, when | Each has exactly one value per fact row at the grain |
| 4. Facts | The numeric measurements | Each is true at the grain, not at a coarser or finer one |

## Grain checklist

- [ ] Written as a sentence: "One row per ... , recorded when ... ".
- [ ] Names the thing one row is about and which events become rows.
- [ ] Atomic (the lowest level the process captures) unless a summary grain is a deliberate addition alongside it.
- [ ] Every fact is true at this grain. A value belonging to a coarser grain (an order's shipping fee on order lines) is moved to its own fact table or allocated by a stated rule.
- [ ] Every dimension has one value per row.
- [ ] One grain per table. Mixed grains go in separate fact tables that share conformed dimensions.
- [ ] The columns that should be unique at the grain are listed, and a `GROUP BY ... HAVING COUNT(*) > 1` test runs after every load. No platform enforces it for you (below).

## Fact table types

From the Kimball Group's [technique index](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/):

| Type | Grain | Rows after insert | Typical measures | Example |
|---|---|---|---|---|
| Transaction | One event at one instant | Never updated | Additive amounts and quantities | One order line |
| Periodic snapshot | One entity per fixed period | One new row per period, even with no activity | Levels and balances (semi-additive) | Stock per product per store per day |
| Accumulating snapshot | One instance of a process with fixed milestones | Updated as each milestone is reached | Milestone dates, lags between them | One order from placed to delivered |

## Measure additivity

| Kind | Sums across | Example | Rule |
|---|---|---|---|
| Additive | Every dimension | Sale amount, units | Sum freely |
| Semi-additive | Some dimensions, never time | Account balance, stock on hand | Across time take the period's last value or an average, never a sum |
| Non-additive | Nothing | Margin percent, unit price | Store the additive parts, sum them, divide last |

## Keys

| Key | What it is | Where it lives |
|---|---|---|
| Surrogate key | A meaningless integer or hash the warehouse assigns, one per dimension row (one per version under type 2) | Dimension key, and the fact table's foreign key |
| Natural key | The source system's identifier, such as a customer number | Dimension attribute; the same across every version |
| Date key | The date itself, the usual exception to surrogate keys | Date dimension and fact |

How each platform generates a surrogate key, and whether it enforces keys:

| Platform | Generating a surrogate key | Primary and foreign keys enforced? |
|---|---|---|
| BigQuery | No auto-increment; `GENERATE_UUID()` or a hash such as `FARM_FINGERPRINT` over the natural key and validity start | No; used by the optimizer to remove and reorder joins ([Primary and foreign keys](https://docs.cloud.google.com/bigquery/docs/primary-foreign-keys)) |
| Snowflake | `IDENTITY` or `AUTOINCREMENT` column, or a sequence; unique, not gap-free | No on standard tables; `NOT NULL` and `CHECK` are enforced |
| Redshift | `IDENTITY` column; unique, not guaranteed consecutive | No; informational, but the planner trusts them, so an invalid key can return wrong results ([Table constraints](https://docs.aws.amazon.com/redshift/latest/dg/t_Defining_constraints.html)) |

A **conformed dimension** has the same keys and attribute values in every fact table that uses it, so results from separate fact tables line up on its attributes (drilling across). Never join two fact tables row to row.

## Schema shapes on a columnar warehouse

| Shape | Layout | Fits when | Costs |
|---|---|---|---|
| Star | Fact with surrogate keys, one denormalized table per dimension | The default. Dimensions are small enough to broadcast, or change after facts are written | A join per dimension, cheap when broadcast |
| Snowflake | Dimensions normalized into further tables | Rarely. Kimball advises avoiding it ([Snowflaked Dimensions](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/snowflake-dimension/)) | Extra joins; the storage it saves is mostly saved by compression already |
| One wide table | Dimension attributes copied onto every fact row | Attributes never change after the fact is written, or the table is rebuilt every run; a large dimension that would otherwise shuffle | Each attribute change rewrites blocks across every partition holding that value |
| Nested (`STRUCT`, `ARRAY`) | Child rows or attributes stored inside the parent row | BigQuery; children always read with the parent and rarely changed, such as lines of an order | A second grain inside the table (double counting after `UNNEST`); a change rewrites the whole parent row; at most 15 nesting levels ([Use nested and repeated fields](https://cloud.google.com/bigquery/docs/nested-repeated)) |

The three mechanics behind the table:

- Columns a query does not reference cost nothing, so width alone costs nothing.
- A join moves rows unless one side is small enough to broadcast (BigQuery broadcast join, Redshift `DISTSTYLE ALL`, Snowflake's optimizer choice). Large-to-large joins shuffle both sides.
- Columnar blocks are rewritten, not edited, so a value copied onto many rows multiplies the cost of changing it.

On BigQuery on-demand, a repeated `STRING` costs 2 bytes plus its UTF-8 length per row, against 8 for an `INT64` key ([Data type sizes](https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/data-types)), so flattening a string onto the fact can scan more bytes than the star it replaces.

## Slowly changing dimension types

From the Kimball Group's [technique index](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/):

| Type | On a change | Last year's report by that attribute | Use for |
|---|---|---|---|
| 0 | Nothing; the original value is kept | Unchanged | Attributes labelled "original", most date attributes |
| 1 | Overwrite the value | Restated in today's terms | Corrections of wrong values; history nobody wants |
| 2 | Close the current row, add a new row with a new surrogate key | Unchanged: old facts point at the old version | History that reports must keep |
| 3 | Overwrite the value, keep the prior one in a `previous_` column | Restated, but the prior value is one column away | One planned change viewed both ways |
| 4 | Fast-changing attributes moved to a mini-dimension with its own key, stored on the fact | Unchanged for the banded attributes | Attributes that would make a type 2 dimension grow a version per change |
| 6 | Type 2 row plus a type 1 `current_` column overwritten on every version | Either view from one join | Reporting by value at the time and value now |

### Columns a type 2 dimension needs

| Column | Purpose |
|---|---|
| Surrogate key | One per version; what the fact stores |
| Natural key | Same across versions; finds and counts the entity |
| Attributes | The tracked (type 2) and overwritten (type 1) values |
| `valid_from` | Start of the version, inclusive |
| `valid_to` | End of the version, exclusive, equal to the next version's `valid_from`; null or 9999-12-31 for the current row (pick one per model) |
| `is_current` | Flag for today's version |

### Point-in-time join

Preferred: store the surrogate key on the fact at load time, and join on equality. Otherwise, join on the natural key and the interval:

```sql
JOIN dim_customer AS d
  ON  f.customer_id = d.customer_id
  AND f.event_at >= d.valid_from
  AND (f.event_at < d.valid_to OR d.valid_to IS NULL)
```

| Defect in the dimension | Effect on the join |
|---|---|
| Overlapping intervals for one natural key | The fact matches twice and is double counted |
| A gap between intervals | The fact matches nothing and an inner join drops it |
| Closed intervals (`<=` at both ends) | A fact at the exact change instant matches both versions |

### dbt snapshots

From [Snapshots](https://docs.getdbt.com/docs/build/snapshots), dbt 1.9 and later:

| Item | Value |
|---|---|
| Required config | `unique_key`, `strategy` (`timestamp` with `updated_at`, or `check` with `check_cols`) |
| Columns added | `dbt_valid_from`, `dbt_valid_to`, `dbt_scd_id`, `dbt_updated_at`; `dbt_is_deleted` with `hard_deletes: new_record` |
| Current row | `dbt_valid_to` is null, unless `dbt_valid_to_current` sets a value |
| Source deletes | `hard_deletes`: `ignore` (default), `invalidate`, `new_record` |
| Blind spot | Captures state at each run only; a change reverted between runs is never recorded |

## Sources

- [Docs: "Dimensional Modeling Techniques", Kimball Group](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
- [Docs: "Four-Step Dimensional Design Process", Kimball Group](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/four-4-step-design-process/)
- [Docs: "Declare the Grain", Kimball Group](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/grain/)
- [Docs: "Type 2: Add New Row", Kimball Group](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/type-2/)
- [Docs: "Use nested and repeated fields", Google Cloud](https://cloud.google.com/bigquery/docs/nested-repeated)
- [Docs: "Snapshots", dbt](https://docs.getdbt.com/docs/build/snapshots)
- [Resources](../RESOURCES.md)
