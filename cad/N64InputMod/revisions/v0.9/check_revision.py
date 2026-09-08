import sys,json
from pathlib import Path
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A
p=Path(__file__).resolve().parent
old=A.openDocument(str(p/'revisions/v0.1/N64InputMod.FCStd'))
new=A.openDocument(str(p/'N64InputMod.FCStd'))
a=old.FemaleFitCoupon.Shape;b=new.FemaleFitCoupon.Shape
r={'female_coupon_symmetric_difference_mm3':a.cut(b).Volume+b.cut(a).Volume,'male_loading_path_samples':[]}
for name in ['MalePort1','MalePort2','MalePort3','MalePort4']:
 s=new.getObject(name).Shape
 for dz in [0,.5,1,2,4,8,16,25]:
  v=s.translated(A.Vector(0,0,dz)).common(new.RearAlignmentGauge.Shape).Volume
  r['male_loading_path_samples'].append({'part':name,'lift_mm':dz,'lower_gauge_overlap_mm3':v})
r['pcb_keeper_overlap_mm3']=new.BoardKeeper.Shape.common(new.ESP32BoardEnvelope.Shape).Volume
r['component_keeper_overlap_mm3']=new.BoardKeeper.Shape.common(new.ESP32ComponentKeepout.Shape).Volume
r['usb_keeper_overlap_mm3']=new.BoardKeeper.Shape.common(new.USBCEnvelope.Shape).Volume
r['passed']=r['female_coupon_symmetric_difference_mm3']<.001 and max(v['lower_gauge_overlap_mm3'] for v in r['male_loading_path_samples'])<.005 and max(r[k] for k in ['pcb_keeper_overlap_mm3','component_keeper_overlap_mm3','usb_keeper_overlap_mm3'])<.005
(p/'revision-checks.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r,indent=2))
assert r['passed']
