include <C:/gh/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/parameters.scad>
include <C:/gh/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/oobb_hardware.scad>
include <C:/gh/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/geometry.scad>
difference() { intersection() { difference() {
	union() {
		translate(v = [0, 0, 0]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						linear_extrude(height = 1.6) {
							polygon(points = [[2.308, 0.0], [1.1540000000000001, 1.998786631934484], [-1.1539999999999995, 1.9987866319344845], [-2.308, 2.826484812432091e-16], [-1.154000000000001, -1.9987866319344838], [1.1539999999999984, -1.9987866319344851]]);
						}
					}
					union();
				}
			}
		}
	}
	union();
}
 translate([-5,-5,0]) cube([10,10,1.6]); } translate([0,0,-0.01]) cylinder(r=1,h=1.62); }