include <C:/gh/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/parameters.scad>
include <C:/gh/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/oobb_hardware.scad>
include <C:/gh/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/geometry.scad>
difference() { translate([0,0,-8]) cylinder(r=1.5,h=8); translate([0,0,-1]) cylinder(r=0.75,h=1.01,$fn=6); }