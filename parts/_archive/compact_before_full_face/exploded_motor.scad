include <parameters.scad>;
use <oobb_hardware.scad>;
include <geometry.scad>;
include <motor_reference_parameters.scad>;
include <nema17_reference.scad>;
assembly(0,12);
translate([0,0,motor_face_z-24]) nema17_reference();
