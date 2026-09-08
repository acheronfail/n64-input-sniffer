from pathlib import Path
import sys,json
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A,Part
r=Path(__file__).resolve().parent;d=A.openDocument(str(r/'N64InputMod.FCStd'))
results=[]
for z in [0,.25,1,3,8,16,32]:
 lid=d.UpperShell.Shape.translated(A.Vector(0,0,z))
 for o in d.PrintParts.Group:
  if o.Name in ['UpperShell','LightWindow']:continue
  hit=lid.common(o.Shape)
  if hit.Volume>.005:
   results.append({'z':z,'part':o.Name,'volume':hit.Volume,'bounds':str(hit.BoundBox)})
print(json.dumps(results,indent=2))
(r/'lid-sweep-inspection.json').write_text(json.dumps(results,indent=2))
