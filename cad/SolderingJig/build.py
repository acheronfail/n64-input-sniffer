"""Build the one-pair soldering jig, independent of the enclosure. Units: mm."""
from pathlib import Path
import sys,json,itertools
import FreeCAD as A,Part,Mesh
r=Path(__file__).resolve().parent;V=A.Vector
# Move the female station inward. Keep its seat, clamp, and access aligned.
WIRE_GAP=18.1
FEMALE_SHIFT=28.0-WIRE_GAP
d=A.newDocument('N64SolderingJig')
parts=d.addObject('App::DocumentObjectGroup','PrintParts');refs=d.addObject('App::DocumentObjectGroup','Connectors')
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def union(ss):return ss[0].multiFuse(ss[1:]).removeSplitter()
def clear(s,c=.22):return union([s.translated(V(*v)) for v in [(0,0,0),(c,0,0),(-c,0,0),(0,c,0),(0,-c,0),(0,0,c),(0,0,-c)]])
def feature(name,s,group):
 o=d.addObject('Part::Feature',name);o.Shape=s;group.addObject(o);return o
def vol(s):return 0 if s.isNull() or not s.Solids else s.Volume
male=Part.Shape();male.read(str(r.parent/'n64-input-ControllerPortMale-housing.step'));male.translate(V(120,45,18))
female=Part.Shape();female.read(str(r.parent/'n64-input-ControllerPortFemale.step'));female.translate(V(-110,-20+FEMALE_SHIFT,18))
# The male black projection faces flat side down. The housing faces flat side up.
tip=Part.makeCylinder(8,12,V(0,45,18),V(0,1,0)).common(box(-9,45,10,18,12,12))
tip.rotate(V(0,45,18),V(0,1,0),180)
assert tip.isValid()
feature('MaleHousing',male,refs);feature('MaleMatingPortion',tip,refs);feature('FemaleHousing',female,refs)
# Rounded 50 x (90 - FEMALE_SHIFT) mm base, 3 mm thick, with an open soldering/wiring well.
base=union([box(-21,-39+FEMALE_SHIFT,0,42,90-FEMALE_SHIFT,3),box(-25,-35+FEMALE_SHIFT,0,50,82-FEMALE_SHIFT,3)]+[Part.makeCylinder(4,3,V(x,y,0)) for x in [-21,21] for y in [-35+FEMALE_SHIFT,47]])
base=base.cut(box(-13,-16+FEMALE_SHIFT,-1,26,WIRE_GAP,5))
# Keyed lower seats: the male front face, male rear shoulder, and female flange prevent axial movement.
ms=box(-14,14,3,28,33,15).cut(clear(male)).cut(clear(tip,.35))
fs=box(-13,-33+FEMALE_SHIFT,3,26,15.1,15).cut(clear(female))
# Preserve the full rear terminal extrusion/prong width through the female seat.
fs=fs.cut(box(-6.4,-18.5+FEMALE_SHIFT,3,12.8,5,30))
base=base.fuse(ms).fuse(fs)
caps=[];screwrefs=[]
for name,shape,cy,top,n in [('MaleClamp',male,28,29,1),('FemaleClamp',female,-26+FEMALE_SHIFT,31,2)]:
 # Central housing bands avoid the male curved lip. Contour keys resist rotation.
 cap=box(-14,cy-5,18,28,10,top-18)
 seat=top-3
 for sx in [-18,18]:
  cap=cap.fuse(box(sx-4 if sx<0 else 14,cy-5,seat,8,10,3))
  post=box(sx-4,cy-5,3,8,10,seat-3)
  post=post.cut(Part.makeCylinder(.8,5.5,V(sx,cy,seat-5.5)))
  base=base.fuse(post)
  cap=cap.cut(Part.makeCylinder(1.1,4,V(sx,cy,seat-.5)))
  cap=cap.cut(Part.makeCone(2.1,1.1,1,V(sx,cy,top),V(0,0,-1)))
  screw=Part.makeCylinder(1,7,V(sx,cy,top-8)).fuse(Part.makeCone(1,2,1,V(sx,cy,top-1)))
  screwrefs.append(feature(name+('LeftScrew' if sx<0 else 'RightScrew'),screw,refs))
 cap=cap.cut(clear(shape)).removeSplitter()
 for j in range(n):cap=cap.cut(Part.makeCylinder(.6,.5,V((j-(n-1)/2)*2.5,cy,top-.4)))
 caps.append(feature(name,cap.removeSplitter(),parts))
# Optional holes for screws to attach the jig. Keep broad side rails for a bench clamp.
for x in [-20,20]:
 for y in [-35+FEMALE_SHIFT,47]:base=base.cut(Part.makeCylinder(2.2,4,V(x,y,-.5)))
base=base.removeSplitter();bo=feature('JigBase',base,parts)
report={'revision':'v1.1','footprint_mm':[50,90-FEMALE_SHIFT],'wire_gap_mm':WIRE_GAP,'connector_axis_height_mm':18,'female_terminal_passage_mm':12.8,'hardware':'Four 2 mm x 8 mm countersunk screws suitable for plastic; no nuts or print pauses','parts':{},'checks':{}}
for o in parts.Group:
 assert o.Shape.isValid() and len(o.Shape.Solids)==1,o.Name
 report['parts'][o.Name]={'volume_mm3':o.Shape.Volume,'valid':True,'solids':1}
for a,b in itertools.combinations(list(parts.Group)+[d.MaleHousing,d.MaleMatingPortion,d.FemaleHousing],2):
 overlap=vol(a.Shape.common(b.Shape));assert overlap<.005,(a.Name,b.Name,overlap)
report['checks']['no_assembled_part_collisions']=True
measured_gap=male.distToShape(female)[0]
assert abs(measured_gap-WIRE_GAP)<.001,measured_gap
report['checks']['connector_gap_mm']=measured_gap
for sh,cap,label in [(male,caps[0].Shape,'male'),(female,caps[1].Shape,'female')]:
 fixture=base.fuse(cap)
 movements={}
 for axis in [V(.6,0,0),V(-.6,0,0),V(0,.6,0),V(0,-.6,0),V(0,0,.6),V(0,0,-.6)]:
  overlap=vol(sh.translated(axis).common(fixture));assert overlap>.005,(label,axis,overlap);movements[str(axis)]=overlap
 report['checks'][label+'_translation_blocked_mm3']=movements
 assert max(vol(cap.translated(V(0,0,z)).common(sh)) for z in [0,.5,1,3,6,12,20])<.005
report['checks']['clamps_can_be_lowered_vertically']=True
# Clear female prong corridor and both soldering approaches, excluding connectors.
paths=[box(-6.39,-18.49+FEMALE_SHIFT,12,12.78,4.4,13),box(-7,0,10,14,11.4,18)]
for i,path in enumerate(paths):
 overlap=sum(vol(path.common(o.Shape)) for o in parts.Group);assert overlap<.005,(i,overlap)
report['checks']['terminal_approaches_clear']=True
for screw in screwrefs:
 for sh in [male,female,tip]+[o.Shape for o in caps]:assert vol(screw.Shape.common(sh))<.005
report['checks']['screw_heads_and_housings_clear']=True
# Root STL files already have their print orientation: base upright, clamp flat top on the bed.
for o in parts.Group:
 s=o.Shape.copy()
 if o!=bo:s.rotate(V(0,0,0),V(1,0,0),180)
 b=s.optimalBoundingBox();s.translate(V(-(b.XMin+b.XMax)/2,-(b.YMin+b.YMax)/2,-b.ZMin))
 Mesh.Mesh(s.tessellate(.05)).write(str(r/(o.Name+'.stl')))
Part.export(parts.Group,str(r/'N64-Soldering-Jig-v1.1.step'))
d.recompute();d.saveAs(str(r/'N64-Soldering-Jig-v1.1.FCStd'))
(r/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
