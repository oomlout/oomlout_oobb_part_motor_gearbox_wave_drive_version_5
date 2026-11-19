include <parameters.scad>;
use <oobb_hardware.scad>;
include <geometry.scad>;
translate([33.9, 33.9, 0]) output_cover();
translate([98.05, 32.25, 0]) cage_face_down();
translate([160.55, 32.25, 0]) cage_cap();
translate([26.25, 92.05, 0]) wave_cap();