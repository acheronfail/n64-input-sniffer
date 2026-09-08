"""Verify v0.5 preserves fit features and confines changes to support improvements."""
from pathlib import Path
import sys,json
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A,Part
r=Path(__file__).parent;old=A.openDocument(str(r/'revisions/v0.4/N64InputMod.FCStd'));new=A.openDocument(str(r/'N64InputMod.FCStd'))
V=A.Vector
box=lambda x,y,z,dx,dy,dz:Part.makeBox(dx,dy,dz,V(x,y,z))
def volume(s):return 0 if s.isNull() or not s.Solids else s.Volume
def diff(a,b):return a.cut(b)
def intersection(s,t):return 0 if volume(s)<1e-8 else volume(s.common(t))
def outside(s,region):return 0 if volume(s)<1e-8 else volume(s.cut(region))
result={}
for name in ['BoardKeeper','LightWindow','RearAlignmentGauge','RearAlignmentGaugeUpper']:
 a=old.getObject(name).Shape;b=new.getObject(name).Shape;result[name+'_changed_mm3']=volume(diff(a,b))+volume(diff(b,a))
loadd=diff(new.LowerShell.Shape,old.LowerShell.Shape)
hiadd=diff(new.UpperShell.Shape,old.UpperShell.Shape)
result['lower_removed_mm3']=volume(diff(old.LowerShell.Shape,new.LowerShell.Shape))
result['upper_removed_outside_LED_mm3']=outside(diff(old.UpperShell.Shape,new.UpperShell.Shape),box(-9.41,-57.41,12.89,18.82,18.82,.92))
for name in ['LowerShell','UpperShell']:
 a=old.getObject(name).Shape;b=new.getObject(name).Shape
 region=box(-10,-65,-9,20,8,10)
 result[name+'_USB_region_changed_mm3']=intersection(a.cut(b),region)+intersection(b.cut(a),region)
for x in [-79,79]:
 region=box(x-3.01,-52.01,-4,6.02,6.02,7)
 for name in ['LowerShell','UpperShell']:
  a=old.getObject(name).Shape.common(region);b=new.getObject(name).Shape.common(region)
  result[name+str(x)+'_alignment_fit_changed_mm3']=volume(a.cut(b))+volume(b.cut(a))
for o in new.Hardware.Group:
 if o.Name.startswith(('MalePort','FemalePort')):
  expanded=o.Shape.multiFuse([o.Shape.translated(V(*v)) for v in [(.22,0,0),(-.22,0,0),(0,.22,0),(0,-.22,0),(0,0,.22),(0,0,-.22)]])
  result[o.Name+'_added_material_in_clearance_mm3']=volume(loadd.common(expanded))+volume(hiadd.common(expanded))
assert all(v<.005 for v in result.values()),result
result['added_lower_volume_mm3']=volume(loadd);result['added_upper_volume_mm3']=volume(hiadd)
(r/'support-revision-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
