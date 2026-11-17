include <parameters.scad>;
use <oobb_hardware.scad>;
include <geometry.scad>;
// Complete inventory, spread across multiple print beds.
translate([44.5, 44.5, 0]) motor_mount_plate();
translate([138.5, 39.5, 0]) fixed_ring();
translate([227.5, 39.5, 0]) output_housing();
translate([305.75, 28.75, 0]) cage();
translate([28.75, 127.75, 0]) cage_cap();
translate([92.5, 124.0, 0]) output_hub();
translate([160.0, 131.5, 0]) output_retainer();
translate([225.75, 122.25, 0]) wave_generator();
translate([281.0, 121.0, 0]) wave_cap();
translate([325.0, 111.0, 0]) motor_eccentric();
translate([12.0, 186.0, 0]) motor_eccentric_cap();