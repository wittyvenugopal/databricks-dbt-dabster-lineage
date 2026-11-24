import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Print declared dbt model dependencies.")
    default_manifest = Path(__file__).resolve().parents[1] / "dbt_project/target/manifest.json"
    parser.add_argument("manifest", nargs="?", type=Path, default=default_manifest)
    args = parser.parse_args()

    with args.manifest.open(encoding="utf-8") as manifest_file:
        manifest = json.load(manifest_file)

    for node in sorted(manifest["nodes"].values(), key=lambda item: item["unique_id"]):
        if node["resource_type"] == "model":
            upstream = ", ".join(node["depends_on"]["nodes"]) or "(none)"
            print(f"{node['unique_id']} [{node['config']['materialized']}] <- {upstream}")


if __name__ == "__main__":
    main()
