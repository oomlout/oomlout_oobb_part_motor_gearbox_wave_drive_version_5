include <parameters.scad>;
use <oobb_hardware.scad>;
include <geometry.scad>;
input_angle = 360 * $t;
assembly(input_angle, 0);
