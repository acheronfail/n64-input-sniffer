"""Generous male connector relief envelopes, inferred from physical fit photos."""
import FreeCAD as A, Part


def side_tab_reliefs(p, index):
    """Open vertical insertion pockets for the two aft side tabs; index is zero-based."""
    x = p['male_port_x'][index]
    y = p['nose_y'] + p['port_x'][index] ** 2 / p['curve_radius']
    inner = p['male_tab_relief_inner_x']
    outer = p['male_tab_relief_outer_x']
    bottom = p['male_tab_relief_bottom_z']
    start_y = y - p['male_body_length'] - 0.5
    top = p['male_keeper_top'] + p['connector_clearance']
    return Part.makeCompound([
        Part.makeBox(outer - inner, p['male_tab_relief_length'], top - bottom,
                     A.Vector(x + offset, start_y, bottom))
        for offset in (-outer, inner)
    ])


def front_keeper_relief(p, index):
    """Clear the 6.5 mm shoulder feature with 0.5 mm extra axial space."""
    x = p['male_port_x'][index]
    y = p['nose_y'] + p['port_x'][index] ** 2 / p['curve_radius']
    width = p['male_keeper_front_relief_width']
    return Part.makeBox(width, p['male_keeper_front_relief_length'] + 0.35,
                        p['male_keeper_front_relief_top_z'] + 1,
                        A.Vector(x - width / 2, y - p['male_keeper_front_relief_length'], -1))


def cradle_depth_relief(p, index):
    """Lower the rounded seat without moving the mating opening or pressure pad.

    The printed sample catches on the cradle. This is an empirical clearance
    correction, not a revised measurement of the connector body.
    """
    x = p['male_port_x'][index]
    y = p['nose_y'] + p['port_x'][index] ** 2 / p['curve_radius']
    c = p['connector_clearance']
    radius = p['male_body_diameter'] / 2 + c
    depth = p['male_cradle_extra_depth']
    length = p['male_body_length'] + 2 * c
    start_y = y - p['male_body_length'] - c
    rounded = Part.makeCylinder(radius, length, A.Vector(x, start_y, -depth), A.Vector(0, 1, 0))
    bridge = Part.makeBox(2 * radius, length, depth, A.Vector(x - radius, start_y, -depth))
    lower_half = Part.makeBox(2 * radius + 2, length, radius + depth + 1,
                              A.Vector(x - radius - 1, start_y, -radius - depth - 1))
    return rounded.fuse(bridge).common(lower_half).removeSplitter()
