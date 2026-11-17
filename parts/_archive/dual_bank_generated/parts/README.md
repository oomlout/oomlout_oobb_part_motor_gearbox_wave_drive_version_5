# 20:1 opposed roller wave gearbox

Print fit_coupons.stl first, then print_bed_01.stl through print_bed_05.stl.
The beds contain all 26 printed pieces from 19 designs.
Purchase 40 nylon spacers: 7 mm OD x 12 mm long; bore assumed 3.2 mm.
The rollers are not included on the production beds.

Both mounting plates have 1.5 mm corner radii. All assembly screws are socket caps,
with a 35 mm maximum under-head length; the longest default screw is 16 mm.

Open assembly.scad, animation.scad or motor_fit.scad. The NEMA 17 motor is a full
40 mm reference model; a bracket and coupling/revised input connection are still needed.
See ASSEMBLY.md for the keyed profile-ring phase, nut-loading order and hardware.

In the ZIP, renders/exploded_motor.png and renders/motor_fit.png show the arrangement.
manifest.json lists quantities and bed placements; hardware.yaml lists purchased items.
mesh_validation.json and checks/ hold the executed checks. Physical performance is untested.
