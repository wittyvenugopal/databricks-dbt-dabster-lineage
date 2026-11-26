# Databricks notebook source
# MAGIC %md
# MAGIC # dbt model dependencies
# MAGIC The graph shows declared dependencies from dbt's manifest. The bundled example is the policy pilot.
# MAGIC To inspect another project, set `manifest_path` to the path of its `manifest.json` in a Unity Catalog volume or workspace file, then run the Python cell.

# COMMAND ----------

import json
from html import escape
from pathlib import Path

dbutils.widgets.text("manifest_path", "", "Optional manifest.json path")
manifest_path = dbutils.widgets.get("manifest_path").strip()

# Small dependency-only snapshot extracted from the policy pilot's real manifest.
resources = {'model.policy_lineage_pilot.fct_policy': {'kind': 'table',
                                           'name': 'fct_policy',
                                           'parents': ['model.policy_lineage_pilot.stg_policies',
                                                       'model.policy_lineage_pilot.stg_customers',
                                                       'model.policy_lineage_pilot.stg_quotes']},
 'model.policy_lineage_pilot.stg_customers': {'kind': 'view',
                                              'name': 'stg_customers',
                                              'parents': ['seed.policy_lineage_pilot.raw_customers']},
 'model.policy_lineage_pilot.stg_policies': {'kind': 'view',
                                             'name': 'stg_policies',
                                             'parents': ['seed.policy_lineage_pilot.raw_policies']},
 'model.policy_lineage_pilot.stg_quotes': {'kind': 'view',
                                           'name': 'stg_quotes',
                                           'parents': ['seed.policy_lineage_pilot.raw_quotes']},
 'seed.policy_lineage_pilot.raw_customers': {'kind': 'seed',
                                             'name': 'raw_customers',
                                             'parents': []},
 'seed.policy_lineage_pilot.raw_policies': {'kind': 'seed',
                                            'name': 'raw_policies',
                                            'parents': []},
 'seed.policy_lineage_pilot.raw_quotes': {'kind': 'seed',
                                          'name': 'raw_quotes',
                                          'parents': []}}
if manifest_path:
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    resources = {
        node["unique_id"]: {
            "name": node["name"],
            "kind": node["config"]["materialized"] if node["resource_type"] == "model" else node["resource_type"],
            "parents": node.get("depends_on", {}).get("nodes", []),
        }
        for group in ("nodes", "sources")
        for node in manifest.get(group, {}).values()
        if node["resource_type"] in {"model", "seed", "source", "snapshot"}
    }

parents = {
    key: sorted(set(node["parents"]) & resources.keys())
    for key, node in resources.items()
}
depths = {}
pending = set(resources)
while pending:
    ready = sorted(key for key in pending if all(parent in depths for parent in parents[key]))
    if not ready:
        raise ValueError("The selected resources contain a dependency cycle.")
    for key in ready:
        depths[key] = max((depths[parent] + 1 for parent in parents[key]), default=0)
    pending.difference_update(ready)

if not depths:
    raise ValueError("The manifest has no models, seeds, sources or snapshots.")

columns = [
    sorted(key for key, node_depth in depths.items() if node_depth == depth)
    for depth in range(max(depths.values()) + 1)
]
width = 60 + 260 * len(columns)
height = 90 + 90 * max(map(len, columns))
positions = {
    key: (40 + column * 260, (height - (len(keys) - 1) * 90 - 58) // 2 + row * 90)
    for column, keys in enumerate(columns)
    for row, key in enumerate(keys)
}

edges = []
for target, dependencies in parents.items():
    x2, y2 = positions[target]
    for source in dependencies:
        x1, y1 = positions[source]
        start, end = x1 + 190, x2 - 5
        middle = (start + end) / 2
        y1, y2_center = y1 + 29, y2 + 29
        edges.append(
            f'<path d="M{start},{y1} C{middle},{y1} {middle},{y2_center} {end},{y2_center}" '
            'fill="none" stroke="#415775" stroke-width="2" marker-end="url(#arrow)"/>'
        )

colors = {"seed": "#e8f0ff", "source": "#e8f0ff", "view": "#e6f6f1", "table": "#fff0d7", "ephemeral": "#f3e9ff"}
cards = []
for key, (x, y) in positions.items():
    node = resources[key]
    label, kind = escape(node["name"]), escape(node["kind"])
    fill = colors.get(node["kind"], "#edf1f6")
    cards.append(
        f'<g><title>{escape(key)}</title><rect x="{x}" y="{y}" width="190" height="58" rx="9" '
        f'fill="{fill}" stroke="#a5b2c3"/><text x="{x+95}" y="{y+23}" text-anchor="middle" '
        f'font-size="15" font-weight="700" fill="#122039">{label}</text>'
        f'<text x="{x+95}" y="{y+43}" text-anchor="middle" font-size="13" fill="#415775">{kind}</text></g>'
    )

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" '
    'role="img" aria-label="dbt dependency graph" font-family="system-ui, sans-serif">'
    '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
    'markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#415775"/></marker></defs>'
    f'<rect width="{width}" height="{height}" rx="12" fill="#fafcff"/>'
    + "".join(edges) + "".join(cards) + "</svg>"
)
displayHTML(f'<div class="nodarkmode" style="overflow-x:auto">{svg}</div>')
print(f"Displayed {len(resources)} resources and {len(edges)} dependency edges.")
