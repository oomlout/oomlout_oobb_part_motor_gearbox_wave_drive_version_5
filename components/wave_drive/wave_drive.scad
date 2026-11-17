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
housing_radius=32.5+bearing_seat_clearance+output_holder_wall;
case_boss_radius=mount_m3_pocket_radius+case_boss_wall;
case_boss_inner_radius=housing_radius-case_boss_overlap-case_boss_radius;
case_boss_outer_radius=housing_screw_pitch_radius+case_boss_radius;
case_boss_radial_depth=case_boss_outer_radius-case_boss_inner_radius;
case_boss_corner_radius=case_boss_rounding_fraction*min(case_boss_outer_radius-housing_screw_pitch_radius,case_boss_radius,case_boss_radial_depth/2);
case_boss_center_radius=(case_boss_inner_radius+case_boss_outer_radius)/2;
cage_screw_count=roller_count;
cage_screw_radius=pitch_radius+cage_screw_radial_offset;
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
cage_head_lift=cage_screw_length-cage_screw_reference_length+cage_tip_extra_clearance;
cage_upper_plate_depth=cage_plate_depth+cage_head_lift;
hub_z=cage_floor_z+cage_upper_plate_depth;
bearing_z=hub_z+0.1;
ring_height=hub_z-ring_z;
bearing_stack_height=7.2;
hub_height=output_hub_depth;
retainer_z=hub_z+hub_height;

wave_seat_z=(wave_height-4)/2-0.4;
wave_bearing_z=wave_z+wave_seat_z+0.1;
wave_split_z=wave_bearing_z+2;
wave_lower_depth=wave_split_z-wave_z;
wave_cap_depth=wave_height-wave_lower_depth;
cam_z=wave_z+wave_seat_z-1;
cam_base_z=shaft_clamp_axis_z-3.4;
cam_shoulder_z=cam_z-cam_base_z;
cam_cap_z=cam_z+5.2;
cam_cap_height=6.8;
shaft_clamp_z=shaft_clamp_axis_z;
eccentric_join_head_z=cam_cap_z+cam_cap_height+countersunk_head_proud;
eccentric_join_nut_z=eccentric_join_head_z-eccentric_join_screw_length+0.1;
eccentric_join_mounts=[[eccentricity,-eccentric_join_pitch_radius],[eccentricity,eccentric_join_pitch_radius]];
wave_head_recess=-countersunk_head_proud;
wave_nut_z=wave_height-wave_head_recess-wave_screw_length+0.3;
housing_top_z=hub_z+bearing_stack_height+3.5;
case_socket_depth=case_socket_recess+cage_head_lift;
case_head_seat=housing_top_z-case_socket_depth;
housing_top_depth=housing_top_z-hub_z;
motor_head_seat=motor_plate_depth+countersunk_head_proud;
motor_head_relief_depth=max(0,motor_head_seat+countersunk_head_clearance-cage_cap_z);
wave_head_relief_depth=max(0,wave_z+wave_height-wave_head_recess+countersunk_head_clearance-cage_floor_z);
assembly_height=housing_top_z+output_above_housing;
output_cover_z=assembly_height-output_cover_depth;
output_plate_z=output_cover_z;
output_flange_z=housing_top_z+output_face_clearance;
output_neck_height=output_cover_z-retainer_z;
retainer_depth=output_neck_height;
output_head_seat=assembly_height+countersunk_head_proud;
shaft_blind_depth=max(0,motor_shaft_length+motor_shaft_end_clearance-hub_z);
output_nut_z=cage_floor_z+cage_head_lift+0.3;
cage_head_seat=hub_z;
cage_nut_z=cage_head_seat-cage_screw_length;
wave_mounts=[for(a=[0:90:270]) [18*cos(a),18*sin(a)]];
output_mounts=[[output_fixing_x,output_fixing_y],[-output_fixing_y,output_fixing_x],[-output_fixing_x,-output_fixing_y],[output_fixing_y,-output_fixing_x]];
output_attachment_mounts=[[0,0],[output_grid_pitch,0],[-output_grid_pitch,0],[0,output_grid_pitch],[0,-output_grid_pitch]];
function separated(p,points,d)=len(points)==0?true:min([for(q=points) norm(p-q)])>=d;
function select_m3_mounts(points,index=0,selected=[])=index>=len(points)?selected:
    select_m3_mounts(points,index+1,separated(points[index],selected,2*mount_m3_pocket_radius+mount_minimum_web)?concat(selected,[points[index]]):selected);
function m3_mount_angle(p)=atan2(p[1],p[0])-30;
function m3_pocket_points(p)=[for(q=concat(
    [for(a=[0:60:300]) polar(mount_m3_hex_radius,a)],
    [for(x=[-mount_m3_bridge_half_width,mount_m3_bridge_half_width],y=[-mount_m3_bridge_half_height,mount_m3_bridge_half_height]) [x,y]]))
    p+rotate_point(q,m3_mount_angle(p))];
output_m3_candidates=[for(i=[-floor(output_plate_diameter/output_grid_pitch):floor(output_plate_diameter/output_grid_pitch)],j=[-floor(output_plate_diameter/output_grid_pitch):floor(output_plate_diameter/output_grid_pitch)])
    let(p=[i*output_grid_pitch/2,j*output_grid_pitch/2])
    if(max([for(q=m3_pocket_points(p)) norm(q)])+mount_m3_edge_wall<=min(output_plate_diameter/2,25-journal_clearance) &&
       separated(p,output_attachment_mounts,mount_m3_pocket_radius+mount_m6_pocket_radius+mount_minimum_web) &&
       separated(p,output_mounts,mount_m3_pocket_radius+1.8+mount_minimum_web)) p];
output_m3_attachment_mounts=select_m3_mounts(output_m3_candidates);
motor_mounts=[for(x=[-motor_hole_pitch/2,motor_hole_pitch/2],y=[-motor_hole_pitch/2,motor_hole_pitch/2]) [x,y]];
assert(overhang && max_screw_length<=35);
assert(roller_bank_count==1 && bearing_output=="6810" && bearing_wave=="6704");
assert(cam_cap_z+cam_cap_height<=motor_shaft_length-1,"Motor shaft too short");
assert(housing_top_depth>=bearing_stack_height+2,"Top bearing holder too thin");
include <compact_helpers.scad>;

module case_mounts() {
    for(i=[0:housing_screw_count-1]) rotate([0,0,housing_screw_angle+360*i/housing_screw_count])
        translate([housing_screw_pitch_radius,0,0]) children();
}
module cage_mounts() {
    for(i=[0:cage_screw_count-1]) rotate([0,0,180/roller_count+360*i/cage_screw_count])
        translate([cage_screw_radius,0,0]) children();
}
module case_body(h) {
    union() {
        cylinder(r=housing_radius,h=h);
        for(i=[0:housing_screw_count-1]) rotate([0,0,housing_screw_angle+360*i/housing_screw_count])
            translate([case_boss_center_radius,0,0])
                rounded_rectangle_plate([case_boss_radial_depth,2*case_boss_radius,h],case_boss_corner_radius);
    }
}
module motor_mount_plate() {
    render(convexity=20) difference() {
        union() {
            oobb_motor_plate_body();
            case_body(motor_plate_depth);
        }
        translate([0,0,-eps]) cylinder(r=9.5,h=motor_plate_depth+2*eps);
        translate([0,0,-eps]) cylinder(d=motor_pilot_diameter+0.2,h=motor_pilot_height+0.2+eps);
        // The recessed eccentric and its screw head must clear at every input angle.
        translate([0,0,motor_pilot_height+0.2]) cylinder(r=11.1,h=motor_plate_depth);
        grid_cuts(motor_plate_depth);
        at_mounts(motor_mounts) {
            translate([0,0,-eps]) screw_hole("m3",motor_plate_depth+2*eps);
            translate([0,0,motor_head_seat]) oobb_motor_countersunk_m3();
        }
        case_mounts() {
            translate([0,0,-eps]) screw_hole("m3",motor_plate_depth+2*eps);
            // Nuts load from underneath; the bridge retains the hex pocket roof.
            translate([0,0,-eps]) oobb_nut_m3();
        }
    }
}
module fixed_ring() {
    render(convexity=20) difference() {
        case_body(ring_height);
        translate([0,0,-eps]) linear_extrude(ring_height+2*eps) polygon(profile_points());
        // Upper outer-race retaining lip; clear the cage and support only the outer race.
        translate([0,0,ring_height-0.3]) cylinder(r=31.5,h=0.4);
        case_mounts() translate([0,0,-eps]) screw_hole("m3",ring_height+2*eps);
        translate([0,0,shaft_clamp_z-ring_z]) shaft_service_port();
    }
}
module output_housing() {
    // Print with bearing mouth upward; mirror this part in the assembly.
    render(convexity=20) difference() {
        case_body(housing_top_depth);
        translate([0,0,-eps]) cylinder(r=31.5,h=housing_top_depth+2*eps);
        translate([0,0,housing_top_depth-bearing_stack_height]) cylinder(r=32.5+bearing_seat_clearance,h=bearing_stack_height+eps);
        case_mounts() {
            translate([0,0,-eps]) screw_hole("m3",housing_top_depth+2*eps);
            // Housing prints upside down. Restore the top-entering socket recess.
            translate([0,0,case_socket_depth]) rotate([180,0,0]) socket_recess("m3",case_socket_depth+eps);
        }
    }
}
module cage_face_down() {
    // Intermediate construction coordinates; cage() gives the printing orientation.
    render(convexity=20) difference() {
        union() {
            cylinder(r=25-journal_clearance,h=hub_height);
            translate([0,0,hub_height]) tube(cage_outer,12.6,cage_upper_plate_depth);
        }
        if(shaft_blind_depth>0) translate([0,0,hub_height-shaft_blind_depth]) cylinder(r=12.6,h=shaft_blind_depth+cage_upper_plate_depth+eps);
        // A full annular sweep clears the proud wave screws at every input angle.
        if(wave_head_relief_depth>0)
            translate([0,0,hub_height+cage_upper_plate_depth-wave_head_relief_depth])
                tube(18+eccentricity+m3_countersunk_radius+countersunk_head_clearance,
                    18-eccentricity-m3_countersunk_radius-countersunk_head_clearance,
                    wave_head_relief_depth+eps);
        at_mounts(output_mounts) {
            translate([0,0,-eps]) screw_hole("m3",hub_height+cage_upper_plate_depth+2*eps);
            translate([0,0,hub_height+cage_upper_plate_depth-(2.7+cage_head_lift)])
                scale([1,1,(2.7+cage_head_lift)/2.7]) oobb_nut_m3();
        }
        cage_mounts() {
            translate([0,0,-eps]) screw_hole("m2",hub_height+cage_upper_plate_depth+2*eps);
            translate([0,0,hub_height]) rotate([180,0,0]) oobb_cage_countersunk_m2();
        }
    }
}
module cage() {
    // Broad closure on the bed, integrated hub upward. The central blind roof bridges.
    translate([0,0,hub_height+cage_upper_plate_depth]) mirror([0,0,1]) cage_face_down();
}
module cage_cap() {
    // Lower ring and every tooth print together, teeth upright.
    render(convexity=20) difference() {
        union() {
            tube(cage_outer,cage_center_diameter/2,cage_plate_depth);
            translate([0,0,cage_plate_depth]) difference() {
                tube(cage_outer,cage_inner,window_height);
                for(i=[0:roller_count-1]) rotate([0,0,360*i/roller_count])
                    translate([cage_inner-2,-(roller_diameter+roller_slot_clearance)/2,(wave_height-roller_length)/2-eps])
                        cube([cage_wall+4,roller_diameter+roller_slot_clearance,roller_length+2*roller_end_clearance+2*eps]);
            }
        }
        cage_mounts() {
            translate([0,0,-eps]) screw_hole("m2",cage_plate_depth+window_height+2*eps);
            translate([0,0,-eps]) scale([1,1,(cage_nut_z+1.6-cage_cap_z+eps)/2.2]) oobb_nut_m2();
        }
        // This ring rotates over the four stationary motor screw heads.
        if(motor_head_relief_depth>0) translate([0,0,-eps])
            tube(sqrt(2)*motor_hole_pitch/2+m3_countersunk_radius+countersunk_head_clearance,
                sqrt(2)*motor_hole_pitch/2-m3_countersunk_radius-countersunk_head_clearance,
                motor_head_relief_depth+eps);
        translate([0,0,shaft_clamp_z-cage_cap_z]) shaft_service_port();
    }
}
module shaft_service_port() {
    // Alignment: eccentric +X, lower cage service bore +X, housing bore +X.
    translate([shaft_clamp_head_radius,0,0]) rotate([0,90,0]) cylinder(d=shaft_access_diameter,h=60);
}
module output_retainer() {
    // Print pocket mouths on the bed; in use they face up into the separate cover.
    difference() {
        union() {
            cylinder(r=25-journal_clearance,h=retainer_depth);
            cylinder(r=26.2,h=output_cover_z-(hub_z+bearing_stack_height));
        }
        at_mounts(output_mounts) translate([0,0,-eps]) screw_hole("m3",retainer_depth+2*eps);
        at_mounts(output_attachment_mounts) oobb_nut_m6();
        for(p=output_m3_attachment_mounts) translate([p[0],p[1],0]) rotate([0,0,m3_mount_angle(p)])
            scale([1,1,output_m3_nut_depth/2.7]) oobb_nut_m3();
    }
}
module output_cover() {
    // Printed and assembled face up. Closed pocket floors keep payload bolts blind.
    difference() {
        union() {
            cylinder(r=31.5-output_radial_clearance,h=output_cover_depth);
            translate([0,0,output_flange_z-output_cover_z]) cylinder(d=output_plate_diameter,h=assembly_height-output_flange_z);
        }
        at_mounts(output_mounts) {
            translate([0,0,-eps]) screw_hole("m3",output_cover_depth+2*eps);
            translate([0,0,output_cover_depth+countersunk_head_proud]) oobb_countersunk_m3();
        }
        at_mounts(output_attachment_mounts) translate([0,0,-eps]) screw_hole("m6",output_cover_depth+2*eps);
        at_mounts(output_m3_attachment_mounts) translate([0,0,-eps]) screw_hole("m3",output_cover_depth+2*eps);
    }
}
module clamp_cuts(z) {
    // Captive M3 nut; top head clearance lets the screw press onto the motor shaft.
    translate([0,0,z]) rotate([0,90,0]) screw_hole("m3",12);
    translate([shaft_clamp_head_radius,0,z]) rotate([0,90,0]) oobb_shaft_clamp_m3();
    translate([5,0,z]) rotate([0,90,0]) oobb_nut_m3();
    translate([5,-3.35,-eps]) cube([2.7,6.7,z+eps]);
}
module motor_eccentric() {
    difference() {
        union() {
            cylinder(r=9,h=cam_shoulder_z);
            translate([0,0,cage_cap_z-cam_base_z]) cylinder(r=10.5,h=cam_shoulder_z-(cage_cap_z-cam_base_z));
            translate([eccentricity,0,cam_shoulder_z]) cylinder(r=11,h=1);
            translate([eccentricity,0,cam_shoulder_z+1]) cylinder(r=10-journal_clearance,h=4.2);
        }
        translate([0,0,-eps]) shaft_cut(cam_shoulder_z+5.2+2*eps);
        clamp_cuts(3.4);
        at_mounts(eccentric_join_mounts) {
            translate([0,0,-eps]) screw_hole("m3",cam_shoulder_z+5.2+2*eps);
            translate([0,0,-eps]) scale([1,1,(eccentric_join_nut_z+2.5-cam_base_z+eps)/2.7]) oobb_nut_m3();
        }
    }
}
module motor_eccentric_cap() {
    difference() {
        translate([eccentricity,0,0]) cylinder(r=11,h=cam_cap_height);
        translate([0,0,-eps]) shaft_cut(cam_cap_height+2*eps);
        at_mounts(eccentric_join_mounts) {
            translate([0,0,-eps]) screw_hole("m3",cam_cap_height+2*eps);
            translate([0,0,cam_cap_height+countersunk_head_proud]) oobb_countersunk_m3();
        }
    }
}
module roller() { tube(roller_radius,roller_bore_diameter/2,roller_length); }
module cage_assembly(a=0,explode=0) {
    rotate([0,0,-a/roller_count]) {
        translate([0,0,cage_cap_z+explode]) cage_cap();
        translate([0,0,cage_floor_z+9*explode]) cage();
        translate([0,0,output_cover_z+13*explode]) mirror([0,0,1]) output_retainer();
        translate([0,0,output_cover_z+14*explode]) output_cover();
    }
}
module input_assembly(a=0,explode=0) {
    rotate([0,0,a]) {
        translate([0,0,cam_base_z+3*explode]) motor_eccentric();
        translate([0,0,cam_cap_z+6*explode]) motor_eccentric_cap();
    }
}
module wave_assembly(a=0,explode=0) {
    p=polar(eccentricity,a);
    translate([p[0],p[1],wave_z+4*explode]) wave_generator();
    translate([p[0],p[1],wave_split_z+7*explode]) wave_cap();
}
module nominal_bearings(a=0,explode=0) {
    p=polar(eccentricity,a);
    translate([0,0,bearing_z+11*explode]) tube(32.5,25,7);
    translate([p[0],p[1],wave_bearing_z+5*explode]) tube(13.5,10,4);
}
module roller_assembly(a=0,explode=0) {
    for(i=[0:roller_count-1]) let(p=roller_position(i,a)) translate([p[0],p[1],roller_z+8*explode]) roller();
}
module fixed_assembly(explode=0) {
    motor_mount_plate();
    translate([0,0,ring_z+2*explode]) fixed_ring();
    translate([0,0,housing_top_z+12*explode]) mirror([0,0,1]) output_housing();
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
