from pathlib import Path
import sys,math,json
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A,Part
r=Path(__file__).parent;d=A.openDocument(str(r/'N64InputMod.FCStd'));V=A.Vector
# FreeCAD assembly Z decreases as the roof-down lid is printed upward.
# Before the two cap layers, completed printed heights are 5.32 and 13.96 mm.
def nut(x,y,z,af,h,angle=0):
 rad=af/math.sqrt(3);pts=[V(x+rad*math.cos(angle+k*math.pi/3),y+rad*math.sin(angle+k*math.pi/3),z) for k in range(6)]
 return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,h))
def volume(s):return 0 if s.isNull() or not s.Solids else s.Volume
checks={};specs=[]
for i,x in enumerate([-63.7,-36,36,63.7]):
 y=7+x*x/1450-23
 # Effective printed floor at Zprint=2.76 (assembly13.24), nut2.4 high.
 specs.append((f'M3_{i}',nut(x,y,10.84,5.5,2.4),5.32))
for i,(x,y) in enumerate([(-77,-39),(77,-39),(-19,-19),(19,-19),(-79,-18),(79,-18)]):
 # Effective printed floor at Zprint=12.04 (assembly3.96), nut1.6 high.
 specs.append((f'M2_{i}',nut(x,y,2.36,4,1.6,math.pi/2 if abs(x)==79 else 0),13.96))
for name,n,h in specs:
 lid=d.UpperShell.Shape
 checks[name+'_final_collision']=volume(n.common(lid))
 already_printed=lid.common(Part.makeBox(400,400,h,V(-200,-200,16-h)))
 checks[name+'_drop_in_collision']=max(volume(n.translated(V(0,0,-dist)).common(already_printed)) for dist in [0,.1,.3,.6,1,2,3,5,8])
 # The final cap must physically block the nut from exiting downward in assembly.
 assert volume(n.translated(V(0,0,-2)).common(lid))>.1,name
assert max(checks.values())<.005,checks
checks['M3_nut_below_completed_rim_mm']=.16;checks['M2_nut_below_completed_rim_mm']=.32
(r/'embedded-nut-validation.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
