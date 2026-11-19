include <C:/gh/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/parameters.scad>
include <C:/gh/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/oobb_hardware.scad>
include <C:/gh/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/geometry.scad>
include <C:/gh/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/motor_reference_parameters.scad>
include <C:/gh/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/nema17_reference.scad>
translate([80,0,0]) cube([1,1,1]);
intersection() { union() { translate([0,0,cage_floor_z]) cage(); translate([0,0,output_cover_z]) mirror([0,0,1]) output_retainer(); translate([0,0,output_cover_z]) output_cover(); } translate([0,0,cage_floor_z-1]) cylinder(d=output_view_diameter-0.02,h=assembly_height-cage_floor_z+2); }
