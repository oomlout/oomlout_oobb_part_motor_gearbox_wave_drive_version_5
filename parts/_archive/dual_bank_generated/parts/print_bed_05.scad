include <parameters.scad>;
use <oobb_hardware.scad>;
include <geometry.scad>;
translate([60.5, 60.5, 0]) stationary_joint();
translate([162.0, 43.0, 0]) wave_generator();