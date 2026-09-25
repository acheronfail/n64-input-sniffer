"""Check centred side fasteners and constrain v1.4 changes to their surroundings."""
from pathlib import Path
import json
import FreeCAD as A, Part
r=Path(__file__).resolve().parent
p=json.loads((r/'parameters.json').read_text())
d=A.openDocument(str(r/'Enclosure-v1.4.FCStd'))
old=A.openDocument(str(r/'Enclosure-v1.3.FCStd'))
V=A.Vector

def volume(shape):
 return 0.0 if shape.isNull() or not shape.Solids else shape.Volume

report={'revision':'v1.4','side_fasteners':[],'part_changes':{},'physical_fit_verified':False}
regions=[]
for x,y in p['closure_screw_xy'][-2:]:
 section=d.OuterContourLoft.Shape.common(Part.makeBox(.02,100,.02,V(x-.01,-60,-.01)))
 b=section.BoundBox
 midpoint=(b.YMin+b.YMax)/2
 assert abs(y-midpoint)<.05,(x,y,midpoint)
 assert abs(x)==79.5
 # Both shell through-holes must stay open; the captive nut is checked separately.
 bore=Part.makeCylinder(1.09,19,V(x,y,-16))
 assert volume(bore.common(d.LowerShell.Shape.fuse(d.UpperShell.Shape)))<.005
 head_material=Part.makeCylinder(1,.5,V(x,2,-14.9))
 assert volume(head_material.cut(d.LowerShell.Shape))<.005,'Old underside bolt hole remains open'
 report['side_fasteners'].append({'xy_mm':[x,y],'side_y_limits_mm':[b.YMin,b.YMax],'edge_midpoint_y_mm':midpoint,'midpoint_error_mm':abs(y-midpoint),'move_along_side_mm':2-y})
 for cy in [2,y]:regions.append(Part.makeCylinder(4.6,40,V(x,cy,-20)))
region=Part.makeCompound(regions)
assert region.isValid() and len(region.Solids)==4
# Upper-shell gap reinforcement is a separate authorised addition.
addition_region=region.fuse(d.InterPortGapFills.Shape) if p.get('inter_port_gap_fill') else region
for obj in d.PrintParts.Group:
 before=old.getObject(obj.Name).Shape;after=obj.Shape
 added=after.cut(before);removed=before.cut(after)
 # OCC can return a non-null empty compound for geometrically identical parts.
 outside=sum(volume(solid.cut(addition_region)) for solid in added.Solids)+sum(volume(solid.cut(region)) for solid in removed.Solids)
 assert outside<.005,(obj.Name,'unrelated change',outside)
 report['part_changes'][obj.Name]={'added_mm3':volume(added),'removed_mm3':volume(removed),'change_outside_authorised_regions_mm3':outside}
# Keep a continuous 1 mm wall around all male keeper screw pilots.
for i,x in enumerate(p['male_port_x'],1):
 y=p['nose_y']+p['port_x'][i-1]**2/p['curve_radius']-p['male_body_length']-4
 for sign in [-1,1]:
  sx=x+sign*p['male_keeper_screw_offset']
  wall=Part.makeCylinder(1.8,7.98,V(sx,y,2.81)).cut(Part.makeCylinder(.801,8,V(sx,y,2.8)))
  assert volume(wall.cut(d.LowerShell.Shape))<.005,(i,sign,'keeper pilot wall')
report['male_keeper_pilot_minimum_wall_mm']=1.0
for obj in d.Hardware.Group:
 if not hasattr(obj,'Shape'):continue
 before=old.getObject(obj.Name).Shape
 assert volume(obj.Shape.cut(before))+volume(before.cut(obj.Shape))<.005,obj.Name
(r/'side-closure-v1.4-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
