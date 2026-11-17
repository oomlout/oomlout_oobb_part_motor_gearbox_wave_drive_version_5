// Reusable native geometry helpers.
function polar(r,a)=[r*cos(a),r*sin(a)];
function rotate_point(p,a)=[p[0]*cos(a)-p[1]*sin(a),p[0]*sin(a)+p[1]*cos(a)];
function profile_point(t)=let(
    s=sqrt(pow(pitch_radius,2)-pow(eccentricity*sin(cavity_count*t),2)),
    r=eccentricity*cos(cavity_count*t)+s,
    xi=atan2(eccentricity*cavity_count*sin(cavity_count*t),s),
    rr=roller_radius+profile_clearance)
    [r*cos(t)+rr*cos(t+xi),r*sin(t)+rr*sin(t+xi)];
function profile_points(upper=false)=[for(i=[0:cavity_count*profile_samples_per_cavity-1])
    rotate_point(profile_point(360*i/(cavity_count*profile_samples_per_cavity)),0)];
function roller_position(i,a,upper=false)=let(
    t=-a/roller_count+360*i/roller_count,
    rel=t-a-(upper?180:0),
    r=eccentricity*cos(rel)+sqrt(pow(pitch_radius,2)-pow(eccentricity*sin(rel),2))) polar(r,t);
module tube(ro,ri,h) { difference() { cylinder(r=ro,h=h); translate([0,0,-eps]) cylinder(r=ri,h=h+2*eps); } }
module screw_hole(size,h) { scale([1,1,h]) { if(size=="m2") oobb_hole_m2(); if(size=="m3") oobb_hole_m3(); if(size=="m6") oobb_hole_m6(); } }
module socket_recess(size,depth) {
    // OOBB socket head starts at the under-head plane and extends outward.
    scale([1,1,depth/(size=="m3"?3.2:2.2)]) {
        if(size=="m3") oobb_socket_m3(); else oobb_socket_m2();
    }
}
module at_mounts(points) { for(p=points) translate([p[0],p[1],0]) children(); }
module shaft_cut(h,fit=shaft_fit_clearance) {
    linear_extrude(h) intersection() {
        circle(r=input_shaft_diameter/2+fit);
        translate([-10,-10]) square([10+input_shaft_diameter/2-input_shaft_flat_depth+fit,20]);
    }
}
module rounded_rectangle_plate(size=[119,119,3],radius=5) {
    hull() for(x=[-1,1],y=[-1,1]) translate([x*(size[0]/2-radius),y*(size[1]/2-radius),0]) cylinder(r=radius,h=size[2]);
}
module grid_cuts(h) {
    // Actual OOBB grid centres: six units are centred on half-pitch offsets.
    for(i=[0:base_width-1],j=[0:base_height-1])
        let(x=(i-(base_width-1)/2)*oobb_grid_pitch,y=(j-(base_height-1)/2)*oobb_grid_pitch)
        if(base_hole_fits([x,y],3.25))
            translate([x,y,-eps]) screw_hole("m6",h+2*eps);
    // OOBE half-grid, omitting positions already occupied by the M6 grid.
    for(i=[0:2*(base_width-1)],j=[0:2*(base_height-1)])
        let(x=(i-(base_width-1))*oobb_grid_pitch/2,y=(j-(base_height-1))*oobb_grid_pitch/2)
        if((i%2!=0 || j%2!=0) && base_hole_fits([x,y],1.8))
            translate([x,y,-eps]) screw_hole("m3",h+2*eps);
}
function base_hole_fits(p,r)=norm(p)>housing_radius+r+mount_minimum_web &&
    min([for(i=[0:housing_screw_count-1]) distance_to_case_boss(p,housing_screw_angle+360*i/housing_screw_count)])>r+mount_minimum_web;
function distance_to_case_boss(p,a)=let(q=rotate_point(p,-a),
    dx=max(case_boss_inner_radius-q[0],0,q[0]-case_boss_outer_radius),
    dy=max(abs(q[1])-case_boss_radius,0)) norm([dx,dy]);
module wave_generator() {
    render(convexity=20) difference() {
        tube(wave_radius,12.6,wave_lower_depth);
        translate([0,0,wave_seat_z]) cylinder(r=13.5+bearing_seat_clearance,h=wave_lower_depth);
        at_mounts(wave_mounts) {
            translate([0,0,-eps]) screw_hole("m3",wave_lower_depth+2*eps);
            translate([0,0,-eps]) scale([1,1,(wave_nut_z+2.5+eps)/2.7]) oobb_nut_m3();
        }
    }
}
module wave_cap() {
    render(convexity=20) difference() {
        tube(wave_radius,12.6,wave_cap_depth);
        translate([0,0,-eps]) cylinder(r=13.5+bearing_seat_clearance,h=2.1+eps);
        at_mounts(wave_mounts) {
            translate([0,0,-eps]) screw_hole("m3",wave_cap_depth+2*eps);
            translate([0,0,wave_cap_depth]) oobb_countersunk_m3();
        }
    }
}
