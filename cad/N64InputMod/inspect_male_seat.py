import sys,json
from pathlib import Path
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A,Part
r=Path(__file__).parent
s=Part.Shape();s.read(str(r.parent/'n64-input-ControllerPortMale.step'));s.translate(A.Vector(120,0,0))
b=s.BoundBox
out={'bounds':[b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax],'faces':[]}
for f in s.Faces:
 b=f.BoundBox
 if b.YLength<.001 or b.ZLength<.001:
  out['faces'].append({'area':f.Area,'type':str(type(f.Surface)),'bounds':[b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax]})
print(json.dumps(out,indent=2))
