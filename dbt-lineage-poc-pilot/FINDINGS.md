# Policy pilot findings

- [x] Validate the local dbt manifest and Dagster asset graph.
- [ ] After approval, create the dedicated schema and run the dbt baseline.
- [ ] Inspect dbt Docs and compare its graph with Catalog Explorer lineage for `fct_policy`.
- [ ] Materialise `fct_policy` and its upstream assets from Dagster and inspect asset checks.

## Expected behaviour

Three seed tables feed three staging views. The views join into a four-row policy fact table. The unconverted quote is absent and the cancelled policy is retained. Policy 302 illustrates a bound premium that differs from its quoted premium. Premiums retain their currency and should only be aggregated within a currency or after conversion.

## Verified locally

Offline dbt parse passed. Dagster loaded seven assets and 17 check definitions. Both graphs show `fct_policy` depending on all three staging views. The seed keys and all four policy joins were checked locally. Databricks execution and runtime lineage are pending.
