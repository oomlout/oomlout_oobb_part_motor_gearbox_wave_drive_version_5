// Two rigid roller-wave banks, opposed eccentrics, one common output cage.
// Millimetres. Native geometry; OOBB supplies hardware clearances and bridge cuts.
$fn=circle_fragments;
eps=0.01;
roller_count=reduction;
cavity_count=roller_count+1;
roller_radius=roller_diameter/2;
pitch_radius=wave_radius+roller_radius;
cage_inner=pitch_radius-cage_wall/2;
cage_outer=pitch_radius+cage_wall/2;
cage_joint_radius=cage_outer+1;
stationary_joint_inner_radius=cage_joint_radius+1;
bearing_z=housing_flange_depth;
ring_z=bearing_z+7;
cage_base_z=ring_z+bearing_axial_clearance;
window_z=cage_base_z+cage_plate_depth;
wave_height=max(roller_length,10.2);
window_height=wave_height+2*roller_end_clearance;
wave_z=window_z+roller_end_clearance;
roller_z=wave_z+(wave_height-roller_length)/2;
joint_z=window_z+window_height;
mirror_z=joint_z+central_joint_depth/2;
assembly_height=2*mirror_z;
ring_height=joint_z-ring_z;
shaft_length=5*ceil((assembly_height+25)/5);
wave_cap_depth=4.2;
wave_seat_z=wave_height-wave_cap_depth-4-bearing_axial_clearance;
wave_bearing_z=wave_z+wave_seat_z+bearing_axial_clearance/2;
cam_z=wave_z+wave_seat_z-1;
cam_height=5+bearing_axial_clearance;
outer_spacer_z=bearing_z+5+bearing_axial_clearance;
outer_spacer_length=cam_z-outer_spacer_z;
middle_spacer_z=cam_z+cam_height;
middle_spacer_length=mirror_z-middle_spacer_z;
case_head_seat=3.2;
case_screw_length=12;
case_nut_z=case_head_seat+case_screw_length-3;
output_head_recess=2;
output_screw_length=12;
wave_head_recess=3.2;
wave_screw_length=6;
wave_nut_z=wave_height-wave_head_recess-wave_screw_length+0.3;
available_screws=[6,8,10,12,14,16,18,20,25,30,35];
function choose_screw(target,seat)=max([for(v=available_screws) if(v<=min(max_screw_length,target-seat)+eps) v]);
ring_join_screw_length=choose_screw(joint_z+3,ring_z+3.2);
ring_join_head_seat=joint_z+3-ring_join_screw_length;
cage_screw_length=choose_screw(joint_z+2.6,cage_base_z+2.2);
cage_head_seat=joint_z+2.6-cage_screw_length;
upper_profile_rotation=180/cavity_count;
mounts=[for(x=[-15,-7.5,7.5,15],y=[-15,-7.5,7.5,15]) if(abs(x)!=abs(y)) [x,y]];
wave_mounts=[for(a=[0:90:270]) [18*cos(a),18*sin(a)]];

assert(overhang && max_screw_length<=35,"Use OOBB overhang and screws <=35 mm");
assert(central_joint_depth>=6,"Opposed nut pockets need a 6 mm joint");
assert(roller_count>=2*cage_screw_count && roller_count%cage_screw_count==0,"Cage nut patterns must be distinct");
assert(bearing_output=="6810" && bearing_input=="6704" && bearing_wave=="6704");
assert(cage_inner-wave_radius-eccentricity>=0.2);
assert(wave_radius+roller_diameter-eccentricity-cage_outer>=0.2);

function polar(r,a)=[r*cos(a),r*sin(a)];
function rotate_point(p,a)=[p[0]*cos(a)-p[1]*sin(a),p[0]*sin(a)+p[1]*cos(a)];
function profile_point(t)=let(
    s=sqrt(pow(pitch_radius,2)-pow(eccentricity*sin(cavity_count*t),2)),
    r=eccentricity*cos(cavity_count*t)+s,
    xi=atan2(eccentricity*cavity_count*sin(cavity_count*t),s),
    rr=roller_radius+profile_clearance)
    [r*cos(t)+rr*cos(t+xi),r*sin(t)+rr*sin(t+xi)];
function profile_points(upper=false)=[for(i=[0:cavity_count*profile_samples_per_cavity-1])
    rotate_point(profile_point(360*i/(cavity_count*profile_samples_per_cavity)),upper?upper_profile_rotation:0)];
function roller_position(i,a,upper=false)=let(
    t=-a/roller_count+360*i/roller_count,
    rel=t-a-(upper?180:0),
    r=eccentricity*cos(rel)+sqrt(pow(pitch_radius,2)-pow(eccentricity*sin(rel),2))) polar(r,t);
function case_clock(upper=false)=upper?11.25:0;
function cage_clock(upper=false)=180/roller_count+(upper?360/roller_count:0);

module tube(ro,ri,h) { difference() { cylinder(r=ro,h=h); translate([0,0,-eps]) cylinder(r=ri,h=h+2*eps); } }
module screw_hole(size,h) { scale([1,1,h]) { if(size=="m2") oobb_hole_m2(); if(size=="m3") oobb_hole_m3(); if(size=="m6") oobb_hole_m6(); } }
module socket_recess(size,depth) {
    // OOBB socket head starts at the under-head plane and extends outward.
    scale([1,1,depth/(size=="m3"?3.2:2.2)]) {
        if(size=="m3") oobb_socket_m3(); else oobb_socket_m2();
    }
}
module at_mounts(points) { for(p=points) translate([p[0],p[1],0]) children(); }
module case_mounts(upper=false,join=false) {
    // One offset joint screw keys the 21-cavity profiles to the centre ring.
    for(i=[0:housing_screw_count-1]) rotate([0,0,case_clock(upper)+(join?22.5:0)+(join && i==0?5:0)+360*i/housing_screw_count])
        translate([housing_screw_pitch_radius,0,0]) children();
}
module cage_mounts(upper=false) {
    for(i=[0:cage_screw_count-1]) rotate([0,0,cage_clock(upper)+360*i/cage_screw_count])
        translate([pitch_radius,0,0]) children();
}
module upper_mirror(extra=0) { translate([0,0,assembly_height+extra]) mirror([0,0,1]) children(); }
module shaft_cut(h,fit=shaft_fit_clearance) {
    linear_extrude(h) intersection() {
        circle(r=input_shaft_diameter/2+fit);
        translate([-10,-10]) square([10+input_shaft_diameter/2-input_shaft_flat_depth+fit,20]);
    }
}
module rounded_rectangle_plate(size=[119,119,3],radius=1.5) {
    hull() for(x=[-1,1],y=[-1,1]) translate([x*(size[0]/2-radius),y*(size[1]/2-radius),0]) cylinder(r=radius,h=size[2]);
}
module grid_cuts(h) {
    for(i=[-7:7],j=[-7:7]) let(x=7.5*i,y=7.5*j,r=sqrt(x*x+y*y),full=(i%2==0 && j%2==0),envelope=full?5.95:3.35)
        if(r>housing_radius+envelope && max(abs(x),abs(y))+envelope<housing_flange_width/2)
            translate([x,y,-eps]) screw_hole(full?"m6":"m3",h+2*eps);
}
module housing(top=false) {
    render(convexity=20) difference() {
        union() {
            rounded_rectangle_plate([housing_flange_width,housing_flange_width,housing_flange_depth],housing_flange_corner_radius);
            cylinder(r=housing_radius,h=ring_z);
        }
        translate([0,0,-eps]) cylinder(r=31.5,h=ring_z+2*eps);
        translate([0,0,bearing_z]) cylinder(r=32.5+bearing_seat_clearance,h=7+eps);
        grid_cuts(housing_flange_depth);
        case_mounts(top) {
            translate([0,0,-eps]) screw_hole("m3",ring_z+2*eps);
            translate([0,0,case_head_seat]) rotate([180,0,0]) socket_recess("m3",case_head_seat+eps);
        }
    }
}
module fixed_ring(top=false) {
    render(convexity=20) difference() {
        cylinder(r=housing_radius,h=ring_height);
        translate([0,0,-eps]) linear_extrude(ring_height+2*eps) polygon(profile_points(top));
        case_mounts(top) {
            translate([0,0,-eps]) screw_hole("m3",case_nut_z-ring_z+3.4);
            translate([0,0,case_nut_z-ring_z]) oobb_nut_m3();
            // Radial loading slot for the end-housing captive nut.
            translate([0,-3.5,case_nut_z-ring_z]) cube([housing_radius-housing_screw_pitch_radius+eps,7,2.7]);
        }
        case_mounts(top,true) {
            translate([0,0,-eps]) screw_hole("m3",ring_height+2*eps);
            translate([0,0,ring_join_head_seat-ring_z]) rotate([180,0,0]) socket_recess("m3",ring_join_head_seat-ring_z+eps);
        }
    }
}
module stationary_joint() {
    render(convexity=20) difference() {
        tube(housing_radius,stationary_joint_inner_radius,central_joint_depth);
        for(top=[false,true]) case_mounts(top,true) {
            translate([0,0,-eps]) screw_hole("m3",central_joint_depth+2*eps);
            translate([0,0,top?central_joint_depth-2.7:0]) oobb_nut_m3();
        }
        translate([52,-2,central_joint_depth-0.4]) linear_extrude(0.5) text("UP",size=2.2);
    }
}
module output_hub() {
    render(convexity=20) difference() {
        cylinder(r=25-journal_clearance,h=7+bearing_axial_clearance);
        translate([0,0,-eps]) cylinder(r=12.6,h=7+bearing_axial_clearance+2*eps);
        translate([0,0,-eps]) cylinder(r=13.5+bearing_seat_clearance,h=4+bearing_axial_clearance+eps);
        at_mounts(mounts) translate([0,0,-eps]) screw_hole("m3",8);
        for(x=[-15,15],y=[-15,15]) translate([x,y,-eps]) screw_hole("m3",8);
    }
}
module output_retainer() {
    render(convexity=20) difference() {
        tube(26.2,12.6,retainer_depth);
        at_mounts(mounts) {
            translate([0,0,-eps]) screw_hole("m3",retainer_depth+2*eps);
            translate([0,0,output_head_recess]) rotate([180,0,0]) socket_recess("m3",3.3);
        }
        for(x=[-15,15],y=[-15,15]) translate([x,y,-eps]) screw_hole("m3",retainer_depth+2*eps);
    }
}
module cage(top=false) {
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
        at_mounts(mounts) {
            translate([0,0,-eps]) screw_hole("m3",cage_plate_depth+2*eps);
            translate([0,0,cage_plate_depth-2.7]) oobb_nut_m3();
        }
        for(x=[-15,15],y=[-15,15]) translate([x,y,-eps]) screw_hole("m3",cage_plate_depth+2*eps);
        cage_mounts(top) {
            translate([0,0,-eps]) screw_hole("m2",cage_plate_depth+window_height+2*eps);
            translate([0,0,cage_head_seat-cage_base_z]) rotate([180,0,0]) socket_recess("m2",cage_head_seat-cage_base_z+eps);
        }
    }
}
module cage_joint() {
    render(convexity=20) difference() {
        tube(cage_joint_radius,12.6,central_joint_depth);
        for(top=[false,true]) cage_mounts(top) {
            translate([0,0,-eps]) screw_hole("m2",central_joint_depth+2*eps);
            translate([0,0,top?central_joint_depth-2.2:0]) oobb_nut_m2();
        }
    }
}
module wave_generator() {
    render(convexity=20) difference() {
        tube(wave_radius,12.6,wave_height);
        translate([0,0,wave_seat_z]) cylinder(r=13.5+bearing_seat_clearance,h=wave_height);
        translate([0,0,wave_height-wave_cap_depth]) cylinder(r=22.15,h=wave_cap_depth+eps);
        at_mounts(wave_mounts) {
            translate([0,0,-eps]) screw_hole("m3",wave_height+2*eps);
            translate([0,0,wave_nut_z]) scale([1,1,(wave_height-wave_cap_depth-wave_nut_z+eps)/2.7]) oobb_nut_m3();
        }
    }
}
module wave_cap() {
    render(convexity=20) difference() {
        tube(22,12.6,wave_cap_depth);
        at_mounts(wave_mounts) {
            translate([0,0,-eps]) screw_hole("m3",wave_cap_depth+2*eps);
            translate([0,0,wave_cap_depth-wave_head_recess]) socket_recess("m3",wave_head_recess+eps);
        }
    }
}
module eccentric_cam(top=false) {
    difference() {
        union() {
            translate([top?-eccentricity:eccentricity,0,0]) cylinder(r=11,h=1);
            translate([top?-eccentricity:eccentricity,0,1]) cylinder(r=10-journal_clearance,h=4+bearing_axial_clearance);
        }
        translate([0,0,-eps]) shaft_cut(cam_height+2*eps);
    }
}
module input_journal() {
    difference() {
        union() { cylinder(r=10-journal_clearance,h=4+bearing_axial_clearance); translate([0,0,4+bearing_axial_clearance]) cylinder(r=11,h=1); }
        translate([0,0,-eps]) shaft_cut(5+bearing_axial_clearance+2*eps);
    }
}
module input_spacer(h,shoulder=false,top=false) {
    difference() {
        union() {
            cylinder(r=7,h=h);
            if(shoulder) translate([top?-eccentricity:eccentricity,0,0]) cylinder(r=11,h=1);
        }
        translate([0,0,-eps]) shaft_cut(h+2*eps);
    }
}
module input_collar() {
    difference() {
        union() { cylinder(r=18,h=3); translate([0,0,3]) cylinder(r=10.5,h=10); }
        translate([0,0,-eps]) shaft_cut(13+2*eps);
        translate([0,0,7]) rotate([0,90,0]) screw_hole("m3",12);
        translate([5,0,7]) rotate([0,90,0]) oobb_nut_m3();
        translate([5,-3.35,-eps]) cube([2.7,6.7,7+eps]);
    }
}
module roller() { tube(roller_radius,roller_bore_diameter/2,roller_length); }
module bank_mirror(top=false,extra=0) { if(top) upper_mirror(extra) children(); else translate([0,0,-extra]) children(); }
module cage_assembly(a=0,explode=0) {
    rotate([0,0,-a/roller_count]) {
        for(top=[false,true]) bank_mirror(top,2*explode) {
            translate([0,0,cage_base_z]) cage(top);
            translate([0,0,bearing_z-explode]) output_hub();
            translate([0,0,bearing_z-retainer_depth-2*explode]) output_retainer();
        }
        translate([0,0,joint_z]) cage_joint();
    }
}
module input_assembly(a=0,explode=0) {
    rotate([0,0,a]) {
        for(top=[false,true]) bank_mirror(top,explode) {
            translate([0,0,cam_z]) eccentric_cam(top);
            translate([0,0,bearing_z-2*explode]) input_journal();
            translate([0,0,outer_spacer_z-explode]) input_spacer(outer_spacer_length);
            translate([0,0,middle_spacer_z]) input_spacer(middle_spacer_length,true,top);
            translate([0,0,bearing_z-13-3*explode]) input_collar();
        }
        translate([0,0,-12]) shaft_cut(shaft_length,0);
    }
}
module wave_assembly(a=0,explode=0) {
    for(top=[false,true]) let(p=polar(eccentricity,a+(top?180:0))) bank_mirror(top,explode) {
        translate([p[0],p[1],wave_z]) wave_generator();
        translate([p[0],p[1],wave_z+wave_height-wave_cap_depth+0.5*explode]) wave_cap();
    }
}
module nominal_bearings(a=0,explode=0) {
    for(top=[false,true]) let(p=polar(eccentricity,a+(top?180:0))) bank_mirror(top,explode) {
        translate([0,0,bearing_z-2*explode]) tube(32.5,25,7);
        translate([0,0,bearing_z+bearing_axial_clearance/2-2*explode]) tube(13.5,10,4);
        translate([p[0],p[1],wave_bearing_z]) tube(13.5,10,4);
    }
}
module roller_assembly(a=0,explode=0) {
    for(top=[false,true]) bank_mirror(top,explode)
        for(i=[0:roller_count-1]) let(p=roller_position(i,a,top)) translate([p[0],p[1],roller_z]) roller();
}
module fixed_assembly(explode=0) {
    for(top=[false,true]) bank_mirror(top,4*explode) {
        housing(top);
        translate([0,0,ring_z+2*explode]) fixed_ring(top);
    }
    translate([0,0,joint_z]) stationary_joint();
}
module assembly(a=0,explode=0) {
    color("Turquoise") fixed_assembly(explode);
    color([0.08,0.08,0.08]) cage_assembly(a,explode);
    color("Goldenrod") input_assembly(a,explode);
    color("SteelBlue") wave_assembly(a,explode);
    color("Silver") nominal_bearings(a,explode);
    color("Ivory") roller_assembly(a,explode);
}
module motion_section(a=0,top=false) {
    color("Turquoise") difference() { circle(r=housing_radius); polygon(profile_points(top)); }
    color([0.08,0.08,0.08]) rotate(-a/roller_count) difference() {
        difference() { circle(r=cage_outer); circle(r=cage_inner); }
        for(i=[0:roller_count-1]) rotate(360*i/roller_count) translate([cage_inner-2,-(roller_diameter+roller_slot_clearance)/2]) square([cage_wall+4,roller_diameter+roller_slot_clearance]);
    }
    color("SteelBlue") translate(polar(eccentricity,a+(top?180:0))) difference() { circle(r=wave_radius); circle(r=13.5); }
    for(i=[0:roller_count-1]) color("Ivory") translate(roller_position(i,a,top)) difference() { circle(r=roller_radius); circle(d=roller_bore_diameter); }
}
module fit_coupons() {
    translate([0,0,0]) tube(36,32.5+bearing_seat_clearance,4);
    translate([65,0,0]) tube(18,13.5+bearing_seat_clearance,4);
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
    // Roller/wave tangency is checked independently against analytic circles.
}
