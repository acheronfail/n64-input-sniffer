"""Check complete nut walls, bearing surfaces, insertion and unchanged keepers."""
from pathlib import Path
import sys,json,math
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A,Part
r=Path(__file__).resolve().parent;p=json.loads((r/'parameters.json').read_text())
d=A.openDocument(str(r/'N64InputMod.FCStd'));old=A.openDocument(str(r/'revisions/v0.15/N64InputMod.FCStd'));V=A.Vector
checks={};nuts=[]
def hexagon(x,y,z,af,h,angle=0):
 rad=af/math.sqrt(3);pts=[V(x+rad*math.cos(angle+k*math.pi/3),y+rad*math.sin(angle+k*math.pi/3),z) for k in range(6)]
 return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,h))
for x,y in p['closure_screw_xy']:
 nz=p['closure_nut_pocket_z'];nh=p['closure_nut_pocket_height'];af=p['closure_nut_af'];angle=math.pi/2 if abs(x)==79 else 0
 cavity=hexagon(x,y,nz+.01,af,nh-.02,angle)
 # Continuous surrounding material at least 1.5 mm beyond every hex corner.
 wall=Part.makeCylinder(af/math.sqrt(3)+1.5,nh-.02,V(x,y,nz+.01)).cut(cavity)
 entry={'xy':[x,y],'minimum_checked_wall_mm':1.5,'missing_wall_mm3':wall.cut(d.UpperShell.Shape).Volume,'cavity_obstruction_mm3':cavity.common(d.UpperShell.Shape).Volume}
 for label,z in [('bearing',nz+nh+.01),('cap',nz-.8)]:
  seat=hexagon(x,y,z,af,.79,angle).cut(Part.makeCylinder(1.1,1,V(x,y,z-.1)))
  entry[label+'_missing_mm3']=seat.cut(d.UpperShell.Shape).Volume
 printed=d.UpperShell.Shape.common(Part.makeBox(300,200,30,V(-150,-100,16-13.96)))
 nominal_nut=hexagon(x,y,nz+nh-1.6,4.,1.6,angle)
 entry['insertion_sweep_obstruction_mm3']=max(nominal_nut.translated(V(0,0,z)).common(printed).Volume for z in [-8,-4,-2,-1,0])
 screw=Part.makeCylinder(1,20,V(x,y,-16))
 entry['screw_path_obstruction_mm3']=screw.common(d.LowerShell.Shape).Volume+screw.common(d.UpperShell.Shape).Volume
 assert all(value<.005 for key,value in entry.items() if key.endswith('_mm3')),entry
 nuts.append(entry)
for obj in old.PrintParts.Group:
 if obj.Name != 'BoardKeeper':continue
 new=d.getObject(obj.Name).Shape
 err=obj.Shape.cut(new).Volume+new.cut(obj.Shape).Volume
 checks[obj.Name+'_unchanged_mm3']=err
assert all(v<.005 for v in checks.values()),checks
report={'revision':'v0.16','nuts':nuts,'unchanged_parts':checks,'nut_proxy':{'across_flats_mm':4,'height_mm':1.6},'all_six_have_complete_walls_seats_and_caps':True}
(r/'nut-seats-v0.16-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
