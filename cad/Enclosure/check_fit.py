"""Check current female passages, male projection orientation and keeper clearance."""
from pathlib import Path
import sys,json
import FreeCAD as A,Part
r=Path(__file__).resolve().parent;p=json.loads((r/'parameters.json').read_text());V=A.Vector
new=A.openDocument(str(r/'Enclosure-v1.1.FCStd'))
def volume(s):return 0 if s.isNull() or not s.Solids else s.Volume
def diff(a,b):return volume(a.cut(b))+volume(b.cut(a))
checks={};male=[]
for i,x in enumerate(p['port_x'],1):
 passage=Part.makeBox(12.78,11.5,9.98,V(x-6.39,p['front_y']+16,-4.99))
 checks[f'female_{i}_terminal_passage_obstruction_mm3']=volume(passage.common(new.LowerShell.Shape))
 # Check that the passage reaches the full rear face of both supports. Check that the pilot walls stay intact.
 for side in [-1,1]:
  sx=x+side*p['female_keeper_screw_offset'];sy=p['front_y']+p['female_keeper_screw_y_offset']
  wall=Part.makeCylinder(2.3,7,V(sx,sy,3)).cut(Part.makeCylinder(.8,7,V(sx,sy,3)))
  checks[f'female_{i}_{side}_pilot_wall_missing_mm3']=volume(wall.cut(new.LowerShell.Shape))
for i,x in enumerate(p['male_port_x'],1):
 tip=new.getObject(f'MaleMatingProjection{i}').Shape
 assert tip.isValid() and len(tip.Solids)==1
 y=p['nose_y']+p['port_x'][i-1]**2/p['curve_radius']
 assert abs(tip.optimalBoundingBox().ZMin+4)<.001 and abs(tip.optimalBoundingBox().ZMax-8)<.001
 housing=new.getObject(f'MalePort{i}').Shape;keeper=new.getObject(f'MalePortKeeper{i}').Shape
 checks[f'male_{i}_keeper_seating_sweep_mm3']=max(volume(keeper.translated(V(0,0,z)).common(housing.fuse(tip))) for z in [0,.1,.25,.5,1,2,4,8,16])
 # Continuous remaining roof directly over the rounded lip: 1.1 mm nominal.
 roof=Part.makeBox(1,2,1.08,V(x-.5,y-4,11.71))
 checks[f'male_{i}_lip_roof_missing_mm3']=volume(roof.cut(keeper))
 male.append({'port':i,'lip_clearance_mm':p['male_keeper_lip_clearance'],'roof_checked_mm':1.08})
assert all(v<.005 for v in checks.values()),checks
# The closest paired connector tails are at the two center ports on the curved face.
gaps=[new.getObject(f'MalePort{i}').Shape.distToShape(new.getObject(f'FemalePort{i}').Shape)[0] for i in range(1,5)]
assert abs(min(gaps)-p['minimum_wire_gap'])<.02,gaps
# Keep a slot for wires between the opposing screw towers at every port.
tower_gaps=[new.getObject(f'MaleKeeperPosts{i}').Shape.distToShape(new.getObject(f'FemaleKeeperPosts{i}').Shape)[0] for i in range(1,5)]
assert min(tower_gaps)>=p['minimum_keeper_tower_gap']-.001,tower_gaps
window_centre=new.LightWindow.Shape.BoundBox.Center
assert abs(window_centre.x)<.001
assert abs(window_centre.y-(p['rear_y']-14-p['led_window_inward_shift']-p['pcb_console_inset']))<.001
report={'revision':'v1.1','checks':checks,'female_terminal_passage_width_mm':12.8,'male_lip_relief':male,'window_shift_toward_centre_mm':p['led_window_inward_shift'],'physical_fit_verified':False,'connector_gaps_mm':gaps,'keeper_tower_gaps_mm':tower_gaps,'window_centre_y_mm':window_centre.y}
(r/'fit-v1.1-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
