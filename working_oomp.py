"""Load populated recipes into the standard parts catalogue, without AI tooling."""
import copy
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent


def create_generic(**kwargs):
    kwargs = copy.deepcopy(kwargs)
    kwargs.setdefault("part_filter", "")
    output_root = Path(kwargs.get("output_root", ROOT))
    parts = []
    for source in sorted((output_root / "parts_source").glob("*/working.yaml")):
        if "part_ids" in kwargs and source.parent.name not in kwargs["part_ids"]:
            continue
        if kwargs["part_filter"] not in source.parent.name:
            continue
        part = yaml.safe_load(source.read_text(encoding="utf-8"))
        part["name"] = source.parent.name
        part["name_proper"] = part["name"].replace("_", " ").title()
        part["directory"] = f"parts/{part['name']}"
        folder = output_root / part["directory"]
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "working.yaml").write_text(
            yaml.safe_dump(part, sort_keys=False), encoding="utf-8"
        )
        parts.append(part)
    return parts


def main(**kwargs):
    return create_generic(**kwargs)


if __name__ == "__main__":
    main()

