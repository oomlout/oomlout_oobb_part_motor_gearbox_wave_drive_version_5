include <parameters.scad>;
use <oobb_hardware.scad>;
include <geometry.scad>;
translate([31.75, 31.75, 0]) cage_cap();
translate([89.5, 28.0, 0]) output_hub();
translate([141.75, 26.25, 0]) wave_generator();
translate([191.0, 25.0, 0]) wave_cap();