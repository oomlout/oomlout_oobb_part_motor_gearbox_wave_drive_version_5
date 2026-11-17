include <parameters.scad>;
use <oobb_hardware.scad>;
include <geometry.scad>;
include <motor_reference_parameters.scad>;
include <nema17_reference.scad>;
translate([80,0,0]) cube([1,1,1]);
intersection() { assembly(0,0); translate([0,0,motor_face_z]) nema17_reference(); }
