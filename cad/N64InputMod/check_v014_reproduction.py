import sys,json
from pathlib import Path
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A,Part
r=Path(__file__).resolve().parent
a=A.openDocument(str(r/'.v014-verified-baseline.FCStd'));b=A.openDocument(str(r/'N64InputMod.FCStd'))
checks={}
for obj in a.PrintParts.Group:
 actual=b.getObject(obj.Name).Shape
 err=obj.Shape.cut(actual).Volume+actual.cut(obj.Shape).Volume
 checks[obj.Name]=err
assert all(v<.005 for v in checks.values()),checks
extended=Part.Shape();extended.read(str(r.parent/'n64-input-ControllerPortMale.step'))
assert extended.isValid() and len(extended.Solids)==1
assert abs(extended.BoundBox.YLength-45.5)<.001
report={'revision':'v0.14','print_part_regeneration_difference_mm3':checks,'extended_source_STEP_valid':True,'extended_source_STEP_solids':len(extended.Solids),'extended_source_bounds':str(extended.BoundBox)}
(r/'reproduction-v0.14-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
