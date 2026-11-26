import argparse
import json
from pathlib import Path


GRAPH_TYPES = {"model", "seed", "snapshot", "source"}


def print_mermaid(manifest):
    resources = {
        node["unique_id"]: node
        for group in ("nodes", "sources")
        for node in manifest.get(group, {}).values()
        if node["resource_type"] in GRAPH_TYPES
    }
    node_ids = {key: f"node_{index}" for index, key in enumerate(sorted(resources), 1)}

    print("flowchart LR")
    for key, node_id in node_ids.items():
        node = resources[key]
        resource_type = node["resource_type"]
        kind = node["config"]["materialized"] if resource_type == "model" else resource_type
        label = f"{key.split('.')[1]}.{node['name']} ({kind})"
        label = label.replace('"', "#quot;").replace("<", "#lt;").replace(">", "#gt;")
        print(f'    {node_id}["{label}"]')

    for key, target in node_ids.items():
        parents = resources[key].get("depends_on", {}).get("nodes", [])
        for parent in sorted(parents):
            if parent in node_ids:
                print(f"    {node_ids[parent]} --> {target}")


def main():
    parser = argparse.ArgumentParser(description="Print declared dbt model dependencies.")
    default_manifest = Path(__file__).resolve().parents[1] / "dbt_project/target/manifest.json"
    parser.add_argument("manifest", nargs="?", type=Path, default=default_manifest)
    parser.add_argument("--format", choices=("text", "mermaid"), default="text")
    args = parser.parse_args()

    with args.manifest.open(encoding="utf-8") as manifest_file:
        manifest = json.load(manifest_file)

    if args.format == "mermaid":
        print_mermaid(manifest)
        return

    for node in sorted(manifest["nodes"].values(), key=lambda item: item["unique_id"]):
        if node["resource_type"] == "model":
            upstream = ", ".join(node["depends_on"]["nodes"]) or "(none)"
            print(f"{node['unique_id']} [{node['config']['materialized']}] <- {upstream}")


if __name__ == "__main__":
    main()
