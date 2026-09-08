"""Check the local seam change against the accepted v0.3 geometry."""
from pathlib import Path
import sys,json
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A,Part
r=Path(__file__).parent
old=A.openDocument(str(r/'revisions/v0.3/N64InputMod.FCStd'))
new=A.openDocument(str(r/'N64InputMod.FCStd'))
box=lambda x,y,z,dx,dy,dz:Part.makeBox(dx,dy,dz,A.Vector(x,y,z))
region=box(-9.01,-70,-5.41,18.02,11.11,6.5)
def outside(a,b):
 s=a.cut(b)
 return 0 if s.isNull() or not s.Solids else s.cut(region).Volume
result={}
for name in ['LowerShell','UpperShell']:
 a=old.getObject(name).Shape;b=new.getObject(name).Shape
 result[name+'_change_outside_seam_mm3']=outside(a,b)+outside(b,a)
for name in ['BoardKeeper','FemaleFitCoupon','RearAlignmentGauge','RearAlignmentGaugeUpper','LightWindow']:
 a=old.getObject(name).Shape;b=new.getObject(name).Shape
 result[name+'_changed_mm3']=a.cut(b).Volume+b.cut(a).Volume
result['lower_notch_open_mm3']=new.LowerShell.Shape.common(box(-4.29,-63,-5.4,8.58,4,24)).Volume
result['upper_notch_open_mm3']=new.UpperShell.Shape.common(box(-4.29,-63,-20,8.58,4,14.76)).Volume
result['assembly_sweep_overlap_mm3']=max(new.UpperShell.Shape.translated(A.Vector(0,0,z)).common(new.LowerShell.Shape).Volume for z in [0,.2,.5,1,2,4,6,10,20])
assert all(v<.005 for v in result.values()),result
(r/'split-usb-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
