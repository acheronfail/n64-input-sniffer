"""Fill unused upper-shell slots between adjacent connector collars."""
import FreeCAD as A, Part


def inter_port_gap_fills(p):
    """Four solid bridges: male/female rows, on both sides of the PCB bay."""
    shapes=[]
    z=p['seam_gap']
    top=p['top_z']-p['wall']
    overlap=.05
    for a,b in [(0,1),(2,3)]:
        for row,half_width in [('male',13.6),('female',13.2)]:
            xs=p['male_port_x'] if row=='male' else p['port_x']
            left=xs[a]+half_width
            right=xs[b]-half_width
            assert 0<right-left<2, 'Only fill the narrow slots between paired seats'
            if row=='male':
                ys=[p['nose_y']+p['port_x'][i]**2/p['curve_radius'] for i in [a,b]]
                start=min(ys)-p['male_body_length']-1.5
                end=max(ys)-p['male_body_length']-1.5+p['male_collar_depth']
            else:
                start=p['front_y']
                end=start+19
            shapes.append(Part.makeBox(right-left+2*overlap,end-start,top-z,
                                      A.Vector(left-overlap,start,z)))
    return Part.makeCompound(shapes)
