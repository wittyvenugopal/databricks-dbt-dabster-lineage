from pathlib import Path

from dagster import AssetExecutionContext, Definitions
from dagster_dbt import DbtCliResource, dbt_assets


DBT_PROJECT = Path(__file__).resolve().parents[1] / "dbt_project"


@dbt_assets(manifest=DBT_PROJECT / "target" / "manifest.json")
def policy_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()


defs = Definitions(
    assets=[policy_dbt_assets],
    resources={"dbt": DbtCliResource(project_dir=DBT_PROJECT, profiles_dir=DBT_PROJECT)},
)
