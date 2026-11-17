include <C:/gh/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/parameters.scad>
include <C:/gh/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/oobb_hardware.scad>
include <C:/gh/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/geometry.scad>
difference() { 

difference() {
	union() {
		translate(v = [0, 0, 0]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -0.65]) {
							cylinder(h = 0.65, r1 = 1.0, r2 = 2.0);
						}
						translate(v = [0, 0, -20.0]) {
							cylinder(h = 20, r = 1.0);
						}
					}
					union();
				}
			}
		}
	}
	union();
}
 translate([0,0,-0.45]) cylinder(r=0.65,h=0.46,$fn=6); }