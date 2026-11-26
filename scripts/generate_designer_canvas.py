"""Build a Designer experiment from an exported, matching Designer template."""

import argparse
import copy
import json
from pathlib import Path
from uuid import uuid4

import yaml


NOTEBOOK_METADATA = "application/vnd.databricks.v1+notebook"
CELL_METADATA = "application/vnd.databricks.v1+cell"
PILOTS = {
    "policy": ("model.policy_lineage_pilot.fct_policy", "Policy_manifest_canvas_poc", "visual_fct_policy_poc"),
    "retail": ("model.retail_lineage_poc.fct_sales", "Retail_manifest_canvas_poc", "visual_fct_sales_poc"),
}


def split_cell(cell):
    prefix, metadata, body = "".join(cell["source"]).split('"""', 2)
    assert not prefix.strip()
    return yaml.safe_load(metadata), body


def block(body, start, end, replacement):
    left = body.index(start)
    right = body.index(end, left)
    return body[:left] + replacement + body[right:]


def make_cell(template, metadata, body):
    cell = copy.deepcopy(template)
    cell["metadata"][CELL_METADATA]["nuid"] = str(uuid4())
    cell["outputs"] = []
    cell["execution_count"] = None
    header = yaml.safe_dump(metadata, sort_keys=False, width=1000)
    cell["source"] = ('"""\n' + header + '"""' + body).splitlines(keepends=True)
    compile("".join(cell["source"]), metadata["id"], "exec")
    return cell


def materialized_dependencies(manifest, model_key):
    pending = list(manifest["parent_map"][model_key])
    visited = set()
    dependencies = []
    while pending:
        key = pending.pop()
        if key in visited:
            continue
        visited.add(key)
        node = manifest["nodes"][key]
        if node["config"].get("materialized") == "ephemeral":
            pending.extend(manifest["parent_map"][key])
        else:
            dependencies.append(node)
    return dependencies


def generate(template, manifest, compiled_sql, pilot="policy"):
    model_key, canvas_name, output_name = PILOTS[pilot]
    model = manifest["nodes"][model_key]
    dependencies = materialized_dependencies(manifest, model_key)
    catalog, schema = model["database"], model["schema"]
    if not dependencies:
        raise ValueError("The selected model has no materialized inputs.")
    if len({node["name"] for node in dependencies}) != len(dependencies):
        raise ValueError("Designer Source names must be unique.")

    source_cell, sql_cell, output_cell = template["cells"]
    source_meta, source_body = split_cell(source_cell)
    sql_meta, sql_body = split_cell(sql_cell)
    output_meta, output_body = split_cell(output_cell)
    assert [m["template"] for m in (source_meta, sql_meta, output_meta)] == ["source", "sql", "output"]
    sources = []
    cells = []
    for index, dependency in enumerate(sorted(dependencies, key=lambda item: item["name"]), 1):
        source_name = dependency["name"]
        source_id = f"source_{index}"
        table_name = f"{dependency['database']}.{dependency['schema']}.{dependency['alias']}"
        quoted = ".".join(f"`{part}`" for part in table_name.split("."))
        if compiled_sql.count(quoted) != 1:
            raise ValueError(f"Expected one compiled reference to {table_name}.")
        compiled_sql = compiled_sql.replace(quoted, source_name)
        sources.append({"node": source_id, "output_port": "data", "name": source_name, "df_name": source_name})
        metadata = copy.deepcopy(source_meta)
        metadata.update(id=source_id, name=source_name, position={"x": 80, "y": 100 + 170 * (index - 1)})
        old_table = metadata["config"]["table_source"]["tableName"]
        metadata["config"]["table_source"]["tableName"] = table_name
        body = source_body.replace(old_table, table_name).replace('"source_1', f'"{source_id}')
        cells.append(make_cell(source_cell, metadata, body))

    sql_meta.update(name=model["name"], position={"x": 400, "y": 270})
    sql_meta["config"]["query"] = compiled_sql.strip()
    sql_meta["input"] = [{"node": src["node"], "input_port": "data", "output_port": "data"} for src in sources]
    sql_meta.pop("description", None)
    sql_body = block(sql_body, "config = {", 'config["meta_state"]', f'config = {json.dumps(sql_meta["config"])}\n')
    contexts = ", ".join(f'ctx["{src["node"]}.data"]' for src in sources)
    inputs = f'inputs = {{"data": [{contexts}], "data__sources": {json.dumps(sources)}}}\n'
    sql_body = block(sql_body, "inputs = {\n", 'if config["meta_state"]["is_disabled"]', inputs)
    cells.append(make_cell(sql_cell, sql_meta, sql_body))

    old_destination = output_meta["config"]
    old_catalog, old_schema, old_output = (old_destination[key] for key in ("catalog", "schema", "table_name"))
    old_fqn = ".".join((old_catalog, old_schema, old_output))
    new_fqn = ".".join((catalog, schema, output_name))
    output_body = output_body.replace(old_fqn, new_fqn)
    for old, new in ((old_catalog, catalog), (old_schema, schema), (old_output, output_name)):
        output_body = output_body.replace(json.dumps(old), json.dumps(new))
    old_destination.update(catalog=catalog, schema=schema, table_name=output_name)
    output_meta.update(name=f"Output to {output_name}", position={"x": 720, "y": 270})
    cells.append(make_cell(output_cell, output_meta, output_body))

    canvas = copy.deepcopy(template)
    canvas["metadata"][NOTEBOOK_METADATA]["notebookName"] = f"{canvas_name}.designer.ipynb"
    canvas["cells"] = cells
    return canvas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("template", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("compiled_sql", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--pilot", choices=PILOTS, default="policy")
    args = parser.parse_args()
    canvas = generate(
        json.loads(args.template.read_text(encoding="utf-8")),
        json.loads(args.manifest.read_text(encoding="utf-8")),
        args.compiled_sql.read_text(encoding="utf-8"),
        pilot=args.pilot,
    )
    args.output.write_text(json.dumps(canvas, indent=2), encoding="utf-8")
    print(f"Generated {len(canvas['cells'])} Designer cells: {args.output}")


if __name__ == "__main__":
    main()
