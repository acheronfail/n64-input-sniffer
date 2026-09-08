import sys,json
from pathlib import Path
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A,Part
p=Path(__file__).resolve().parent
old=A.openDocument(str(p/'revisions/v0.2/N64InputMod.FCStd'));new=A.openDocument(str(p/'N64InputMod.FCStd'))
def diff(a,b):return a.cut(b).Volume+b.cut(a).Volume
region=Part.makeBox(16,10,8,A.Vector(-8,-64,-10))
r={'keeper_difference_mm3':diff(old.BoardKeeper.Shape,new.BoardKeeper.Shape),'lower_shell_difference_outside_usb_mm3':diff(old.LowerShell.Shape.cut(region),new.LowerShell.Shape.cut(region)),'lower_shell_removed_mm3':old.LowerShell.Shape.cut(new.LowerShell.Shape).Volume,'unchanged_parts':{}}
for name in ['UpperShell','FemaleFitCoupon','RearAlignmentGauge','RearAlignmentGaugeUpper','LightWindow']:
 r['unchanged_parts'][name]=diff(old.getObject(name).Shape,new.getObject(name).Shape)
r['usb_housing_interference_mm3']=new.LowerShell.Shape.common(new.USBCEnvelope.Shape).Volume
r['passed']=max([r['keeper_difference_mm3'],r['lower_shell_difference_outside_usb_mm3'],r['lower_shell_removed_mm3'],r['usb_housing_interference_mm3']]+list(r['unchanged_parts'].values()))<.005
(p/'usb-revision-checks.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));assert r['passed']
