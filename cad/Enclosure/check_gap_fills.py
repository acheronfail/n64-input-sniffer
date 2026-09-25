"""Verify filled collar slots without obstructing keeper removal or changing the outline."""
from pathlib import Path
import json
import FreeCAD as A, Part
r=Path(__file__).resolve().parent
p=json.loads((r/'parameters.json').read_text())
d=A.openDocument(str(r/'Enclosure-v1.4.FCStd'))
V=A.Vector

def volume(s):
 return 0 if s.isNull() or not s.Solids else s.Volume

assert p['inter_port_gap_fill']
checks={}
# Probe the finished ribs, including both formerly separate wall skins.
# Probe widths leave 0.01 mm inside the keeper-clearance boundaries.
for side in [-1,1]:
 for name,centre,width,start,length in [('male',side*50.02,.98,-9,19),('female',side*49.85,1.64,p['front_y']+.2,18.6)]:
  probe=Part.makeBox(width,length,12.7,V(centre-width/2,start,.18)).common(d.OuterContourLoft.Shape)
  assert volume(probe)>100,(name,side,'empty check region')
  missing=volume(probe.cut(d.UpperShell.Shape))
  assert missing<.005,(name,side,missing)
  checks[f'{name}_{side}_rib_missing_mm3']=missing
bridges=d.InterPortGapFills.Shape
checks['gap_fill_missing_mm3']=volume(bridges.cut(d.UpperShell.Shape))
checks['outside_enclosure_mm3']=volume(d.UpperShell.Shape.cut(d.OuterContourLoft.Shape))
checks['lower_shell_intersection_mm3']=volume(bridges.common(d.LowerShell.Shape))
for o in d.PrintParts.Group:
 if o.Name in ['UpperShell','LowerShell']:continue
 checks[o.Name+'_installation_obstruction_mm3']=max(volume(o.Shape.translated(V(0,0,z)).common(bridges)) for z in [0,.25,1,3,8,16,32])
assert all(v<.005 for v in checks.values()),checks
report={'revision':'v1.4','checks':checks,'filled_slots':4,'male_rib_nominal_width_mm':1.0,'female_rib_nominal_width_mm':1.66,'physical_fit_verified':False}
(r/'gap-fill-v1.4-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
