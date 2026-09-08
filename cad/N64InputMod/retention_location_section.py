import sys,json
from pathlib import Path
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A
r=Path(__file__).resolve().parent
d=A.openDocument(str(r/'N64InputMod.FCStd'))
out={}
for name in ['MalePort3','LowerShell','UpperShell']:
 s=d.getObject(name).Shape
 out[name]=[[[p.y,p.z] for p in w.discretize(Deflection=.025)] for w in s.slice(A.Vector(1,0,0),36)]
(r/'retention-location-section.json').write_text(json.dumps(out))
