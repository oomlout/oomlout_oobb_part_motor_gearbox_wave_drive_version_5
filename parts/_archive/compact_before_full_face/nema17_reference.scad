// Visual reference matching the previous cycloidal project's 40 mm motor envelope.
// Face is Z=0; motor body extends towards -Z and shaft towards +Z.
// End caps, corner chamfers and connector are illustrative external details.
// This is purchased reference hardware, never a printable gearbox component.
module nema17_outline(width=42.3,depth=6,chamfer=3) {
    w=width/2;
    linear_extrude(depth) polygon([
        [-w+chamfer,-w],[w-chamfer,-w],[w,-w+chamfer],[w,w-chamfer],
        [w-chamfer,w],[-w+chamfer,w],[-w,w-chamfer],[-w,-w+chamfer]
    ]);
}
module nema17_front() {
    difference() {
        translate([0,0,-motor_cap_depth])
            nema17_outline(motor_body_width,motor_cap_depth,motor_corner_chamfer);
        for(x=[-motor_hole_pitch/2,motor_hole_pitch/2],y=[-motor_hole_pitch/2,motor_hole_pitch/2])
            translate([x,y,-motor_thread_depth]) cylinder(d=3,h=motor_thread_depth+0.01);
        translate([0,0,-motor_cap_depth-0.01]) cylinder(d=motor_shaft_diameter,h=motor_cap_depth+0.02);
    }
}
module nema17_stator() {
    translate([0,0,-motor_body_depth+motor_cap_depth])
        nema17_outline(motor_body_width,motor_body_depth-2*motor_cap_depth,motor_corner_chamfer);
}
module nema17_rear() {
    difference() {
        translate([0,0,-motor_body_depth])
            nema17_outline(motor_body_width,motor_cap_depth,motor_corner_chamfer);
        for(x=[-motor_hole_pitch/2,motor_hole_pitch/2],y=[-motor_hole_pitch/2,motor_hole_pitch/2])
            translate([x,y,-motor_body_depth-0.01]) cylinder(d=4.5,h=1.2);
    }
}
module nema17_pilot() {
    difference() {
        cylinder(d=motor_pilot_diameter,h=motor_pilot_height);
        translate([0,0,-0.01]) cylinder(d=motor_shaft_diameter,h=motor_pilot_height+0.02);
    }
}
module nema17_shaft() {
    linear_extrude(motor_shaft_length) intersection() {
        circle(d=motor_shaft_diameter);
        translate([-10,-10]) square([10+motor_shaft_diameter/2-motor_shaft_flat_depth,20]);
    }
}
module nema17_connector() {
    // Indicative connector envelope; actual cable exit depends on motor model.
    translate([-7,motor_body_width/2-1,-motor_body_depth+motor_cap_depth])
        cube([14,5,7]);
}
module nema17_reference() {
    color("Silver") { nema17_front(); nema17_rear(); nema17_pilot(); nema17_shaft(); }
    color([0.08,0.08,0.08]) nema17_stator();
    color([0.2,0.2,0.2]) nema17_connector();
}
