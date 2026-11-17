# Mishin Machine reference inspection — 16 November 2026

Source landing page: https://urals.co/mshn/wgwr

The three CAD documents linked by that page were opened and inspected in the browser:

| Document | Observations | Signed-in export |
| --- | --- | --- |
| [Parametric gearbox](https://cad.onshape.com/documents/b77bd5f26eda1d0db7f8a940/w/4546d7a6751e09dd9c3f7a5e/e/af99731a4c0cd6d6cfd15d2a) | 63 features, 10 parts. Fixed inner-profile ring, separator/output, free wave generator, eccentric input cam, motor mount, output shaft, bearing housing, bearing lip ring, spacer and handle. Feature folders include counterbalance and second-stage variants. | `onshape/mishin_wave_gearbox_all_parts.step`, 10 named manifold solids; Variables inspected and transcribed. |
| [NEMA17 housing variant](https://cad.onshape.com/documents/642a22b68e01b1a8c25f6d7c/w/210d085d4de245fdb609a29c/e/48b3b39636e22719b43b0018) | 60 features, 10 parts. Motor mount and output housing changes; additional ring and separator parts are present. | `onshape/mishin_nema17_all_parts.step`, 10 named manifold solids; Variables inspected and transcribed. |
| [Generator example](https://cad.onshape.com/documents/dd8655be933d8b5fa2c4eb1a/w/b262b9d4d2a93e39b8c6a666/e/24a14ec8fdde7fad16276a17) | 5 features, 4 parts. Inspected the separator in isolation. The shown example has spherical windows; the source explicitly implements rectangular windows for cylindrical rollers. Tabs: Example, Wave Gear With Rollers, Roller Wave Gear Icon.svg. | `onshape/mishin_generator_example_all_parts.step`, 4 named manifold solids; original SVG attachment also downloaded. |

Downloaded/archived source:

- `urals_page.html`: the reference landing page.
- `gist_metadata.json`: the complete GitHub gist API response, including revision metadata and file inventory.
- `wave_roller_gear.py`: the complete, byte-preserved raw file from the linked gist. The gist contains one file. Read in full; its plotting entry point was not executed.
- `wave_gear_with_rollers.fs`: the complete 852-line FeatureScript read through the browser editor's Select All / Copy operation. Saved from that exact browser tool result. It is not a native Onshape model export.
- `files.json`: SHA-256 checksums for the archive.

FeatureScript source tab: https://cad.onshape.com/documents/dd8655be933d8b5fa2c4eb1a/w/b262b9d4d2a93e39b8c6a666/e/371f02b3a16778926a93e58c

The initial anonymous viewer denied exports and variable access. Martin McDoozle then signed in, resolving those limits. All three Part Studios were exported through the browser's Export dialog as STEP AP242, with **Include hidden instances** enabled, default orientation and no preprocessing. The STEP headers and named `MANIFOLD_SOLID_BREP` entities were inspected locally and match the viewer's 10 / 10 / 4 parts. `onshape/inspection.json` records those names and hashes. The original SVG is an editable 216 × 216 vector icon depicting the roller ring; its paths and colours were inspected.

`onshape/variables.json` is a manual transcription of the two visible variable tables, preserving the original variable-name spelling. The main design uses 14 rollers of diameter 7 mm, a 35 × 47 × 8 input bearing and a 50 × 65 × 7 output bearing. The NEMA variant uses 8 rollers of diameter 5 mm, a 15 × 24 × 5 input bearing and a 20 × 32 × 7 output bearing. Both use 5 mm roller height and a 5 mm input shaft. This project's 20 rollers and three 6704 bearings are deliberate adaptations, not claims about the reference defaults.

The exports archive the solids available in those Part Studios. They do not preserve editable Onshape feature history or automatically enumerate suppressed configurations. The full generator FeatureScript is archived separately. No reference geometry is imported into this project's build or Blender rendering pipeline.

## What the implementation takes from the reference

The fixed ring has `roller_count + 1` cavities. Each loose roller translates radially in a rigid output separator. A round wave wheel runs eccentrically on a bearing. The shaft drives the eccentric inner journal; the wheel is free to turn on its bearing. There is no flexible spline and no fixed pin ring.

For a fixed ring, 20 rollers and 21 cavities give `output_angle = -input_angle / 20`. The new code uses conventional cosine-X/sine-Y axes, whereas the original uses sine-X/cosine-Y axes. The normal-envelope equation is otherwise equivalent. The Python and SCAD implementations are checked independently against the circular cam geometry.

The reference's nominal outside-radius labels differ between the Python example and FeatureScript. Python uses `wave_radius = cy_r - 2*eccentricity - roller_diameter`; FeatureScript uses `wave_radius = cy_r - eccentricity - roller_diameter`. This project defines the **actual wave radius directly**, so it does not silently inherit that naming discrepancy.

The original fixes eccentricity to 0.2 times roller diameter. The current opposed-bank build uses an explicit 0.75 mm eccentricity with 7 mm OD nylon spacers and a 40 mm wave radius. Its 4 mm radial cage wall has 0.75 mm nominal radial separation from both the eccentric wave wheel and the innermost fixed profile. Each bank has independent rollers. The upper profile is rotated 180/21 degrees and its eccentric is 180 degrees opposite the lower, so both banks drive one common cage. Clearance intentionally introduces backlash; the nominal ratio is not a measured backlash or torque claim.

The original files are attribution/provenance references. They are not imported by the build. No license grant for the whole Onshape design is assumed; confirm original licensing before redistributing those reference files commercially.

