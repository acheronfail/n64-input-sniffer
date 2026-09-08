from pathlib import Path
import sys,math,json
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A,Part
r=Path(__file__).parent;old=A.openDocument(str(r/'revisions/v0.6/N64InputMod.FCStd'));d=A.openDocument(str(r/'N64InputMod.FCStd'));V=A.Vector
shells=[d.LowerShell.Shape,d.UpperShell.Shape]
def vol(s):return 0 if s.isNull() or not s.Solids else s.Volume
def hexnut(x,y,z,af,h,along_y=False):
 rad=af/math.sqrt(3);a=math.pi/2 if along_y else 0
 pts=[V(x+rad*math.cos(a+k*math.pi/3),y+rad*math.sin(a+k*math.pi/3),z) for k in range(6)]
 return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,h))
def screw(x,y,z,diam,head_d,length,direction):
 h=(head_d-diam)/2
 head=Part.makeCone(head_d/2,diam/2,h,V(x,y,z),V(0,0,direction))
 shaft=Part.makeCylinder(diam/2,length-h,V(x,y,z+direction*h),V(0,0,direction))
 return head.fuse(shaft)
checks={};coords=[(-77,-39),(77,-39),(-19,-19),(19,-19),(-79,-18),(79,-18)]
for i,(x,y) in enumerate(coords):
 nut=hexnut(x,y,2,4,1.6,abs(x)==79)
 checks[f'closure_nut_{i}_collision']=sum(vol(nut.common(s)) for s in shells)
 fast=screw(x,y,-16,2,4,20,1)
 checks[f'closure_screw_{i}_collision']=sum(vol(fast.common(s)) for s in shells)
for i,x in enumerate([-63.7,-36,36,63.7]):
 y=7+x*x/1450-23
 for top in [17.2,16.8,16.4]:
  fast=screw(x,y,top,3,6,8,-1)
  checks[f'clamp_{i}_head_z{top}_collision']=vol(fast.common(d.UpperShell.Shape))
checks['keeper_changed']=vol(old.BoardKeeper.Shape.cut(d.BoardKeeper.Shape))+vol(d.BoardKeeper.Shape.cut(old.BoardKeeper.Shape))
checks['shell_overlap']=vol(shells[0].common(shells[1]))
(r/'embedded-fastener-clearance.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2));assert all(v<.005 for v in checks.values()),checks
