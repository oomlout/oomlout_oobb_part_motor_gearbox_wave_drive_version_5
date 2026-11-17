"""Run the populated SCAD gearbox configurations."""
import copy
import working


def main(**kwargs):
    kwargs = copy.deepcopy(kwargs)
    kwargs["run_solidcraft"] = False
    kwargs.setdefault("scad_only", True)
    kwargs.setdefault("no_renders", True)
    return working.main(**kwargs)


if __name__ == "__main__":
    main()
