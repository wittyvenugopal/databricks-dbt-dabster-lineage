# Policy lineage pilot

This standalone dbt project uses fictional customers, quotes and policies. Three seeds feed three staging views. `fct_policy` joins those views, matching the quote on both quote and customer ID. It contains one row per issued policy with IDs, coverage, effective date, status, currency, quoted premium and bound annual premium. The expected result is four policies. Tests cover keys, relationships, status values and policy-to-quote customer consistency.

## Set up from PowerShell

From the repository root, enter the lab and reuse the parent POC's environment:

```powershell
cd dbt-lineage-poc-pilot
..\.venv\Scripts\Activate.ps1
if (-not (Test-Path dbt_project/profiles.yml)) {
    Copy-Item dbt_project/profiles.yml.example dbt_project/profiles.yml
}
```

For an independent checkout, create a Python 3.11 virtual environment and install `requirements.txt` before copying the profile.

## Build on Databricks after approval

Choose a SQL warehouse and a separate schema for the pilot. Replace the connection placeholders and substitute your catalog for `sandbox_catalog` in the examples. In SQL Editor, create the schema if needed:

```sql
create schema if not exists sandbox_catalog.dbt_policy_lineage_pilot;
```

Configure the same PowerShell window using the CLI OAuth session:

```powershell
$env:DATABRICKS_HOST = '<workspace-hostname>'
$env:DATABRICKS_HTTP_PATH = '/sql/1.0/warehouses/<warehouse-id>'
$env:DATABRICKS_CATALOG = 'sandbox_catalog'
$env:DATABRICKS_SCHEMA = 'dbt_policy_lineage_pilot'
$env:DATABRICKS_AUTH_TYPE = 'pat'
$env:DATABRICKS_TOKEN = (databricks auth token '<cli-profile>' --output json |
    Out-String | ConvertFrom-Json).access_token
if (-not $env:DATABRICKS_TOKEN) { throw 'No CLI OAuth token was returned.' }
```

The SDK calls this bearer-token provider `pat`. The token above comes from the CLI OAuth session. For an offline parse, use host `example.invalid`, HTTP path `/sql/1.0/warehouses/offline` and token `offline-placeholder`.

```powershell
dbt parse --project-dir dbt_project --profiles-dir dbt_project
dbt debug --project-dir dbt_project --profiles-dir dbt_project
dbt build --project-dir dbt_project --profiles-dir dbt_project
Copy-Item dbt_project/target/run_results.json dbt_project/target/build_run_results.json
dbt docs generate --project-dir dbt_project --profiles-dir dbt_project
dbt docs serve --project-dir dbt_project --profiles-dir dbt_project --port 8081
```

Open **http://localhost:8081**, choose `fct_policy` and open its graph using the bottom-right button. In Databricks Catalog Explorer, open the same table's **Lineage** tab and compare the three upstream staging views. Inspect the four expected policies in SQL Editor with `select * from sandbox_catalog.dbt_policy_lineage_pilot.fct_policy order by policy_id`.

## Run locally through Dagster

From the same configured shell, run `dbt parse` again if the model definitions changed, then:

```powershell
New-Item -ItemType Directory -Force .dagster | Out-Null
$env:DAGSTER_HOME = (Resolve-Path .dagster).Path
dagster dev -f orchestration/definitions.py --host 127.0.0.1 --port 3002
```

Open **http://localhost:3002** → **Assets** to see the manifest-derived graph. Materialise `fct_policy` with its upstream assets to rebuild the pilot through Dagster. Check **Runs** and asset **Checks** for outcomes. The pilot keeps its run history in its own `.dagster` folder. Record observations in [FINDINGS.md](FINDINGS.md).
