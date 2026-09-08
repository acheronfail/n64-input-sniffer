import sys,json
from pathlib import Path
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A,Part
r=Path(__file__).resolve().parent;d=A.openDocument(str(r/'N64InputMod.FCStd'))
# Read-only candidate: extend the female collar bases down to the inside floor.
blocks=[Part.makeBox(26.4,19,3.6,A.Vector(x-13.2,-62,-13.6)) for x in [-63.7,-36,36,63.7]]
fill=blocks[0].multiFuse(blocks[1:]).common(d.OuterContourLoft.Shape).cut(d.LowerShell.Shape)
result={'female_base_added_volume_mm3':fill.Volume,'collisions':{}}
for o in d.Hardware.Group+[d.BoardKeeper,d.UpperShell]:
 if hasattr(o,'Shape'):
  vol=fill.common(o.Shape).Volume
  if vol>.005:result['collisions'][o.Name]=vol
assert not result['collisions'],result
(r/'support-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
