"""Run the populated SCAD gearbox configurations."""
import copy
import working


def main(**kwargs):
    kwargs = copy.deepcopy(kwargs)
    kwargs["run_solidcraft"] = False
    kwargs.setdefault("scad_only", False)
    kwargs.setdefault("no_renders", False)
    return working.main(**kwargs)


if __name__ == "__main__":
    main()
