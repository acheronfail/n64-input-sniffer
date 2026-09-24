"""Extract a complete production port-2 seat for a two-part pressure test. Units: mm."""
from pathlib import Path
import json,hashlib
import FreeCAD as A, Part, Mesh

r=Path(__file__).resolve().parent
p=json.loads((r/'parameters.json').read_text())
source=A.openDocument(str(r/'Enclosure-v1.3.FCStd'))
V=A.Vector
x=p['male_port_x'][1]
y=p['nose_y']+p['port_x'][1]**2/p['curve_radius']
body_length=p['male_body_length']
# Keep the complete collar and both posts, with 1 mm behind the posts.
y_min=y-body_length-8.5
y_max=y+4
region=Part.makeBox(27.2,y_max-y_min,p['top_z']-p['bottom_z'],V(x-13.6,y_min,p['bottom_z']))
base=source.LowerShell.Shape.common(region).removeSplitter()
keeper=source.MalePortKeeper2.Shape
body=source.MalePort2.Shape
plug=source.MaleMatingProjection2.Shape
pad=source.MalePressurePad2.Shape

def vol(shape):
 return 0.0 if shape.isNull() or not shape.Solids else shape.Volume

assert base.isValid() and len(base.Solids)==1
assert keeper.isValid() and len(keeper.Solids)==1
tab_relief=source.MaleTabRelief2.Shape
front_relief=source.MaleKeeperFrontRelief2.Shape
checks={
 'deep_cradle_obstruction_mm3':vol(source.MaleCradleDepthRelief2.Shape.common(base)),
 'fully_lowered_body_obstruction_mm3':vol(base.common(body.translated(V(0,0,-p['connector_clearance']-p['male_cradle_extra_depth'])))),
 'side_tab_insertion_obstruction_mm3':vol(tab_relief.common(base)),
 'keeper_tab_obstruction_mm3':vol(source.MaleKeeperTabRelief2.Shape.common(keeper)),
 'front_feature_obstruction_mm3':vol(front_relief.common(keeper)),
 'posts_missing_mm3':vol(source.MaleKeeperPosts2.Shape.cut(base)),
 'base_keeper_overlap_mm3':vol(base.common(keeper)),
 'base_connector_overlap_mm3':vol(base.common(body.fuse(plug))),
 'settled_body_overlap_mm3':vol(base.common(body.translated(V(0,0,-p['connector_clearance'])))),
}
# Preserve the full original collar from its rear stop through the front lip.
seat_region=Part.makeBox(27.2,body_length+4.5,29,V(x-13.6,y-body_length-1.5,-16))
checks['seat_missing_mm3']=vol(source.LowerShell.Shape.common(seat_region).cut(base))
checks['keeper_installation_obstruction_mm3']=max(vol(keeper.translated(V(0,0,z)).common(base)) for z in [0,.25,1,3,8,16])
assert all(v<.005 for v in checks.values()),checks
fixture=base.fuse(keeper)
retention={}
for label,delta in [('lift',V(0,0,.8)),('forward',V(0,.8,0)),('backward',V(0,-.8,0))]:
 overlap=vol(body.fuse(plug).translated(delta).common(fixture).cut(pad))
 assert overlap>.01,(label,overlap)
 retention[label+'_blocked_mm3']=overlap
contact=keeper.common(body.translated(V(0,0,-p['connector_clearance']-p['male_cradle_extra_depth'])) )
assert vol(contact.cut(pad))<.005
expected_contact=p['male_pressure_pad_width']*p['male_pressure_pad_length']*p['male_pressure_preload'] if p['male_pressure_pad_enabled'] else 0
assert abs(vol(contact)-expected_contact)<.005
for side in ['L','R']:
 screw=source.getObject('MaleKeeperScrew2'+side).Shape
 # Thread engagement in the printed pilot holes is intentional.
 assert vol(screw.common(keeper.fuse(body).fuse(plug)))<.005

# Embed the exact production keeper and connector reference in a small standalone model.
d=A.newDocument('SinglePortPressureTest')
parts=d.addObject('App::DocumentObjectGroup','PrintParts')
refs=d.addObject('App::DocumentObjectGroup','References')
for name,shape,group in [('SinglePortTestBase',base,parts),('MalePortKeeper2',keeper,parts),('MaleBody',body,refs),('MalePlug',plug,refs)]:
 o=d.addObject('Part::Feature',name);o.Shape=shape.copy();group.addObject(o)
 if A.GuiUp:o.ViewObject.ShapeColor=(.3,.5,.7) if group==parts else (.18,.2,.22)
meta=d.addObject('App::FeaturePython','FitTestNotes')
meta.addProperty('App::PropertyString','Instructions')
meta.Instructions='Production port 2 with two-dimple keeper. Two 2 mm x 8 mm countersunk plastic screws. Fit 4: deeper cradle retained; small central pad tier removed. Check contact at the remaining wider step and plug fit; no nominal pad preload. Physical fit not verified.'
d.recompute();d.saveAs(str(r/'Enclosure-single-port-v1.3.FCStd'))
Mesh.Mesh(base.tessellate(.08)).write(str(r/'SinglePortTestBase.stl'))
report={'revision':'v1.3','parts':2,'source_model':'Enclosure-v1.3.FCStd','source_model_sha256':hashlib.sha256((r/'Enclosure-v1.3.FCStd').read_bytes()).hexdigest(),'production_port':2,'base_dimensions_mm':[base.BoundBox.XLength,base.BoundBox.YLength,base.BoundBox.ZLength],'checks':checks,'retention':retention,'contact_at_deeper_body_seat_mm3':vol(contact),'cradle_extra_depth_mm':p['male_cradle_extra_depth'],'small_tier_enabled':p['male_pressure_pad_enabled'],'pad_extension_mm':p['male_pressure_pad_extension'] if p['male_pressure_pad_enabled'] else 0,'actual_clamp_contact_requires_physical_test':True,'physical_fit_verified':False}
(r/'single-port-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
