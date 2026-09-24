"""Check current female passages, male projection orientation and keeper clearance."""
from pathlib import Path
import sys,json
import FreeCAD as A,Part
r=Path(__file__).resolve().parent;p=json.loads((r/'parameters.json').read_text());V=A.Vector
new=A.openDocument(str(r/'Enclosure-v1.3.FCStd'))
def volume(s):return 0 if s.isNull() or not s.Solids else s.Volume
def diff(a,b):return volume(a.cut(b))+volume(b.cut(a))
checks={};male=[];pressure=[]
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
 housing=new.getObject(f'MalePort{i}').Shape
 bounds=housing.optimalBoundingBox()
 assert abs(bounds.XLength-p['male_body_diameter'])<.001
 assert abs(bounds.ZLength-p['male_body_height'])<.001
 assert abs(bounds.YLength-p['male_body_length'])<.001
 assert abs(bounds.ZMax-(p['male_body_height']-p['male_body_diameter']/2))<.001
 assert abs(tip.optimalBoundingBox().YMax-bounds.YMin-p['male_total_length'])<.001
 keeper=new.getObject(f'MalePortKeeper{i}').Shape
 for angle in [-5,5]:
  rotated=housing.copy();rotated.rotate(V(x,y,0),V(0,1,0),angle)
  # Exclude preload when checking that the D profile itself prevents roll.
  assert volume(rotated.common(new.LowerShell.Shape.fuse(keeper)).cut(new.getObject(f'MalePressurePad{i}').Shape))>.005,(i,angle,'body can roll')
 pad=new.getObject(f'MalePressurePad{i}').Shape
 pad_bounds=pad.optimalBoundingBox()
 assert abs(pad_bounds.XLength-p['male_pressure_pad_width'])<.001 and abs(pad_bounds.YLength-p['male_pressure_pad_length'])<.001
 assert abs(pad_bounds.Center.x-x)<.001 and abs(pad_bounds.Center.y-(y-p['male_body_length']/2-p['male_pressure_pad_center_backshift']))<.001
 expected_bottom=bounds.ZMax-p['connector_clearance']-p['male_pressure_pad_extension']-p['male_pressure_preload']
 assert abs(pad_bounds.ZMin-expected_bottom)<.001
 assert abs(pad_bounds.ZMax-6.8)<.001, 'Pad must print from the existing roof, without a floating island'
 if p['male_pressure_pad_enabled']:
  checks[f'male_{i}_pad_missing_mm3']=volume(pad.cut(keeper))
 else:
  # Remove the protruding tier while preserving the underlying wider step.
  removed=pad.common(Part.makeBox(30,30,5.269-pad_bounds.ZMin,V(x-15,y-25,pad_bounds.ZMin)))
  checks[f'male_{i}_small_tier_remaining_mm3']=volume(removed.common(keeper))
  for ya,length,z in [(-14,2,5.271),(-12,4.5,5.401)]:
   step=Part.makeBox(10,length,6.79-z,V(x-5,y+ya,z))
   checks[f'male_{i}_broad_step_{ya}_missing_mm3']=volume(step.cut(keeper))
 tab_relief=new.getObject(f'MaleTabRelief{i}').Shape
 front_relief=new.getObject(f'MaleKeeperFrontRelief{i}').Shape
 checks[f'male_{i}_tab_insertion_obstruction_mm3']=volume(tab_relief.common(new.LowerShell.Shape))
 checks[f'male_{i}_keeper_tab_obstruction_mm3']=volume(new.getObject(f'MaleKeeperTabRelief{i}').Shape.common(keeper))
 checks[f'male_{i}_front_feature_obstruction_mm3']=volume(front_relief.common(keeper))
 assert pad_bounds.YMax<=y-p['male_keeper_front_relief_length']-.49
 assert abs(front_relief.BoundBox.YLength-7.35)<.001
 # Test the pad against the body's new deeper seat position.
 settled=housing.translated(V(0,0,-p['connector_clearance']-p['male_cradle_extra_depth']))
 cradle=new.getObject(f'MaleCradleDepthRelief{i}').Shape
 checks[f'male_{i}_deep_cradle_obstruction_mm3']=volume(cradle.common(new.LowerShell.Shape))
 assert abs(cradle.BoundBox.ZMin-(-p['male_body_diameter']/2-p['connector_clearance']-p['male_cradle_extra_depth']))<.001
 deep_body=housing.translated(V(0,0,-p['connector_clearance']-p['male_cradle_extra_depth']))
 checks[f'male_{i}_deep_body_seat_obstruction_mm3']=volume(deep_body.common(new.LowerShell.Shape))
 assert abs(front_relief.BoundBox.XLength-p['male_keeper_front_relief_width'])<.001
 for side in [-1,1]:
  # Outer ports also have necessary local clearance around closure-nut bosses.
  length=7.2 if i in [2,3] else 3.0
  wall_x=x+11.5 if side>0 else x-13.2
  web=Part.makeBox(1.7,length,12.3,V(wall_x,y-length,.3))
  checks[f'male_{i}_{side}_front_side_wall_missing_mm3']=volume(web.cut(keeper))
 checks[f'male_{i}_deeper_body_seat_interference_mm3']=volume(settled.common(new.LowerShell.Shape))
 contact=keeper.common(settled)
 checks[f'male_{i}_contact_outside_pad_mm3']=volume(contact.cut(pad))
 contact_area=p['male_pressure_pad_width']*p['male_pressure_pad_length']
 expected_contact=contact_area*p['male_pressure_preload'] if p['male_pressure_pad_enabled'] else 0
 assert abs(volume(contact)-expected_contact)<.005
 # Installation is clear apart from the final intentional pad compression.
 checks[f'male_{i}_keeper_seating_sweep_mm3']=max(volume(keeper.translated(V(0,0,z)).common(housing.fuse(tip)).cut(pad.translated(V(0,0,z)))) for z in [0,.1,.25,.5,1,2,4,8,16])
 # The print-first gauge must contain every male post and the surrounding seat.
 gauge=new.RearAlignmentGauge.Shape
 post=new.getObject(f'MaleKeeperPosts{i}').Shape
 checks[f'male_{i}_gauge_post_missing_mm3']=volume(post.cut(gauge))
 seat_region=Part.makeBox(27.2,p['male_body_length']+4.5,29,V(x-13.6,y-p['male_body_length']-1.5,-16))
 checks[f'male_{i}_gauge_seat_missing_mm3']=volume(new.LowerShell.Shape.common(seat_region).cut(gauge))
 pressure.append({'port':i,'small_tier_enabled':p['male_pressure_pad_enabled'],'width_mm':pad_bounds.XLength,'length_mm':pad_bounds.YLength,'pad_face_z_mm':pad_bounds.ZMin if p['male_pressure_pad_enabled'] else None,'nominal_preload_at_deeper_body_seat_mm':p['male_pressure_preload'] if p['male_pressure_pad_enabled'] else 0,'contact_at_deeper_body_seat_mm3':volume(contact),'extra_cradle_depth_mm':p['male_cradle_extra_depth'],'pad_extension_mm':p['male_pressure_pad_extension'],'actual_clamp_contact_requires_physical_test':True})
 # The former square top recess is filled, except for the explicit side-tab windows.
 filled_top=Part.makeBox(12,11,1,V(x-6,y-p['male_body_length']+3,p['male_keeper_top']-1))
 checks[f'male_{i}_filled_top_missing_mm3']=volume(filled_top.cut(keeper))
 for side in [-1,1]:
  roof_x=x+7.5 if side>0 else x-10.5
  side_roof=Part.makeBox(3,8,1,V(roof_x,y-16,p['male_keeper_top']-1))
  checks[f'male_{i}_{side}_side_pocket_roof_missing_mm3']=volume(side_roof.cut(keeper))
 # Continuous remaining roof directly over the rounded lip: 1.1 mm nominal.
 roof=Part.makeBox(1,2,1.08,V(x-.5,y-4,11.71))
 checks[f'male_{i}_lip_roof_missing_mm3']=volume(roof.cut(keeper))
 male.append({'port':i,'lip_clearance_mm':p['male_keeper_lip_clearance'],'roof_checked_mm':1.08})
assert all(v<.005 for v in checks.values()),checks
# The closest paired connector tails are at the two center ports on the curved face.
gaps=[new.getObject(f'MalePort{i}').Shape.distToShape(new.getObject(f'FemalePort{i}').Shape)[0] for i in range(1,5)]
assert min(gaps)>=p['minimum_wire_gap']-.02,gaps
# Keep a slot for wires between the opposing screw towers at every port.
tower_gaps=[new.getObject(f'MaleKeeperPosts{i}').Shape.distToShape(new.getObject(f'FemaleKeeperPosts{i}').Shape)[0] for i in range(1,5)]
assert min(tower_gaps)>=p['minimum_keeper_tower_gap']-.001,tower_gaps
window_centre=new.LightWindow.Shape.BoundBox.Center
assert abs(window_centre.x)<.001
assert abs(window_centre.y-(p['rear_y']-14-p['led_window_inward_shift']-p['pcb_console_inset']))<.001
report={'revision':'v1.3','checks':checks,'pressure_pads':pressure,'female_terminal_passage_width_mm':12.8,'male_lip_relief':male,'window_shift_toward_centre_mm':p['led_window_inward_shift'],'physical_fit_verified':False,'connector_gaps_mm':gaps,'keeper_tower_gaps_mm':tower_gaps,'window_centre_y_mm':window_centre.y}
(r/'fit-v1.3-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
