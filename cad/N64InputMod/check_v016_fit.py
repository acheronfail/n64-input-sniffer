"""Regression checks for the three physical-fit corrections in v0.16."""
from pathlib import Path
import sys,json
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A,Part
r=Path(__file__).resolve().parent;p=json.loads((r/'parameters.json').read_text());V=A.Vector
new=A.openDocument(str(r/'N64InputMod.FCStd'));old=A.openDocument(str(r/'revisions/v0.15/N64InputMod.FCStd'))
def volume(s):return 0 if s.isNull() or not s.Solids else s.Volume
def diff(a,b):return volume(a.cut(b))+volume(b.cut(a))
checks={};male=[]
for i,x in enumerate(p['port_x'],1):
 passage=Part.makeBox(12.78,11.5,9.98,V(x-6.39,p['front_y']+16,-4.99))
 checks[f'female_{i}_terminal_passage_obstruction_mm3']=volume(passage.common(new.LowerShell.Shape))
 # Verify passage reaches the full rear face of both supports and pilot walls stay intact.
 for side in [-1,1]:
  sx=x+side*p['female_keeper_screw_offset'];sy=p['front_y']+22
  wall=Part.makeCylinder(2.3,7,V(sx,sy,3)).cut(Part.makeCylinder(.8,7,V(sx,sy,3)))
  checks[f'female_{i}_{side}_pilot_wall_missing_mm3']=volume(wall.cut(new.LowerShell.Shape))
for i,x in enumerate(p['male_port_x'],1):
 tip=new.getObject(f'MaleMatingProjection{i}').Shape
 assert tip.isValid() and len(tip.Solids)==1
 expected=old.getObject(f'MaleMatingProjection{i}').Shape.copy()
 y=p['nose_y']+p['port_x'][i-1]**2/p['curve_radius']
 expected.rotate(V(x,y,0),V(0,1,0),180)
 checks[f'male_{i}_tip_flip_error_mm3']=diff(tip,expected)
 assert abs(tip.optimalBoundingBox().ZMin+4)<.001 and abs(tip.optimalBoundingBox().ZMax-8)<.001
 # Housing saddle behind the mating projection stays exactly as printed in v0.15.
 seat=Part.makeBox(26.6,33.0,14,V(x-13.3,y-33.3,-14))
 checks[f'male_{i}_base_housing_seat_change_mm3']=diff(new.LowerShell.Shape.common(seat),old.LowerShell.Shape.common(seat))
 housing=new.getObject(f'MalePort{i}').Shape;keeper=new.getObject(f'MalePortKeeper{i}').Shape
 checks[f'male_{i}_keeper_seating_sweep_mm3']=max(volume(keeper.translated(V(0,0,z)).common(housing.fuse(tip))) for z in [0,.1,.25,.5,1,2,4,8,16])
 # Continuous remaining roof directly over the rounded lip: 1.1 mm nominal.
 roof=Part.makeBox(1,2,1.08,V(x-.5,y-4,11.71))
 checks[f'male_{i}_lip_roof_missing_mm3']=volume(roof.cut(keeper))
 removed=volume(old.getObject(f'MalePortKeeper{i}').Shape.cut(keeper));assert removed>1
 male.append({'port':i,'keeper_removed_material_mm3':removed,'lip_clearance_mm':p['male_keeper_lip_clearance'],'roof_checked_mm':1.08})
for name in ['LightWindow','LEDWindowSupportTaper']:
 checks[name+'_shift_error_mm3']=diff(old.getObject(name).Shape.translated(V(0,-6,0)),new.getObject(name).Shape)
assert all(v<.005 for v in checks.values()),checks
report={'revision':'v0.16','checks':checks,'female_terminal_passage_width_mm':12.8,'male_lip_relief':male,'window_shift_toward_centre_mm':6,'physical_fit_verified':False}
(r/'fit-v0.16-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
