// One bank, motor-supported input and one upper 6810 output support.
// All purchased-hardware cutters are generated from OOBB with overhang=True.
$fn=circle_fragments;
eps=0.01;
roller_count=reduction;
cavity_count=roller_count+1;
roller_radius=roller_diameter/2;
pitch_radius=wave_radius+roller_radius;
cage_inner=pitch_radius-cage_wall/2;
cage_outer=pitch_radius+cage_wall/2;
housing_radius=32.5+output_holder_wall;
housing_flange_width=base_width*oobb_grid_pitch-oobb_size_allowance;
housing_flange_height=base_height*oobb_grid_pitch-oobb_size_allowance;
ring_z=motor_plate_depth;
cage_cap_z=ring_z+0.3;
window_z=cage_cap_z+cage_plate_depth;
wave_height=max(roller_length,10.2);
window_height=wave_height+2*roller_end_clearance;
wave_z=window_z+roller_end_clearance;
roller_z=wave_z+(wave_height-roller_length)/2;
cage_floor_z=window_z+window_height;
hub_z=cage_floor_z+cage_plate_depth;
bearing_z=hub_z+0.1;
ring_height=hub_z-ring_z;
hub_height=7.2;
retainer_z=hub_z+hub_height;

wave_cap_depth=4.2;
wave_seat_z=wave_height-wave_cap_depth-4-0.2;
wave_bearing_z=wave_z+wave_seat_z+0.1;
cam_z=wave_z+wave_seat_z-1;
cam_base_z=cage_cap_z;
cam_shoulder_z=cam_z-cam_base_z;
cam_cap_z=cam_z+5.2;
cam_cap_height=6.8;
cam_grub_z=cam_base_z+3.4;
cap_grub_z=cam_cap_z+3.4;
wave_head_recess=3.2;
wave_screw_length=6;
wave_nut_z=wave_height-wave_head_recess-wave_screw_length+0.3;
case_head_seat=3.2;
case_screw_length=30;
case_nut_z=case_head_seat+case_screw_length-2.7;
housing_top_z=case_nut_z+3.1;
housing_top_depth=housing_top_z-hub_z;
motor_head_seat=motor_plate_depth-3.2;
motor_screw_length=6;
output_plate_z=housing_top_z+output_face_clearance;
output_neck_height=output_plate_z-retainer_z;
retainer_depth=output_neck_height+output_plate_depth;
assembly_height=output_plate_z+output_plate_depth;
output_head_seat=assembly_height-output_socket_recess;
shaft_blind_depth=max(0,motor_shaft_length+motor_shaft_end_clearance-hub_z);
output_nut_z=cage_floor_z+0.3;
cage_head_seat=cage_cap_z+2.2;
cage_screw_length=wave_height<12?14:16;
cage_nut_z=hub_z-2.2;
wave_mounts=[for(a=[0:90:270]) [18*cos(a),18*sin(a)]];
output_mounts=[for(x=[-output_grid_pitch,output_grid_pitch],y=[-output_grid_pitch,output_grid_pitch]) [x,y]];
output_attachment_mounts=[[0,0],[output_grid_pitch,0],[-output_grid_pitch,0],[0,output_grid_pitch],[0,-output_grid_pitch]];
motor_mounts=[for(x=[-motor_hole_pitch/2,motor_hole_pitch/2],y=[-motor_hole_pitch/2,motor_hole_pitch/2]) [x,y]];
assert(overhang && max_screw_length<=35);
assert(roller_bank_count==1 && bearing_output=="6810" && bearing_wave=="6704");
assert(cam_cap_z+cam_cap_height<=motor_shaft_length-1,"Motor shaft too short");
assert(housing_top_depth>=hub_height+2,"Top bearing holder too thin");
include <compact_helpers.scad>;

module case_mounts() {
    for(i=[0:housing_screw_count-1]) rotate([0,0,360*i/housing_screw_count])
        translate([housing_screw_pitch_radius,0,0]) children();
}
module cage_mounts() {
    for(i=[0:cage_screw_count-1]) rotate([0,0,180/roller_count+360*i/cage_screw_count])
        translate([pitch_radius,0,0]) children();
}
module motor_mount_plate() {
    render(convexity=20) difference() {
        oobb_motor_plate_body();
        translate([0,0,-eps]) cylinder(r=9.5,h=motor_plate_depth+2*eps);
        translate([0,0,-eps]) cylinder(d=motor_pilot_diameter+0.2,h=motor_pilot_height+0.2+eps);
        grid_cuts(motor_plate_depth);
        // Hex-key access at cage angle zero; preload the M2 cap screws first.
        cage_mounts() translate([0,0,-eps]) screw_hole("m3",motor_plate_depth+2*eps);
        at_mounts(motor_mounts) {
            translate([0,0,-eps]) screw_hole("m3",motor_plate_depth+2*eps);
            translate([0,0,motor_head_seat]) socket_recess("m3",3.3);
        }
        case_mounts() {
            translate([0,0,-eps]) screw_hole("m3",motor_plate_depth+2*eps);
            translate([0,0,case_head_seat]) rotate([180,0,0]) socket_recess("m3",3.3);
        }
    }
}
module fixed_ring() {
    render(convexity=20) difference() {
        cylinder(r=housing_radius,h=ring_height);
        translate([0,0,-eps]) linear_extrude(ring_height+2*eps) polygon(profile_points());
        // Upper outer-race retaining lip; clear the cage and support only the outer race.
        translate([0,0,ring_height-0.3]) cylinder(r=31.5,h=0.4);
        case_mounts() translate([0,0,-eps]) screw_hole("m3",ring_height+2*eps);
    }
}
module output_housing() {
    // Print with bearing mouth upward; mirror this part in the assembly.
    render(convexity=20) difference() {
        cylinder(r=housing_radius,h=housing_top_depth);
        translate([0,0,-eps]) cylinder(r=31.5,h=housing_top_depth+2*eps);
        translate([0,0,housing_top_depth-hub_height]) cylinder(r=32.5+bearing_seat_clearance,h=hub_height+eps);
        case_mounts() {
            translate([0,0,-eps]) screw_hole("m3",housing_top_depth+2*eps);
            translate([0,0,-eps]) oobb_nut_m3();
            // Nut access from the exposed top face; the pocket bottoms at its seat.
            translate([0,0,-eps]) scale([1,1,(housing_top_z-case_nut_z+2*eps)/2.7]) oobb_nut_m3();
        }
    }
}
module cage() {
    // Print the floor down. In use the fingers point towards the motor.
    render(convexity=20) difference() {
        union() {
            tube(cage_outer,12.6,cage_plate_depth);
            translate([0,0,cage_plate_depth]) difference() {
                tube(cage_outer,cage_inner,window_height);
                for(i=[0:roller_count-1]) rotate([0,0,360*i/roller_count])
                    translate([cage_inner-2,-(roller_diameter+roller_slot_clearance)/2,(wave_height-roller_length)/2-eps])
                        cube([cage_wall+4,roller_diameter+roller_slot_clearance,roller_length+2*roller_end_clearance+2*eps]);
            }
        }
        at_mounts(output_mounts) {
            translate([0,0,-eps]) screw_hole("m3",cage_plate_depth+2*eps);
            translate([0,0,cage_plate_depth-2.7]) oobb_nut_m3();
        }
        cage_mounts() {
            translate([0,0,-eps]) screw_hole("m2",cage_plate_depth+window_height+2*eps);
            oobb_nut_m2();
        }
    }
}
module cage_cap() {
    render(convexity=20) difference() {
        tube(cage_outer,11,cage_plate_depth);
        cage_mounts() {
            translate([0,0,-eps]) screw_hole("m2",cage_plate_depth+2*eps);
            translate([0,0,2.2]) rotate([180,0,0]) socket_recess("m2",2.3);
        }
    }
}
module output_hub() {
    // Printed with the motor recess upward; assembly mirrors the part.
    difference() {
        cylinder(r=25-journal_clearance,h=hub_height);
        if(shaft_blind_depth>0) translate([0,0,hub_height-shaft_blind_depth]) cylinder(r=12.6,h=shaft_blind_depth+eps);
        at_mounts(output_mounts) translate([0,0,-eps]) screw_hole("m3",hub_height+2*eps);
        at_mounts(output_attachment_mounts) oobb_nut_m6();
    }
}
module output_retainer() {
    // Full output face prints downward. No input shaft projects through it.
    difference() {
        union() {
            cylinder(d=output_plate_diameter,h=output_plate_depth);
            translate([0,0,output_plate_depth]) cylinder(r=26.2,h=output_neck_height);
        }
        at_mounts(output_mounts) {
            translate([0,0,-eps]) screw_hole("m3",retainer_depth+2*eps);
            translate([0,0,output_socket_recess]) rotate([180,0,0]) socket_recess("m3",output_socket_recess+eps);
        }
        at_mounts(output_attachment_mounts) translate([0,0,-eps]) screw_hole("m6",retainer_depth+2*eps);
    }
}
module clamp_cuts(z) {
    // Nut enters from the outer radial surface. Grub screw bears on the D flat.
    translate([0,0,z]) rotate([0,90,0]) screw_hole("m3",12);
    translate([5,0,z]) rotate([0,90,0]) oobb_nut_m3();
    translate([5,-3.35,-eps]) cube([2.7,6.7,z+eps]);
}
module motor_eccentric() {
    difference() {
        union() {
            cylinder(r=9,h=cam_shoulder_z);
            translate([eccentricity,0,cam_shoulder_z]) cylinder(r=11,h=1);
            translate([eccentricity,0,cam_shoulder_z+1]) cylinder(r=10-journal_clearance,h=4.2);
        }
        translate([0,0,-eps]) shaft_cut(cam_shoulder_z+5.2+2*eps);
        clamp_cuts(3.4);
    }
}
module motor_eccentric_cap() {
    difference() {
        translate([eccentricity,0,0]) cylinder(r=11,h=cam_cap_height);
        translate([0,0,-eps]) shaft_cut(cam_cap_height+2*eps);
        clamp_cuts(3.4);
    }
}
module roller() { tube(roller_radius,roller_bore_diameter/2,roller_length); }
module cage_assembly(a=0,explode=0) {
    rotate([0,0,-a/roller_count]) {
        translate([0,0,cage_cap_z+explode]) cage_cap();
        translate([0,0,hub_z+5*explode]) mirror([0,0,1]) cage();
        translate([0,0,retainer_z+7*explode]) mirror([0,0,1]) output_hub();
        translate([0,0,assembly_height+9*explode]) mirror([0,0,1]) output_retainer();
    }
}
module input_assembly(a=0,explode=0) {
    rotate([0,0,a]) {
        translate([0,0,cam_base_z+2*explode]) motor_eccentric();
        translate([0,0,cam_cap_z+4*explode]) motor_eccentric_cap();
    }
}
module wave_assembly(a=0,explode=0) {
    p=polar(eccentricity,a);
    translate([p[0],p[1],wave_z+2*explode]) wave_generator();
    translate([p[0],p[1],wave_z+wave_height-wave_cap_depth+4*explode]) wave_cap();
}
module nominal_bearings(a=0,explode=0) {
    p=polar(eccentricity,a);
    translate([0,0,bearing_z+7*explode]) tube(32.5,25,7);
    translate([p[0],p[1],wave_bearing_z+3*explode]) tube(13.5,10,4);
}
module roller_assembly(a=0,explode=0) {
    for(i=[0:roller_count-1]) let(p=roller_position(i,a)) translate([p[0],p[1],roller_z+2*explode]) roller();
}
module fixed_assembly(explode=0) {
    motor_mount_plate();
    translate([0,0,ring_z+explode]) fixed_ring();
    translate([0,0,housing_top_z+8*explode]) mirror([0,0,1]) output_housing();
}
module assembly(a=0,explode=0) {
    color("Turquoise") fixed_assembly(explode);
    color([0.08,0.08,0.08]) cage_assembly(a,explode);
    color("Goldenrod") input_assembly(a,explode);
    color("SteelBlue") wave_assembly(a,explode);
    color("Silver") nominal_bearings(a,explode);
    color("Ivory") roller_assembly(a,explode);
}
module motion_section(a=0) {
    color("Turquoise") difference() { circle(r=housing_radius); polygon(profile_points()); }
    color("SteelBlue") translate(polar(eccentricity,a)) difference() { circle(r=wave_radius); circle(r=13.5); }
    for(i=[0:roller_count-1]) color("Ivory") translate(roller_position(i,a)) difference() { circle(r=roller_radius); circle(d=roller_bore_diameter); }
}
module fit_coupons() {
    tube(36,32.5+bearing_seat_clearance,4);
    translate([60,0,0]) tube(18,13.5+bearing_seat_clearance,4);
    translate([110,0,0]) tube(25-journal_clearance,22,4);
    translate([150,0,0]) tube(10-journal_clearance,7,4);
    translate([0,55,0]) difference() { translate([-10,-10,0]) cube([20,20,5]); translate([0,0,-eps]) shaft_cut(6); }
    translate([40,55,0]) difference() { translate([-12,-8,0]) cube([24,16,4]); translate([-8,-(roller_diameter+roller_slot_clearance)/2,-eps]) cube([16,roller_diameter+roller_slot_clearance,5]); }
    translate([70,55,0]) roller();
    translate([100,55,0]) difference() { translate([-6,-6,0]) cube([12,12,6]); oobb_nut_m3(); translate([0,0,-eps]) screw_hole("m3",7); }
}
module collision_check(a=0) {
    translate([70,0,0]) cube([1,1,1]);
    intersection() { fixed_assembly(); union() { cage_assembly(a); input_assembly(a); wave_assembly(a); roller_assembly(a); } }
    intersection() { cage_assembly(a); union() { input_assembly(a); wave_assembly(a); roller_assembly(a); } }
    intersection() { input_assembly(a); wave_assembly(a); }
    intersection() { nominal_bearings(a); union() { fixed_assembly(); cage_assembly(a); input_assembly(a); wave_assembly(a); } }
}
