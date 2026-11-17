// Generated from installed OOBB v5. All primitives use overhang=True.

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
