from pathlib import Path
import sys,json
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A
r=Path(__file__).resolve().parent;d=A.openDocument(str(r/'N64-Soldering-Jig-v1.FCStd'));v=A.Vector
report=json.loads((r/'validation.json').read_text())
for label,shape,cap in [('male',d.MaleHousing.Shape,d.MaleClamp.Shape),('female',d.FemaleHousing.Shape,d.FemaleClamp.Shape)]:
 for angle in [-5,5]:
  s=shape.copy();s.rotate(v(0,0,18),v(0,1,0),angle)
  overlap=s.common(d.JigBase.Shape.fuse(cap)).Volume
  assert overlap>.005,(label,angle,overlap)
  report['checks'][f'{label}_roll_{angle}_blocked_mm3']=overlap
for o in d.PrintParts.Group+d.Connectors.Group:assert o.Shape.isValid(),o.Name
(r/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('Rotation and all reference-solid validity checks pass.')
