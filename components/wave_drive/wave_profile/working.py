"""Rigid intermediate-roller ring profile. No flexspline and no stationary pins.

The equations are independently expressed in conventional x=cos/y=sin axes.
See references/mishin for Mishin Machine's original sine/cosine convention.
"""
import copy
import math


def define(**kwargs):
    parameters = {
        "roller_count": 12,
        "roller_radius": 3.5,
        "bank_phase_degrees": 0.0,
        "wave_radius": 23.25,
        "eccentricity": 0.75,
        "profile_clearance": 0.15,
        "profile_samples_per_cavity": 100,
    }
    parameters.update(copy.deepcopy(kwargs))
    return parameters


def roller_center(theta, **kwargs):
    c = define(**kwargs)
    n = c["roller_count"] + 1
    e = c["eccentricity"]
    a = c["wave_radius"] + c["roller_radius"]
    s = math.sqrt(a * a - (e * math.sin(n * theta)) ** 2)
    radial = e * math.cos(n * theta) + s
    return radial * math.cos(theta), radial * math.sin(theta)


def action(**kwargs):
    c = define(**kwargs)
    n = c["roller_count"] + 1
    e = c["eccentricity"]
    a = c["wave_radius"] + c["roller_radius"]
    points = []
    for i in range(n * c["profile_samples_per_cavity"]):
        theta = 2 * math.pi * i / (n * c["profile_samples_per_cavity"])
        s = math.sqrt(a * a - (e * math.sin(n * theta)) ** 2)
        xi = math.atan2(e * n * math.sin(n * theta), s)
        x, y = roller_center(theta, **c)
        radius = c["roller_radius"] + c["profile_clearance"]
        points.append([
            x + radius * math.cos(theta + xi),
            y + radius * math.sin(theta + xi),
        ])
    return points


def motion(input_angle, **kwargs):
    """Angles in degrees; the cage turns opposite the input at exactly 1/N."""
    c = define(**kwargs)
    alpha = math.radians(input_angle)
    bank_alpha = alpha+math.radians(c["bank_phase_degrees"])
    beta = -alpha / c["roller_count"]
    e = c["eccentricity"]
    a = c["wave_radius"] + c["roller_radius"]
    centers = []
    for i in range(c["roller_count"]):
        theta = beta + 2 * math.pi * i / c["roller_count"]
        relative = theta - bank_alpha
        radial = e * math.cos(relative) + math.sqrt(a*a - (e * math.sin(relative))**2)
        centers.append([radial * math.cos(theta), radial * math.sin(theta)])
    return {
        "output_angle": math.degrees(beta),
        "wave_center": [e * math.cos(bank_alpha), e * math.sin(bank_alpha)],
        "roller_centers": centers,
    }

