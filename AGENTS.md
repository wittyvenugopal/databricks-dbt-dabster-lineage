# dbt + Databricks + Dagster Lineage POC

## Objective

Build a small, lean proof of concept to evaluate how an existing dbt project running on Databricks can expose model dependencies, data lineage, execution status and orchestration through:

1. Native dbt Docs.
2. Databricks Unity Catalog Lineage.
3. Databricks Lakeflow Designer / Visual Data Prep.
4. Dagster with native dbt integration.
5. Databricks Lakeflow Jobs using a standard dbt build task.

The primary objective is to evaluate these capabilities without refactoring dbt models into Databricks notebooks or duplicating transformation logic.

## Technical constraints

- Use dbt Core and dbt-databricks.
- Use Databricks SQL Warehouse and Unity Catalog.
- Use Python 3.11 with a virtual environment, subject to package compatibility.
- Use small, static CSV datasets.
- Run Dagster locally.
- Keep all dbt models in a single dbt project.
- Use environment variables for authentication and connection configuration.
- Never hardcode credentials.
- Use a dedicated sandbox schema.
- No Docker, Kubernetes, Terraform, cloud deployment or CI/CD.
- No custom frontend or lineage application initially.
- Avoid unnecessary abstractions and overengineering.
- Select compatible package versions and document the tested versions.

## Phase 1 — Build a sample dbt project

Create a retail analytics dbt project called retail_lineage_poc.

Create three CSV seed files:

### raw_customers.csv

Columns:

- customer_id
- customer_name
- country

Generate five fictional customers.

### raw_products.csv

Columns:

- product_id
- product_name
- category
- unit_price

Generate five fictional products.

### raw_orders.csv

Columns:

- order_id
- customer_id
- product_id
- order_date
- quantity
- order_status

Generate 20 fictional orders across multiple customers, products and dates. Include completed, pending and cancelled orders.

Ensure the sample data is deterministic, and all foreign keys are valid.

## Phase 2 — Create dbt models

Create the following models using dbt ref() dependencies.

### Staging layer — materialised as views

- stg_customers: clean customer information.
- stg_products: clean product information and cast unit_price to decimal.
- stg_orders: cast dates and quantities and standardise order statuses.

### Intermediate layer — materialised as ephemeral

- int_order_details: join stg_orders, stg_customers and stg_products. Calculate gross_amount as quantity multiplied by unit_price.

### Mart layer — materialised as tables

- fct_sales: select completed orders from int_order_details.
- dim_customers: use stg_customers and int_order_details to calculate completed order count and lifetime customer spend.
- daily_revenue: use int_order_details to calculate completed daily order count and revenue.

This dependency structure must demonstrate branching, multiple upstream dependencies and an ephemeral model.

Add one simple dbt macro for calculating the sales amount and use it within int_order_details.

Add model descriptions and basic dbt tests:

- Unique order IDs.
- Unique customer IDs.
- Unique product IDs.
- Not-null primary keys.
- Customer and product relationships.
- Accepted values for order_status.

Add a singular test validating that completed order quantities are positive.

Keep the SQL straightforward and readable.

## Phase 3 — Databricks configuration

Create a profiles.yml example using environment variables:

- DATABRICKS_HOST
- DATABRICKS_HTTP_PATH
- DATABRICKS_TOKEN
- DATABRICKS_CATALOG
- DATABRICKS_SCHEMA

Use an existing authorised Unity Catalog sandbox catalog and a dedicated schema named dbt_lineage_poc.

Support personal access token authentication for the POC only where permitted by the organisation. Document OAuth as an alternative.

Create an .env.example containing placeholders only.

Ensure the actual .env file is excluded from Git.

Document how to configure the connection and execute:

```bash
dbt debug
dbt parse
dbt build
dbt docs generate
dbt docs serve
```

Use the appropriate project and profiles directories.

Ensure dbt build includes the seeds, models and tests.

Do not require Databricks notebooks for transformation execution.

## Phase 4 — dbt lineage and artifacts

Generate and explain:

- target/manifest.json
- target/run_results.json
- target/catalog.json

Document how to open dbt Docs and inspect the complete dependency DAG.

Explain how to inspect a model's upstream and downstream dependencies.

Create a small optional Python script called inspect_manifest.py that reads manifest.json and prints each model and its declared dependencies.

Use only the Python standard library for this script.

Do not build a custom graphical viewer.

## Phase 5 — Unity Catalog lineage validation

Create a SQL file containing queries to inspect:

- system.access.table_lineage
- system.access.column_lineage

Filter lineage queries to the configured sandbox catalog and schema.

Provide instructions to manually open Catalog Explorer and inspect the lineage of fct_sales, dim_customers and daily_revenue.

Document the expected differences between:

- Logical dbt dependencies from manifest.json.
- Physical lineage captured by Databricks.
- Ephemeral models.
- Views versus tables.
- dbt tests and macros.
- Column-level lineage.

Do not claim that Unity Catalog exposes the complete dbt project DAG.

Record what can actually be observed during testing.

## Phase 6 — Databricks Visual Data Prep experiment

Create a markdown guide explaining how to perform the following experiments manually in Lakeflow Designer.

Experiment A — Existing dbt outputs:

1. Create a new Visual Data Prep file.
2. Add fct_sales as an existing Unity Catalog Source.
3. Add a filter or SQL operator.
4. Calculate revenue grouped by product category.
5. Add an Output operator to create a separate table named visual_daily_sales_poc.
6. Run the complete visual data prep.
7. Inspect the resulting Unity Catalog lineage.

Experiment B — Reuse compiled dbt SQL:

1. Locate the compiled SQL for a simple dbt model.
2. Add the required upstream tables as Source operators.
3. Paste or adapt the compiled SELECT statement into a SQL operator.
4. Use the Source operator names where required.
5. Compare the results with the original dbt model.

Experiment C — Native dbt dependency support:

1. Investigate whether Visual Data Prep can import manifest.json.
2. Investigate whether it can resolve dbt ref(), Jinja and macros natively.
3. Investigate whether selecting an existing dbt-generated table reveals the complete upstream dbt DAG within the Designer canvas.
4. Investigate whether a complete dbt project can be imported without recreating individual operators.

Mark unsupported or unavailable capabilities clearly.

Do not invent undocumented APIs or claim successful integration without evidence.

Never overwrite existing dbt-generated tables.

The objective is to establish whether Visual Data Prep can consume existing dbt outputs or whether it can genuinely understand and visualise an existing dbt project.

## Phase 7 — Dagster integration

Create the simplest possible local Dagster integration using dagster, dagster-webserver and dagster-dbt.

Use the same existing dbt project and the same Databricks connection.

Use native dbt asset integration through either the supported dbt_assets decorator or the current lightweight equivalent.

Requirements:

- Load model dependencies from manifest.json.
- Automatically represent supported dbt resources as Dagster assets.
- Execute dbt build against Databricks.
- Stream dbt execution events into Dagster.
- Support model selection.
- Expose supported dbt tests as asset checks.
- Do not manually recreate the dependency graph.
- Do not copy dbt SQL into Python.
- Do not introduce additional databases or orchestration infrastructure.

Provide instructions to start the local Dagster UI.

Demonstrate:

1. Viewing the generated asset graph.
2. Viewing upstream and downstream dependencies.
3. Materialising all dbt assets.
4. Materialising a selected model with its upstream dependencies.
5. Inspecting execution status.
6. Inspecting asset checks.
7. Introducing a temporary failure and observing downstream behaviour.
8. Restoring the model and rerunning it.

Explain how Dagster can display the logical asset graph from dbt metadata before taking ownership of execution.

Explain how actual execution history differs between externally executed dbt builds and Dagster-managed builds.

Avoid concurrent execution of the Databricks Job and Dagster against the same schema.

## Phase 8 — Databricks native job experiment

Create a short guide to manually configure a Databricks Lakeflow Job containing a single native dbt task.

Use the same dbt project.

Configure the task to run:

```bash
dbt build
```

Document how to inspect job execution, available dbt artifacts and task-level visibility.

Compare its graph with the dbt Docs and Dagster asset graphs.

Do not create one Databricks task per dbt model.

## Phase 9 — Findings

Create FINDINGS.md containing a comparison matrix for:

- dbt Docs
- Unity Catalog
- Lakeflow Designer / Visual Data Prep
- Databricks Lakeflow Jobs
- Dagster

Compare the following:

- Logical model dependency DAG.
- Table-level lineage.
- Column-level lineage.
- Ephemeral model visibility.
- Model execution status.
- Test visibility.
- Selective execution.
- Failure and downstream dependency visibility.
- Ability to reuse the existing dbt project.
- Additional infrastructure.
- Integration effort.
- Whether SQL refactoring is required.

Separate expected behaviour from verified observations.

Include placeholders for screenshots and actual findings.

## Deliverables

Create a minimal runnable repository containing:

- Sample CSV seed files.
- dbt models and tests.
- One reusable macro.
- dbt_project.yml.
- profiles.yml.example.
- .env.example.
- requirements.txt.
- .gitignore.
- A minimal Dagster definitions file.
- Unity Catalog lineage SQL queries.
- Optional manifest inspection script.
- README.md with step-by-step setup.
- FINDINGS.md.
- A short manual Visual Data Prep guide.
- A short manual Databricks Jobs guide.

## Execution approach

First scaffold the repository and implement the dbt project.

Then implement the minimal Dagster integration.

Validate local configuration and parsing wherever possible.

If Databricks credentials are unavailable, complete the code and provide exact instructions for running the remote validation. Do not claim remote tests passed.

Review the repository for unnecessary complexity and remove anything that does not directly support the POC objectives.

Prioritise a working, understandable demonstration over production readiness.