include <C:/gh/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/parameters.scad>
include <C:/gh/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/oobb_hardware.scad>
include <C:/gh/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/geometry.scad>
difference() { intersection() { 

difference() {
	union() {
		translate(v = [0, 0, 0]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						linear_extrude(height = 5.0) {
							polygon(points = [[5.77, 0.0], [2.8850000000000002, 4.996966579836211], [-2.8849999999999985, 4.996966579836211], [-5.77, 7.066212031080227e-16], [-2.8850000000000025, -4.99696657983621], [2.884999999999996, -4.996966579836213]]);
						}
					}
					union();
				}
			}
		}
	}
	union();
}
 translate([-8,-8,0]) cube([16,16,5.0]); } translate([0,0,-0.01]) cylinder(r=3,h=5.02); }