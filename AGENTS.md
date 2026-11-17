# Project instructions

- The user's preferred name is Martin McDoozle.
- Keep `C:/gh/oomlout_oobb_part_motor_gearbox_cycloidal_version_5` read-only.
- This project is an intermediate-roller wave drive, not a harmonic drive.
- Author settings in `working_oomp_populate.py`, catalogue loading in `working_oomp.py`, and drawing/export in `working_scad.py`.
- Use verbose dictionaries, `copy.deepcopy`, `kwargs.setdefault`, and `**kwargs` forwarding. Keep mechanical defaults easy to edit.
- Use OpenSCAD for geometry. No SolidCraft runtime or generated STEP dependency.
- Use OOBB primitives for hardware and always pass `overhang=True`.
- Default to one compact 12:1 bank with twelve 7 mm OD x 12 mm nylon spacers. Keep the archived dual-bank design separate.
- Use one upper 6810 output bearing and one 6704 wave bearing. The eccentric mounts directly to the motor shaft; no lower 6810 or separate input bearing.
- Use countersunk screws with captive nuts for every cage tooth, the eccentric joint and the M3 motor shaft clamp. The shaft-clamp primitive needs clearance="top" and an aligned driver-access bore through the case and lower cage. Keep all screw lengths at most 35 mm; countersunk lengths include the head.
- The 40 mm NEMA 17 uses a designed direct motor plate and eccentric adapter. Its reference shaft is plain round, 5 mm diameter and 24 mm long; both eccentric pieces use a round bore (flat depth zero). The M3 x 8 radial clamp has a nominal head radius of 10.5 mm. Load capacity and printed fits still need physical verification.
- This project belongs in `C:/gh/oomlout_oobb_part_motor_gearbox_wave_drive_version_5`; do not recreate the old ChatGPT-folder project.
- `python working.py` must regenerate every active populated configuration completely, including documentation and graphics, without AI or manual generated-file edits.
- Store every configuration's drawings, images, scenes, instructions and validation reports inside its own `parts/<part-id>/` directory. Do not recreate root presentation, release or tools directories. ZIP packaging is disabled by default; distribute individual files and do not recreate large backup or print-pack archives.
- Keep reusable helpers in `components/wave_drive/`, inputs in `source_file/`, and prior generated builds under `parts/_archive/`.
- Define named configurations, build flags, render settings and assembly instruction templates in `working_oomp_populate.py`.
- Use a standard OOBB base with 5 mm plan corner radii, 1.5 mm upper/lower edge radii, M6 grid holes and M3 half-grid holes. The full output face is a nut-carrier/cover sandwich with captive M6 and M3 nuts wherever they fit; the motor shaft ends in a blind pocket underneath it.
- The default base is 7 x 5 with the central cylinder and boss footprint added where needed. Recess output nuts inside the 6810 bore and put the black face 1.5 mm above the teal housing. Use a 3 mm main housing wall plus rounded rectangular screw bosses with 2 mm walls and flat inner sides. Split the 6704 rolling member at the bearing centre into two full-diameter clamshells.
- Put every cage tooth on the lower part, printing upright. Integrate the upper closure and support disc into one piece, broad face down and hub up, without a taper. Use one top-access countersunk screw per tooth and nuts in the lower cage.
- Give cage screw heads OOBB clearance="top" through the upper disc. The lower opening is 25 mm to pass over the bare eccentric shaft. Round the fins until the outer arc reaches the screw centreline or becomes a full semicircle. Move output fixings off the OOBB grid to free extra M3 attachment positions; use 0.8 mm axial and 0.6 mm radial visual clearances at the output face.
- Regenerate with `python working.py`; use `--scad-only` for drawings without mesh export and `--no-renders` for meshes/checks without Blender. Verify with `python -m pytest -q`.


- Motor-to-base fasteners are four M3 x 8 countersunk screws, flush on top. Six M3 x 30 case socket caps enter downward from the top housing into captive M3 nuts loaded underneath the base.
- Assembly style: four numbered panels per landscape A4 sheet, cumulative full-colour CAD, combined nut-loading/placement steps, black-only text, no titles or prose on panels; part image then small x2-style quantity and oom.lt/a/{md5_6_alpha} link.

- Use twelve M2 x 20 countersunk cage screws. Raise head seats 3 mm and captive nut seats 1 mm; preserve full nut engagement and 1.6 mm nominal clearance above the cage underside. Raise the bearing/output stack with the 6 mm upper closure; keep case screws at 30 mm using deeper head wells.
- Assembly booklet: stronger panel borders, no arrows, increased explosion, only quantities greater than one as small bottom-right thumbnail overlays. Tight URL line spacing, smaller prefix, smaller bold alpha code. Include cover, sparse project details, four-step pages, signature padding, printed OOBB parts summary on the penultimate page, and back cover.

- Use M3 x 16 countersunk screws and captive M3 nuts for the eccentric joint (6.75 mm pitch radius), and four flush M3 x 12 countersunk screws for the wave clamshell.
- Assembly style 4 uses Consolas numbers/URLs, Segoe UI Semibold part names, pure-black (#000000) 3 pt panel and 1.1 pt parts-box borders, 8.5 mm thumbnails, and quantities shifted 1 mm right. Printed parts have no shortlinks or codes anywhere in the booklet or inventory. Hardware keeps its links.
- Covers use the black Oomlout symbol without words. Include the GitHub project name on the print-oriented cover and technical bullets inside. Step 13 is a full-page boxed completed view; the penultimate page has separate printed/hardware boxes with shared hardware quantities merged.

- Generate a standalone offline HTML viewer from the same audited instructions. Show one step per screen, retain hardware-only links, and provide keyboard, swipe, step-selection and full-screen controls. Root README leads with its GitHub Pages URL; README_DETAILS.md contains the complete design and written sequence.
- Include twelve optional 7 mm OD x 12 mm printable spacers with a 3.2 mm bore in 3dpr and print beds, exported as printable_spacer.stl. Keep them separate from required printed inventory: they replace the purchased nylon rollers, never add another set to the assembly.
- Root README is a version index: project description, Mishin Machine video/creator credit, AI source/readability notice, then a table with image, description, version README, hosted HTML instructions and PDF download. Author its content in `define_project_readme` in the populate file. HTML viewing links must open GitHub Pages, not raw HTML downloads. Follow `C:/gh/oomlout_oobb_version_5/README_GUIDELINES.md`.
- Each version's README link targets `parts/<part-id>/README.md`. Keep that part README focused on the design, printable parts, hardware and assembly; omit regeneration instructions.
