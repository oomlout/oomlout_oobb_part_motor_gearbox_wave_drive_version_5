// Rigid intermediate-roller wave drive. All dimensions in mm.
// Geometry is native SCAD; only the small hardware cutters come from OOBB.
// Printed parts use their own bed-facing origin. assembly() places them.
$fn = circle_fragments;
eps = 0.01;
roller_count = reduction;
cavity_count = roller_count + 1;
roller_radius = roller_diameter / 2;
pitch_radius = wave_radius + roller_radius;
cage_inner = pitch_radius - cage_wall / 2;
cage_outer = pitch_radius + cage_wall / 2;
profile_min = wave_radius + roller_diameter - eccentricity;
profile_max = wave_radius + roller_diameter + eccentricity;
bearing_z = housing_flange_depth;
cage_base_z = bearing_z + 7 + bearing_axial_clearance;
window_z = cage_base_z + cage_plate_depth;
window_height = roller_length + 2*roller_end_clearance;
roller_z = window_z + roller_end_clearance;
cage_cap_z = window_z + window_height;
mirror_z = window_z + window_height/2;
assembly_height = 2*mirror_z;
shaft_length = 5*ceil((assembly_height+25)/5);
ring_z = bearing_z + 7;
ring_height = assembly_height - 2*ring_z;
wave_seat_z = (roller_length - 4 - bearing_axial_clearance)/2;
wave_cap_depth = wave_seat_z;
wave_bearing_z = roller_z + wave_seat_z + bearing_axial_clearance/2;
cam_z = roller_z + wave_seat_z - 1;
lower_spacer_length = cam_z - (bearing_z + 4 + bearing_axial_clearance + 1);
upper_spacer_z = cam_z + 5 + bearing_axial_clearance;
upper_spacer_length = assembly_height - (bearing_z + 5 + bearing_axial_clearance) - upper_spacer_z;
hub_height = 7 + bearing_axial_clearance;
retainer_height = retainer_depth;
mounts = [for(x=[-15,-7.5,7.5,15],y=[-15,-7.5,7.5,15]) if(abs(x)!=abs(y)) [x,y]];
wave_mounts = [for(a=[0:90:270]) [18*cos(a),18*sin(a)]];

assert(reduction >= 5 && floor(reduction) == reduction, "Integer reduction required");
assert(overhang, "OOBB hardware must have overhang enabled");
assert(bearing_output=="6810" && bearing_input=="6704" && bearing_wave=="6704", "This recipe fits 6810/6704");
assert(cage_inner-wave_radius-eccentricity >= 0.2, "Wave/cage collision");
assert(profile_min-cage_outer >= 0.2, "Ring/cage collision");
assert(roller_count % cage_screw_count == 0, "Cap screws must land between windows");
assert(wave_cap_depth >= 1.5, "Insufficient bearing retainer thickness");
assert(cage_wall >= 3.5, "Insufficient M2 pilot wall");
assert(profile_samples_per_cavity >= 40, "Undersampled contact profile");
assert(circle_fragments >= 96, "Insufficient bearing surface resolution");
assert(housing_screw_length >= assembly_height && housing_screw_length <= assembly_height+5, "Review housing screw length");
assert(bearing_z-retainer_depth+output_screw_length >= window_z-0.3 && bearing_z-retainer_depth+output_screw_length <= roller_z-0.1, "Review output screw engagement and protrusion");
assert(wave_screw_length >= roller_length-0.3 && wave_screw_length <= roller_length+0.1, "Review wave cap screw length");
assert(cage_screw_length-cage_plate_depth >= 3 && cage_screw_length-cage_plate_depth <= window_height-1, "Review cage pilot depth");

function polar(r,a) = [r*cos(a),r*sin(a)];
function profile_point(t) =
    let(s=sqrt(pow(pitch_radius,2)-pow(eccentricity*sin(cavity_count*t),2)),
        r=eccentricity*cos(cavity_count*t)+s,
        xi=atan2(eccentricity*cavity_count*sin(cavity_count*t),s),
        rr=roller_radius+profile_clearance)
    [r*cos(t)+rr*cos(t+xi),r*sin(t)+rr*sin(t+xi)];
function profile_points() = [for(i=[0:cavity_count*profile_samples_per_cavity-1])
    profile_point(360*i/(cavity_count*profile_samples_per_cavity))];
function roller_position(i,a) =
    let(t=-a/roller_count+360*i/roller_count,
        r=eccentricity*cos(t-a)+sqrt(pow(pitch_radius,2)-pow(eccentricity*sin(t-a),2)))
    polar(r,t);

module tube(ro,ri,h) {
    difference() {
        cylinder(r=ro,h=h);
        translate([0,0,-eps]) cylinder(r=ri,h=h+2*eps);
    }
}
module screw_hole(size,h) {
    scale([1,1,h]) {
        if(size=="m2") oobb_hole_m2();
        if(size=="m3") oobb_hole_m3();
        if(size=="m6") oobb_hole_m6();
    }
}
module countersink(size) {
    if(size=="m2") oobb_countersink_m2();
    if(size=="m3") oobb_countersink_m3();
}
module at_mounts(points) {
    for(p=points) translate([p[0],p[1],0]) children();
}
module case_mounts() {
    for(i=[0:housing_screw_count-1]) rotate([0,0,360*i/housing_screw_count])
        translate([housing_screw_pitch_radius,0,0]) children();
}
module cage_mounts() {
    for(i=[0:cage_screw_count-1]) rotate([0,0,180/roller_count+360*i/cage_screw_count])
        translate([pitch_radius,0,0]) children();
}
module shaft_cut(h,fit=shaft_fit_clearance) {
    // 5 mm D shaft, flat towards +X. Fit is radial; the flat gets the same allowance.
    linear_extrude(h) intersection() {
        circle(r=input_shaft_diameter/2+fit);
        translate([-10,-10]) square([10+input_shaft_diameter/2-input_shaft_flat_depth+fit,20]);
    }
}

module grid_cuts(h) {
    // OOBB full 15 mm M6 grid plus 7.5 mm M3 half-grid. Never double-drill a shared station.
    for(i=[-7:7],j=[-7:7])
        let(x=7.5*i,y=7.5*j,r=sqrt(x*x+y*y),full=(i%2==0 && j%2==0),envelope=full?5.95:3.35)
        if(r>housing_radius+envelope && max(abs(x),abs(y))+envelope<housing_flange_width/2)
            translate([x,y,-eps]) screw_hole(full?"m6":"m3",h+2*eps);
}

module housing(top=false) {
    render(convexity=20) difference() {
        union() {
            rounded_rectangle_plate(
                size=[housing_flange_width,housing_flange_width,housing_flange_depth],
                radius=housing_flange_corner_radius
            );
            cylinder(r=housing_radius,h=ring_z);
        }
        translate([0,0,-eps]) cylinder(r=31.5,h=ring_z+2*eps);
        translate([0,0,bearing_z]) cylinder(r=32.5+bearing_seat_clearance,h=7+eps);
        grid_cuts(housing_flange_depth);
        case_mounts() {
            translate([0,0,-eps]) screw_hole("m3",ring_z+2*eps);
            if(!top) oobb_nut_m3();
            if(top) rotate([180,0,0]) countersink("m3");
        }
    }
}

// Same four-cylinder hull as OOBB's rounded_rectangle component.
// Native parameters keep direct OpenSCAD editing live; centred XY, bottom at Z=0.
module rounded_rectangle_plate(size=[119,119,3],radius=1.5) {
    assert(radius>0 && 2*radius<min(size[0],size[1]), "Invalid plate corner radius");
    hull() {
        for(x=[-1,1],y=[-1,1])
            translate([x*(size[0]/2-radius),y*(size[1]/2-radius),0])
                cylinder(r=radius,h=size[2]);
    }
}

module fixed_ring() {
    render(convexity=20) difference() {
        cylinder(r=housing_radius,h=ring_height);
        translate([0,0,-eps]) linear_extrude(ring_height+2*eps) polygon(profile_points());
        case_mounts() translate([0,0,-eps]) screw_hole("m3",ring_height+2*eps);
    }
}

module output_hub() {
    render(convexity=20) difference() {
        cylinder(r=25-journal_clearance,h=hub_height);
        translate([0,0,-eps]) cylinder(r=12.6,h=hub_height+2*eps);
        translate([0,0,-eps]) cylinder(r=13.5+bearing_seat_clearance,h=4+bearing_axial_clearance+eps);
        at_mounts(mounts) translate([0,0,-eps]) screw_hole("m3",hub_height+2*eps);
        // Four unused full-grid M3 stations are available for an output attachment.
        for(x=[-15,15],y=[-15,15]) translate([x,y,-eps]) screw_hole("m3",hub_height+2*eps);
    }
}

module output_retainer() {
    render(convexity=20) difference() {
        tube(26.2,12.6,retainer_height);
        at_mounts(mounts) {
            translate([0,0,-eps]) screw_hole("m3",retainer_height+2*eps);
            rotate([180,0,0]) countersink("m3");
        }
        for(x=[-15,15],y=[-15,15]) translate([x,y,-eps]) screw_hole("m3",retainer_height+2*eps);
    }
}

module cage_windows(h) {
    for(i=[0:roller_count-1]) rotate([0,0,360*i/roller_count])
        translate([cage_inner-2,-(roller_diameter+roller_slot_clearance)/2,-eps])
            cube([cage_wall+4,roller_diameter+roller_slot_clearance,h+2*eps]);
}
module plate_holes() {
    at_mounts(mounts) {
        translate([0,0,-eps]) screw_hole("m3",cage_plate_depth+2*eps);
        // Open at the internal face, so nuts are installed before the wave generator.
        translate([0,0,cage_plate_depth-2.7]) oobb_nut_m3();
    }
    for(x=[-15,15],y=[-15,15]) translate([x,y,0]) {
        translate([0,0,-eps]) screw_hole("m3",cage_plate_depth+2*eps);
        translate([0,0,cage_plate_depth]) countersink("m3");
    }
}
module cage() {
    render(convexity=20) difference() {
        union() {
            tube(cage_outer,12.6,cage_plate_depth);
            translate([0,0,cage_plate_depth]) difference() {
                tube(cage_outer,cage_inner,window_height);
                cage_windows(window_height);
            }
        }
        plate_holes();
        cage_mounts() translate([0,0,2*cage_plate_depth+window_height-cage_screw_length-0.1])
            cylinder(d=cage_screw_pilot_diameter,h=cage_screw_length-cage_plate_depth+0.2);
    }
}
module cage_cap() {
    render(convexity=20) difference() {
        tube(cage_outer,12.6,cage_plate_depth);
        // This part is printed interior face down; nuts open on that face.
        at_mounts(mounts) {
            translate([0,0,-eps]) screw_hole("m3",cage_plate_depth+2*eps);
            oobb_nut_m3();
        }
        for(x=[-15,15],y=[-15,15]) translate([x,y,0]) {
            translate([0,0,-eps]) screw_hole("m3",cage_plate_depth+2*eps);
            rotate([180,0,0]) countersink("m3");
        }
        cage_mounts() {
            translate([0,0,-eps]) screw_hole("m2",cage_plate_depth+2*eps);
            translate([0,0,cage_plate_depth]) countersink("m2");
        }
    }
}

module wave_generator() {
    render(convexity=20) difference() {
        tube(wave_radius,12.6,roller_length);
        translate([0,0,wave_seat_z]) cylinder(r=13.5+bearing_seat_clearance,h=roller_length);
        // Recess makes the removable cap flush with the rolling cylinder ends.
        translate([0,0,roller_length-wave_cap_depth]) cylinder(r=22.15,h=wave_cap_depth+eps);
        at_mounts(wave_mounts) {
            translate([0,0,-eps]) screw_hole("m3",roller_length+2*eps);
            oobb_nut_m3();
        }
    }
}
module wave_cap() {
    render(convexity=20) difference() {
        tube(22,12.6,wave_cap_depth);
        at_mounts(wave_mounts) {
            translate([0,0,-eps]) screw_hole("m3",wave_cap_depth+2*eps);
            translate([0,0,wave_cap_depth]) countersink("m3");
        }
    }
}
module eccentric_cam() {
    render(convexity=20) difference() {
        union() {
            translate([eccentricity,0,0]) cylinder(r=11,h=1);
            translate([eccentricity,0,1]) cylinder(r=10-journal_clearance,h=4+bearing_axial_clearance);
        }
        translate([0,0,-eps]) shaft_cut(5+bearing_axial_clearance+2*eps);
    }
}
module input_journal() {
    render(convexity=20) difference() {
        union() {
            cylinder(r=10-journal_clearance,h=4+bearing_axial_clearance);
            translate([0,0,4+bearing_axial_clearance]) cylinder(r=11,h=1);
        }
        translate([0,0,-eps]) shaft_cut(5+bearing_axial_clearance+2*eps);
    }
}
module input_spacer(h,eccentric_end=false) {
    render(convexity=20) difference() {
        union() {
            if(eccentric_end) translate([eccentricity,0,0]) cylinder(r=11,h=1);
            translate([0,0,eccentric_end?1:0]) cylinder(r=7,h=h-(eccentric_end?1:0));
        }
        translate([0,0,-eps]) shaft_cut(h+2*eps);
    }
}
module input_collar() {
    render(convexity=20) difference() {
        union() {
            cylinder(r=18,h=3);
            translate([0,0,3]) cylinder(r=10.5,h=10);
        }
        translate([0,0,-eps]) shaft_cut(13+2*eps);
        translate([0,0,7]) rotate([0,90,0]) screw_hole("m3",12);
        translate([5,0,7]) rotate([0,90,0]) oobb_nut_m3();
        // Nut loads through the outside knob face, then stays behind a solid radial wall.
        translate([5,-3.35,-eps]) cube([2.7,6.7,7+eps]);
    }
}
module roller() { cylinder(d=roller_diameter,h=roller_length); }

module bearing(ro,ri,h) {
    color([0.68,0.70,0.73]) tube(ro,ri,h);
}
module upper_mirror(extra=0) {
    translate([0,0,assembly_height+extra]) mirror([0,0,1]) children();
}
module assembly(a=0,explode=0) {
    beta = -a/roller_count;
    wc = polar(eccentricity,a);
    color("SlateGray") housing(false);
    color("SlateGray") upper_mirror(6*explode) housing(true);
    color("LightSlateGray") translate([0,0,ring_z+3*explode]) fixed_ring();
    rotate([0,0,beta]) {
        color("DarkOrange") translate([0,0,cage_base_z+2*explode]) cage();
        color("DarkOrange") translate([0,0,cage_cap_z+4*explode]) cage_cap();
        color("Goldenrod") translate([0,0,bearing_z+explode]) output_hub();
        color("Goldenrod") upper_mirror(5*explode) translate([0,0,bearing_z]) output_hub();
        color("DarkOrange") translate([0,0,bearing_z-retainer_height]) output_retainer();
        color("DarkOrange") upper_mirror(6*explode) translate([0,0,bearing_z-retainer_height]) output_retainer();
    }
    translate([0,0,bearing_z+explode]) bearing(32.5,25,7);
    upper_mirror(5*explode) translate([0,0,bearing_z]) bearing(32.5,25,7);
    translate([0,0,bearing_z+bearing_axial_clearance/2+explode]) bearing(13.5,10,4);
    upper_mirror(5*explode) translate([0,0,bearing_z+bearing_axial_clearance/2]) bearing(13.5,10,4);
    color("SteelBlue") translate([wc[0],wc[1],roller_z+3*explode]) wave_generator();
    color("LightSkyBlue") translate([wc[0],wc[1],roller_z+roller_length-wave_cap_depth+4*explode]) wave_cap();
    translate([wc[0],wc[1],wave_bearing_z+3*explode]) bearing(13.5,10,4);
    rotate([0,0,a]) {
        color("MediumPurple") translate([0,0,cam_z+3*explode]) eccentric_cam();
        color("MediumPurple") translate([0,0,bearing_z+explode]) input_journal();
        color("MediumPurple") upper_mirror(5*explode) translate([0,0,bearing_z]) input_journal();
        color("Plum") translate([0,0,bearing_z+5+bearing_axial_clearance+2*explode]) input_spacer(lower_spacer_length,false);
        color("Plum") translate([0,0,upper_spacer_z+4*explode]) input_spacer(upper_spacer_length,true);
        color("MediumPurple") translate([0,0,bearing_z-13]) input_collar();
        color("MediumPurple") upper_mirror(6*explode) translate([0,0,bearing_z-13]) input_collar();
        color("Silver") translate([0,0,-12]) shaft_cut(shaft_length,0);
    }
    for(i=[0:roller_count-1]) let(p=roller_position(i,a))
        color("Ivory") translate([p[0],p[1],roller_z+3*explode]) roller();
}

module motion_section(a=0) {
    color("SlateGray") difference() { circle(r=housing_radius); polygon(profile_points()); }
    color("DarkOrange") rotate(-a/roller_count) difference() {
        difference() { circle(r=cage_outer); circle(r=cage_inner); }
        for(i=[0:roller_count-1]) rotate(360*i/roller_count)
            translate([cage_inner-2,-(roller_diameter+roller_slot_clearance)/2]) square([cage_wall+4,roller_diameter+roller_slot_clearance]);
    }
    color("SteelBlue") translate(polar(eccentricity,a)) difference() { circle(r=wave_radius); circle(r=13.5); }
    for(i=[0:roller_count-1]) color("Ivory") translate(roller_position(i,a)) circle(r=roller_radius);
}

module fit_coupons() {
    // Full-size seats and journals, not scaled miniatures. Labels sit outside contact surfaces.
    translate([0,0,0]) tube(36,32.5+bearing_seat_clearance,4);
    translate([65,0,0]) tube(18,13.5+bearing_seat_clearance,4);
    translate([110,0,0]) tube(25-journal_clearance,22,4);
    translate([150,0,0]) tube(10-journal_clearance,7,4);
    translate([0,55,0]) difference() {
        translate([-10,-10,0]) cube([20,20,5]);
        translate([0,0,-eps]) shaft_cut(5+2*eps);
    }
    translate([40,55,0]) difference() {
        translate([-12,-8,0]) cube([24,16,4]);
        translate([-8,-(roller_diameter+roller_slot_clearance)/2,-eps]) cube([16,roller_diameter+roller_slot_clearance,5]);
    }
    translate([70,55,0]) roller();
    translate([100,55,0]) difference() {
        translate([-6,-6,0]) cube([12,12,6]);
        oobb_nut_m3();
        translate([0,0,-eps]) screw_hole("m3",7);
    }
}

module collision_check(a=0) {
    // A small witness cube survives an empty collision result, enabling CLI STL checks.
    translate([70,0,0]) cube([1,1,1]);
    intersection() {
        translate([0,0,ring_z]) fixed_ring();
        union() {
            rotate([0,0,-a/roller_count]) {
                translate([0,0,cage_base_z]) cage();
                translate([0,0,cage_cap_z]) cage_cap();
            }
            for(i=[0:roller_count-1]) let(p=roller_position(i,a))
                translate([p[0],p[1],roller_z]) roller();
        }
    }
    intersection() {
        cage_assembly(a);
        union() {
            wave_assembly(a);
            input_assembly(a);
            for(i=[0:roller_count-1]) let(p=roller_position(i,a))
                translate([p[0],p[1],roller_z]) roller();
        }
    }
    intersection() {
        union() { housing(false); upper_mirror() housing(true); }
        union() { cage_assembly(a); input_assembly(a); wave_assembly(a); }
    }
    intersection() { wave_assembly(a); input_assembly(a); }
    intersection() {
        nominal_bearings(a);
        union() {
            housing(false);
            upper_mirror() housing(true);
            cage_assembly(a);
            input_assembly(a);
            wave_assembly(a);
        }
    }
}

// Uncoloured groups for exact boolean tests; transforms match assembly().
module cage_assembly(a=0) {
    rotate([0,0,-a/roller_count]) {
        translate([0,0,cage_base_z]) cage();
        translate([0,0,cage_cap_z]) cage_cap();
        translate([0,0,bearing_z]) output_hub();
        upper_mirror() translate([0,0,bearing_z]) output_hub();
        translate([0,0,bearing_z-retainer_height]) output_retainer();
        upper_mirror() translate([0,0,bearing_z-retainer_height]) output_retainer();
    }
}
module input_assembly(a=0) {
    rotate([0,0,a]) {
        translate([0,0,cam_z]) eccentric_cam();
        translate([0,0,bearing_z]) input_journal();
        upper_mirror() translate([0,0,bearing_z]) input_journal();
        translate([0,0,bearing_z+5+bearing_axial_clearance]) input_spacer(lower_spacer_length,false);
        translate([0,0,upper_spacer_z]) input_spacer(upper_spacer_length,true);
        translate([0,0,bearing_z-13]) input_collar();
        upper_mirror() translate([0,0,bearing_z-13]) input_collar();
        translate([0,0,-12]) shaft_cut(shaft_length,0);
    }
}
module wave_assembly(a=0) {
    p=polar(eccentricity,a);
    translate([p[0],p[1],roller_z]) wave_generator();
    translate([p[0],p[1],roller_z+roller_length-wave_cap_depth]) wave_cap();
}
module nominal_bearings(a=0) {
    translate([0,0,bearing_z]) tube(32.5,25,7);
    upper_mirror() translate([0,0,bearing_z]) tube(32.5,25,7);
    translate([0,0,bearing_z+bearing_axial_clearance/2]) tube(13.5,10,4);
    upper_mirror() translate([0,0,bearing_z+bearing_axial_clearance/2]) tube(13.5,10,4);
    p=polar(eccentricity,a);
    translate([p[0],p[1],wave_bearing_z]) tube(13.5,10,4);
}

