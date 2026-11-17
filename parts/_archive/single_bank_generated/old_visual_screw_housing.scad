include <C:/od/OneDrive/Documents/ChatGPT/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_20_to_1_reduction/parameters.scad>
include <C:/od/OneDrive/Documents/ChatGPT/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_20_to_1_reduction/oobb_hardware.scad>
include <C:/od/OneDrive/Documents/ChatGPT/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_20_to_1_reduction/geometry.scad>
difference() { difference() {
	union() {
		translate(v = [0, 0, 0]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -1.7]) {
							cylinder(h = 1.7, r1 = 1.5, r2 = 2.9);
						}
						translate(v = [0, 0, -35.0]) {
							cylinder(h = 35.0, r = 1.5);
						}
					}
					union();
				}
			}
		}
	}
	union();
}
 translate([0,0,-1]) cylinder(r=1.0,h=1.01,$fn=6); }