include <parameters.scad>;
use <oobb_hardware.scad>;
include <geometry.scad>;
difference() { assembly(0, 0); translate([-100,-100,mirror_z]) cube([200,100,100]); }
