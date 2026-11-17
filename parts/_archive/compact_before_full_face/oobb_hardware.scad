module oobb_rounded_rectangle_edges(size, radius, radius_top, radius_bottom) {
      rt=radius_top; rb=radius_bottom; depth=size[2]; n=16;
      lower=rb==0 ? [[radius,0]] :
        [for(i=[0:n]) let(a=-90+90*i/n) [radius-rb+rb*cos(a),rb+rb*sin(a)]];
      upper=rt==0 ? [[radius,depth]] :
        [for(i=[0:n]) let(a=90*i/n) [radius-rt+rt*cos(a),depth-rt+rt*sin(a)]];
      hull() for(x=[-size[0]/2+radius,size[0]/2-radius])
        for(y=[-size[1]/2+radius,size[1]/2-radius])
          translate([x,y,0]) rotate_extrude()
            polygon(concat([[0,0]],lower,upper,[[0,depth]]));
    }
// Generated from installed OOBB v5. All primitives use overhang=True.

module oobb_motor_plate_body() {


difference() {
	union() {
		translate(v = [0, 0, 0]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						oobb_rounded_rectangle_edges(radius = 1.5, radius_bottom = 1.5, radius_top = 1.5, size = [89.0, 89.0, 4.0]);
					}
					union();
				}
			}
		}
	}
	union();
}

}

module oobb_hole_m2() {


difference() {
	union() {
		cylinder(h = 1, r = 1.35);
	}
	union();
}

}

module oobb_hole_m3() {


difference() {
	union() {
		cylinder(h = 1, r = 1.8);
	}
	union();
}

}

module oobb_hole_m6() {


difference() {
	union() {
		cylinder(h = 1, r = 3.25);
	}
	union();
}

}

module oobb_nut_m2() {


difference() {
	union() {
		translate(v = [0, 0, 0]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						linear_extrude(height = 2.2) {
							polygon(points = [[2.4234, 0.0], [1.2117000000000002, 2.0987259635312085], [-1.2116999999999996, 2.0987259635312085], [-2.4234, 2.967809053053696e-16], [-1.211700000000001, -2.098725963531208], [1.2116999999999984, -2.0987259635312094]]);
						}
						translate(v = [-1.25, -2.75, -0.3]) {
							cube(size = [2.5, 5.5, 0.3]);
						}
						translate(v = [-1.25, -1.25, -0.6]) {
							cube(size = [2.5, 2.5, 0.3]);
						}
						translate(v = [-1.25, -2.75, 2.2]) {
							cube(size = [2.5, 5.5, 0.3]);
						}
						translate(v = [-1.25, -1.25, 2.5]) {
							cube(size = [2.5, 2.5, 0.3]);
						}
					}
					union();
				}
			}
		}
	}
	union();
}

}

module oobb_socket_m2() {


difference() {
	union() {
		translate(v = [0, 0, 0]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						cylinder(h = 2.2, r = 2.1);
						translate(v = [-1.25, -2.75, -0.3]) {
							cube(size = [2.5, 5.5, 0.3]);
						}
						translate(v = [-1.25, -1.25, -0.6]) {
							cube(size = [2.5, 2.5, 0.3]);
						}
					}
					union();
				}
			}
		}
	}
	union();
}

}

module oobb_nut_m3() {


difference() {
	union() {
		translate(v = [0, 0, 0]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						linear_extrude(height = 2.7) {
							polygon(points = [[3.4619999999999997, 0.0], [1.7310000000000003, 2.9981799479017264], [-1.7309999999999992, 2.9981799479017264], [-3.4619999999999997, 4.2397272186481365e-16], [-1.7310000000000014, -2.998179947901726], [1.7309999999999977, -2.9981799479017277]]);
						}
						translate(v = [-1.75, -3.25, -0.3]) {
							cube(size = [3.5, 6.5, 0.3]);
						}
						translate(v = [-1.75, -1.75, -0.6]) {
							cube(size = [3.5, 3.5, 0.3]);
						}
						translate(v = [-1.75, -3.25, 2.7]) {
							cube(size = [3.5, 6.5, 0.3]);
						}
						translate(v = [-1.75, -1.75, 3.0]) {
							cube(size = [3.5, 3.5, 0.3]);
						}
					}
					union();
				}
			}
		}
	}
	union();
}

}

module oobb_socket_m3() {


difference() {
	union() {
		translate(v = [0, 0, 0]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						cylinder(h = 3.2, r = 3.0);
						translate(v = [-1.75, -3.25, -0.3]) {
							cube(size = [3.5, 6.5, 0.3]);
						}
						translate(v = [-1.75, -1.75, -0.6]) {
							cube(size = [3.5, 3.5, 0.3]);
						}
					}
					union();
				}
			}
		}
	}
	union();
}

}

module oobb_nut_m6() {


difference() {
	union() {
		translate(v = [0, 0, 0]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						linear_extrude(height = 5.2) {
							polygon(points = [[5.914249999999999, 0.0], [2.957125, 5.1218907443321156], [-2.9571249999999982, 5.1218907443321156], [-5.914249999999999, 7.242867331857232e-16], [-2.9571250000000022, -5.121890744332115], [2.9571249999999956, -5.121890744332118]]);
						}
						translate(v = [-2.875, -5.0, -0.3]) {
							cube(size = [5.75, 10, 0.3]);
						}
						translate(v = [-2.875, -2.875, -0.6]) {
							cube(size = [5.75, 5.75, 0.3]);
						}
						translate(v = [-2.875, -5.0, 5.2]) {
							cube(size = [5.75, 10, 0.3]);
						}
						translate(v = [-2.875, -2.875, 5.5]) {
							cube(size = [5.75, 5.75, 0.3]);
						}
					}
					union();
				}
			}
		}
	}
	union();
}

}
