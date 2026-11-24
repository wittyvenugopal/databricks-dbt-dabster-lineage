# Verified findings

The diagrams are redrawn from observed graphs using the generic catalog name `sandbox_catalog`.

## dbt and Unity Catalog

The retail baseline built three seed tables, three staging views and three marts. All 19 tests passed. dbt Docs showed the ephemeral `int_order_details` as a parent of `fct_sales`. After metadata access was granted, Catalog Explorer showed direct edges from the three staging views. System lineage tables were unavailable to the test identity. Column-level mappings and the exact privilege grants remain unverified.

```mermaid
flowchart LR
    subgraph dbt["dbt Docs"]
      S["Three staging views"] --> I["int_order_details (ephemeral)"] --> F["fct_sales"]
    end
    subgraph uc["Unity Catalog · sandbox_catalog"]
      O["stg_orders"] --> U["fct_sales"]
      C["stg_customers"] --> U
      P["stg_products"] --> U
    end
```

![dbt Docs table details for fct_sales using sandbox_catalog](docs/screenshots/dbt-docs-fct-sales.png)

![dbt Docs lineage for the ephemeral parent of fct_sales](docs/screenshots/dbt-docs-lineage.png)

## Lakeflow Designer

```mermaid
flowchart LR
    A["sales_source · 12 rows"] --> B["sales_revenue · 3 rows"] --> C["visual_daily_sales_poc · 3 rows"]
```

Designer read the dbt-built mart and wrote a separate table. The Lakeflow Job showed all three operators succeeding. Delta history confirmed the job write. Catalog Explorer showed the saved canvas and job as producers after metadata access was granted. The direct source-to-output table edge remains unverified.

| Category | Verified revenue |
|---|---:|
| Accessories | 52.50 |
| Home | 69.75 |
| Stationery | 63.00 |

A parameterized reference successfully read a dbt-built view. A SQL preview with raw dbt `ref()` failed with an unresolved template expression. The documented import format is `.designer.ipynb`. Compiled SQL parity, macro evaluation and workspace import probes remain open.

## Native dbt job and Dagster

| Experiment | Verified result |
|---|---|
| Native Lakeflow dbt job | One task, nine successful resources and 19 tests passing. The artifact archive included `manifest.json` and `run_results.json`. |
| Dagster full build | Nine asset materializations and 19 passing checks. |
| Dagster selective build | Selecting `fct_sales` and its upstream assets yielded seven materializations and 15 passing checks. |
| Dagster failure | An invalid column in `stg_orders` failed the run. Independent branches materialized, and all three marts skipped. |
| Dagster recovery | The original SQL materialized all nine assets and passed all 19 checks. |

## Reproduce the checks

- [ ] Build the retail project and inspect dbt Docs.
- [ ] Check table and column lineage in Catalog Explorer.
- [ ] Run the Designer canvas, compare values, and inspect the producers.
- [ ] Compare the native dbt job and local Dagster.
- [ ] Try the [policy lab](dbt-lineage-poc-pilot/README.md).