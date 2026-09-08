"""Geometric regression for the independent v0.15 connector retention."""
from pathlib import Path
import sys,json,itertools
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A,Part
r=Path(__file__).resolve().parent
old=A.openDocument(str(r/'revisions/v0.13/N64InputMod.FCStd'))
new=A.openDocument(str(r/'N64InputMod.FCStd'))
p=json.loads((r/'parameters.json').read_text());v=A.Vector
checks={};retention={}
def vol(s):return 0. if s.isNull() or not s.Solids else s.Volume
def difference(a,b):return vol(a.cut(b))+vol(b.cut(a))
for prefix in ['MalePort','FemalePort']:
 for i in range(1,5):
  name=prefix+str(i)
  checks[name+'_unchanged_mm3']=difference(old.getObject(name).Shape,new.getObject(name).Shape)
dy=p['rear_y']-json.loads((r/'revisions/v0.13/parameters.json').read_text())['rear_y']
for name in ['BoardKeeper','LightWindow','ESP32BoardEnvelope','ESP32ComponentKeepout','USBCEnvelope','BoardCradle','USBSeamTongue']:
 checks[name+'_translated_only_mm3']=difference(old.getObject(name).Shape.translated(v(0,dy,0)),new.getObject(name).Shape)
for i in range(1,5):
 keeper=new.getObject('FemalePortKeeper'+str(i)).Shape
 female=new.getObject('FemalePort'+str(i)).Shape
 for name,delta in [('lift',v(0,0,.5)),('forward',v(0,-.5,0)),('backward',v(0,.5,0))]:
  overlap=vol(female.translated(delta).common(new.LowerShell.Shape.fuse(keeper)))
  retention[f'female_{i}_{name}_blocked_mm3']=overlap
  assert overlap>.01,(i,name,overlap)
 expected=new.FemalePortKeeper1.Shape.translated(v(p['port_x'][i-1]-p['port_x'][0],0,0))
 checks[f'female_keeper_{i}_identical_mm3']=difference(expected,keeper)
for i in range(1,5):
 keeper=new.getObject('MalePortKeeper'+str(i)).Shape
 male=new.getObject('MalePort'+str(i)).Shape.fuse(new.getObject('MaleMatingProjection'+str(i)).Shape)
 for name,delta in [('lift',v(0,0,.5)),('forward',v(0,.6,0)),('backward',v(0,-.6,0))]:
  overlap=vol(male.translated(delta).common(new.LowerShell.Shape.fuse(keeper)))
  retention[f'male_{i}_{name}_blocked_mm3']=overlap
  assert overlap>.01,(i,name,overlap)
 # All eight keeper screws must be clear of the connector housing.
 for side in ['L','R']:
  screw=new.getObject('MaleKeeperScrew'+str(i)+side).Shape
  checks[f'male_{i}_screw_{side}_housing_overlap_mm3']=vol(screw.common(male))
 # Check the measured projection separately: the original housing datum stays put.
 tip=new.getObject('MaleMatingProjection'+str(i)).Shape.BoundBox
 assert abs(tip.XLength-16)<.001 and abs(tip.ZLength-12)<.001 and abs(tip.YLength-12)<.001
for prefix in ['Male','Female']:
 for i in range(1,5):
  for side in ['L','R']:
   screw=new.getObject(prefix+'KeeperScrew'+str(i)+side).Shape
   keeper=new.getObject(prefix+'PortKeeper'+str(i)).Shape
   checks[f'{prefix}_{i}_screw_{side}_lid_overlap_mm3']=vol(screw.common(new.UpperShell.Shape))
   checks[f'{prefix}_{i}_screw_{side}_keeper_overlap_mm3']=vol(screw.common(keeper))
fixed=[new.LowerShell.Shape]+[o.Shape for o in new.PrintParts.Group if o.Name not in ['LowerShell','UpperShell','LightWindow']]
checks['lid_lift_sweep_mm3']=max(vol(new.UpperShell.Shape.translated(v(0,0,z)).common(s)) for z in [0,.25,1,3,8,16,32] for s in fixed)
# Pairwise printable part collisions, including keepers against each other.
checks['print_part_pair_overlap_mm3']=max(vol(a.Shape.common(b.Shape)) for a,b in itertools.combinations(new.PrintParts.Group,2))
# Confirm the relocated USB remains accessible through the enlarged case.
face=new.USBCEnvelope.Shape.BoundBox.YMax
path=Part.makeBox(8.4,25,2.4,v(-4.2,face,9))
checks['USB_access_mm3']=sum(vol(path.common(o.Shape)) for o in new.PrintParts.Group)
assert all(x<.005 for x in checks.values()),checks
result={'revision':'v0.15','checks':checks,'retention_checks':retention,'physical_fit_verified':False,'console_scan_axial_clearance':'See console-retention-fit.json: extended mating envelopes checked separately under the explicitly revised scan registration; installed socket depth remains unverified.'}
(r/'independent-retention-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
