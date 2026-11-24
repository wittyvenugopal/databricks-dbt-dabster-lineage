# Native Lakeflow Jobs experiment

Create the job only after approval. Use the same SQL warehouse, catalog and dedicated schema as the baseline. Keep local dbt and Dagster idle during the job run.

1. Make the same project revision available as a workspace folder or through an approved Git provider. For a workspace copy, upload the `dbt_project` source only, excluding the local `profiles.yml`, targets, logs and credentials. For Git, point the job at the approved revision and use project directory `dbt_project`.
2. In the workspace for `<cli-profile>`, open **Jobs & Pipelines**, create a job named `retail-lineage-poc` and add one task named `dbt_build` with type **dbt**. Choose the workspace project folder or the Git provider source from step 1.
3. Replace the default commands with a single `dbt build`. Choose the approved Pro or Serverless SQL warehouse, set **Warehouse catalog** to `sandbox_catalog` and **Warehouse schema** to `dbt_lineage_poc`. Use the task's generated profile.
4. Choose an approved **dbt CLI compute** option. Under its environment dependencies or libraries, pin `dbt-databricks==1.10.15` and `dbt-core==1.10.15` to match the local requirements. Confirm that the **Run as** identity can use the warehouse and read, create and update the POC relations, including those created by the baseline.
5. Save the task without a schedule and select **Run now**. Open the run, then the dbt task. Inspect task status and dbt logs, then download available dbt artifacts. Look for `manifest.json` and `run_results.json` and record what the UI exposes. The command does not request Docs generation, so treat `catalog.json` as outside this run's expected artifacts.
6. Compare the single task node and its run status with the models in dbt Docs and the assets, events and checks in Dagster. Record per-model statuses from the logs or artifacts and the run ID in [FINDINGS.md](../FINDINGS.md).

[Configure an Azure Databricks dbt task](https://learn.microsoft.com/en-us/azure/databricks/jobs/tasks/dbt)
