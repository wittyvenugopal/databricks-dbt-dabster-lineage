from os import environ
from pathlib import Path

from dagster import AssetExecutionContext, Definitions
from dagster_dbt import DbtCliResource, dbt_assets


DBT_PROJECT = Path(__file__).resolve().parents[1] / "dbt_project"


MANIFEST = Path(environ.get("RETAIL_DBT_MANIFEST", DBT_PROJECT / "target" / "manifest.json"))


@dbt_assets(manifest=MANIFEST)
def retail_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()


defs = Definitions(
    assets=[retail_dbt_assets],
    resources={
        "dbt": DbtCliResource(project_dir=DBT_PROJECT, profiles_dir=DBT_PROJECT),
    },
)
