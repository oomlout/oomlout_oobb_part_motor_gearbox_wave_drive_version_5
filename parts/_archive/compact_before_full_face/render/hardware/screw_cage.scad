include <C:/od/OneDrive/Documents/ChatGPT/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/parameters.scad>
include <C:/od/OneDrive/Documents/ChatGPT/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/oobb_hardware.scad>
include <C:/od/OneDrive/Documents/ChatGPT/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/geometry.scad>
difference() { difference() {
	union() {
		translate(v = [0, 0, 0]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						cylinder(h = 2.0, r = 1.9);
						translate(v = [0, 0, -16.0]) {
							cylinder(h = 16, r = 1.0);
						}
					}
					union();
				}
			}
		}
	}
	union();
}
 translate([0,0,1]) cylinder(r=0.75,h=1.01,$fn=6); }