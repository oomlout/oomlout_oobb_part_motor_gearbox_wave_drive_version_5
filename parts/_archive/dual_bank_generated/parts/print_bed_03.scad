include <parameters.scad>;
use <oobb_hardware.scad>;
include <geometry.scad>;
translate([60.5, 60.5, 0]) fixed_ring(false);
translate([168.5, 49.5, 0]) cage_joint();