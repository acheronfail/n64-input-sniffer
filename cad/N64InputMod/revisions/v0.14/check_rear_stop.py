from pathlib import Path
import sys,json
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A,Part
r=Path(__file__).parent;old=A.openDocument(str(r/'revisions/v0.8/N64InputMod.FCStd'));new=A.openDocument(str(r/'N64InputMod.FCStd'));V=A.Vector
box=lambda x,y,z,dx,dy,dz:Part.makeBox(dx,dy,dz,V(x,y,z))
def vol(s):return 0 if s.isNull() or not s.Solids else s.Volume
def changed(a,b):return vol(a.cut(b))+vol(b.cut(a))
checks={}
for o in new.PrintParts.Group:
 if o.Name!='LowerShell':checks[o.Name+'_changed_mm3']=changed(old.getObject(o.Name).Shape,o.Shape)
for name in ['FemaleFitCoupon','RearAlignmentGauge','RearAlignmentGaugeUpper']:
 checks[name+'_changed_mm3']=changed(old.getObject(name).Shape,new.getObject(name).Shape)
region=box(-11.51,-36.29,-13.61,23.02,2.42,21.62)
a=old.LowerShell.Shape;b=new.LowerShell.Shape
checks['lower_change_outside_rear_stop_mm3']=vol(a.cut(b).cut(region))+vol(b.cut(a).cut(region))
assert max(checks.values())<.005,checks
probe=box(-.5,-37,7.2,1,5,.2)
a=a.common(probe);b=b.common(probe)
checks['rear_stop_shift_mm']=b.BoundBox.YMin-a.BoundBox.YMin
checks['rear_stop_thickness_mm']=b.BoundBox.YLength
assert abs(checks['rear_stop_shift_mm']-.8)<.0001 and abs(checks['rear_stop_thickness_mm']-1.6)<.0001
(r/'rear-stop-validation.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
