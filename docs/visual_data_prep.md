# Lakeflow Designer experiments

Use the `<cli-profile>` workspace after a successful baseline build and approval to create a visual data prep and its output. If **Visual data prep** is absent, record which menu or permission blocked the experiment.

## A. Consume an existing mart

1. Create a **Visual data prep** in a sandbox workspace folder. Add a **Source**, choose the Unity Catalog table `sandbox_catalog.dbt_lineage_poc.fct_sales`, and name the source `sales_source`.
2. Connect a **SQL** operator and enter:

   ```sql
   select category, sum(gross_amount) as total_revenue
   from sales_source
   group by category
   ```

3. Connect an **Output** operator. Choose a Unity Catalog table and set the catalog to `sandbox_catalog`, schema to `dbt_lineage_poc`, and name to `visual_daily_sales_poc`. Verify that name is unused before the first run. Never target a dbt relation or overwrite someone else's output.
4. Choose **Run all** and inspect the result. Compare it with the same aggregation in SQL Editor using the fully qualified `fct_sales` relation. In **Catalog**, open the output's **Lineage** tab and check for the source mart edge. Record the canvas, result and lineage separately.

## B. Reuse compiled SQL

1. Find `dbt_project/target/compiled/retail_lineage_poc/models/staging/stg_orders.sql` from the baseline build. If needed, run `dbt compile --select stg_orders --project-dir dbt_project --profiles-dir dbt_project` with the configured warehouse.
2. Use a separate canvas or disconnected branch with no Output operator. Add `raw_orders` from the same schema as a **Source** named `orders_source`. Connect a **SQL** operator and preview `select * from orders_source` as a control.
3. Paste the compiled `SELECT`, changing its fully qualified `raw_orders` reference to `orders_source`. Set preview to **All rows**. Compare all rows and columns with `stg_orders` in SQL Editor, ordered by `order_id`. Record edits, row counts and any differences.

### Parameterise a Unity Catalog table reference

In the canvas **Parameters** panel, add string parameters named `catalog` and `schema`. For the serverless POC, set their defaults to `sandbox_catalog` and `dbt_lineage_poc`. In a SQL operator, use:

```sql
select *
from identifier(concat(:catalog, '.', :schema, '.stg_orders'))
```

Preview and compare with the existing `stg_orders` view. This resolves a Unity Catalog object name at runtime. Connect a Source operator if you also want the input to appear as a node on the Designer canvas.

The [Designer parameter documentation](https://learn.microsoft.com/en-us/azure/databricks/designer/parameters) also supports binding a Source operator's **Table** field to a single parameter containing the fully qualified relation name. The documented visual prep import format is `.designer.ipynb`. The [native dbt task](https://learn.microsoft.com/en-us/azure/databricks/jobs/tasks/dbt) can refresh dbt models upstream of a Designer task in the same job.

## C. Check native dbt support

1. In the same preview-only SQL operator, try `select * from {{ ref('stg_orders') }}`, then `select {{ calculate_amount('quantity', '2.00') }} from orders_source`. Capture the exact responses.
2. Inspect the Designer creation/import menus and workspace documentation for a way to load `manifest.json` or an entire dbt project. If an importer exists, try it in a sandbox and record which resources and edges it recovers without rebuilding operators. If absent, record that it was unavailable in the tested workspace.
3. Select the `fct_sales` Source on the canvas. Check whether the canvas expands the complete dbt graph, including the ephemeral model, or shows the Source at the start of the Designer workflow. Compare the canvas with the Catalog Explorer lineage tab and dbt Docs.

[Create a visual data prep](https://learn.microsoft.com/azure/databricks/designer/build-transformation) · [Designer built-in operators](https://learn.microsoft.com/azure/databricks/designer/built-in-operators)

## Run the saved canvas as a Lakeflow Job

1. In **Jobs & Pipelines**, create a job and add one task of type **Visual data prep**.
2. Select the saved canvas as the source and choose the available Serverless jobs compute.
3. Confirm the canvas writes only to `visual_daily_sales_poc`. Save and click **Run now**.
4. Open the task run to see its operators. Compare the results with the baseline query and check the output table's **History** and **Lineage** tabs.

[Run a Designer canvas in a job](https://learn.microsoft.com/en-us/azure/databricks/designer/production)