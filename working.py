"""Deterministic populate -> catalogue -> SCAD build. No AI actions or SolidCraft."""
import argparse
import copy
from pathlib import Path


def main(**kwargs):
    import working_oomp_populate
    import working_oomp
    import working_scad
    kwargs = copy.deepcopy(kwargs)
    kwargs.setdefault("output_root", Path(__file__).resolve().parent)
    kwargs.setdefault("run_oomp_populate", True)
    kwargs.setdefault("run_oomp", True)
    kwargs.setdefault("run_scad", True)
    if kwargs.get("run_solidcraft", False):
        raise ValueError("This project uses the SCAD pipeline; set run_solidcraft=False")
    controls = {"output_root", "run_oomp_populate", "run_oomp", "run_scad", "run_solidcraft", "run_action", "run_svg", "scad_only", "no_renders", "assembly_only", "part_filter", "render", "images", "generate_stl", "typ", "export_stl", "export_extras"}
    recipe = {key:value for key,value in kwargs.items() if key not in controls}
    options = None
    if kwargs["run_oomp_populate"]:
        options = working_oomp_populate.main(output_root=kwargs["output_root"], **recipe)
    catalogue_kwargs = {
        "output_root": kwargs["output_root"],
        "part_filter": kwargs.get("part_filter", ""),
    }
    if options is not None:
        catalogue_kwargs["part_ids"] = [option["id"] for option in options]
    parts = None
    if kwargs["run_oomp"]:
        parts = working_oomp.main(**catalogue_kwargs)
    if kwargs["run_scad"]:
        return working_scad.main(parts=parts, **kwargs)
    return parts


def run(**kwargs):
    return main(**kwargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scad-only", action="store_true", help="Generate editable SCAD and instructions without rendering meshes")
    parser.add_argument("--no-renders", action="store_true", help="Build meshes and checks without Blender images")
    parser.add_argument("--assembly-only", action="store_true", help="Regenerate populated assembly cards from validated existing production meshes")
    parser.add_argument("--part-filter", default="")
    parser.add_argument("--render", action="store_true", default=None, help="Explicitly enable STL export")
    parser.add_argument("--images", action="store_true", default=None, help="Explicitly enable SCAD previews")
    main(**vars(parser.parse_args()))
