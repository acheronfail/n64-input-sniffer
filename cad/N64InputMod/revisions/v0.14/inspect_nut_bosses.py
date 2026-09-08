from pathlib import Path
import sys,json,math
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A,Part
r=Path(__file__).resolve().parent;d=A.openDocument(str(r/'N64InputMod.FCStd'));V=A.Vector
current=[(-77,-49),(77,-49),(-19,-19),(19,-19),(-79,-18),(79,-18)]
proposed=[(-18,-60),(18,-60),(-18,-19),(18,-19),(-78,-38.5),(78,-38.5)]
keepers=[o.Shape for o in d.PrintParts.Group if o.Name.startswith(('MalePortKeeper','FemalePortKeeper'))]
hardware=[o.Shape for o in d.Hardware.Group if not 'Screw' in o.Name]
report={'existing':[],'proposed':[]}
for x,y in current:
 # A full 4 mm radius outside the hex guarantees at least 1.5 mm of nut wall.
 nr=4.3/math.sqrt(3);angle=math.pi/2 if abs(x)==79 else 0
 pts=[V(x+nr*math.cos(angle+k*math.pi/3),y+nr*math.sin(angle+k*math.pi/3),2.01) for k in range(6)]
 nut=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,1.98))
 wall=Part.makeCylinder(4,1.98,V(x,y,2.01)).cut(nut)
 report['existing'].append({'xy':[x,y],'missing_wall_mm3':wall.cut(d.UpperShell.Shape).Volume})
for x,y in proposed:
 post=Part.makeCylinder(4.3,29.6,V(x,y,-13.6))
 nut_ring=Part.makeCylinder(4,2.2,V(x,y,1.9))
 footprint=[]
 for k in keepers:
  b=k.BoundBox;c=.22
  footprint.append(Part.makeBox(b.XLength+2*c,b.YLength+2*c,13,V(b.XMin-c,b.YMin-c,.16)))
 report['proposed'].append({'xy':[x,y],'post_hardware_overlap_mm3':sum(post.common(h).Volume for h in hardware),'post_keeper_sweep_overlap_mm3':sum(post.common(s).Volume for s in footprint),'nut_wall_outside_case_mm3':nut_ring.cut(d.OuterContourLoft.Shape).Volume})
print(json.dumps(report,indent=2));(r/'nut-boss-inspection.json').write_text(json.dumps(report,indent=2))
