include <parameters.scad>;
use <oobb_hardware.scad>;
include <geometry.scad>;
collision_check(is_undef(check_angle) ? 0 : check_angle);
