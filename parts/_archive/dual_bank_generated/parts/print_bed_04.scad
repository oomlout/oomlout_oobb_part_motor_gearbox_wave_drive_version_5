include <parameters.scad>;
use <oobb_hardware.scad>;
include <geometry.scad>;
translate([60.5, 60.5, 0]) fixed_ring(true);
translate([162.0, 43.0, 0]) wave_generator();
translate([133.0, 98.0, 0]) input_spacer(7.900000000000002, false, false);